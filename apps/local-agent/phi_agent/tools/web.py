"""
WebTool for browser automation using Playwright
"""
import asyncio
from typing import Any, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from phi_agent.tools.base import BaseTool


class WebTool(BaseTool):
    """Browser automation tool using Playwright"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Script registry for common operations
        self.scripts = {
            "LOGIN_AND_EXPORT_DAILY_ORDERS": self._login_and_export_daily_orders,
            "LOGIN": self._login,
            "DOWNLOAD_REPORT": self._download_report,
        }
    
    async def _initialize_browser(self):
        """Initialize browser if not already initialized"""
        if self.browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
    
    async def _cleanup(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def _login(self, url: str, username: str, password: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Login to a website"""
        await self._initialize_browser()
        await self.page.goto(url)
        
        # Fill username
        username_selector = selectors.get("username", 'input[name="username"], input[type="email"], #username')
        await self.page.fill(username_selector, username)
        
        # Fill password
        password_selector = selectors.get("password", 'input[name="password"], input[type="password"], #password')
        await self.page.fill(password_selector, password)
        
        # Click login button
        login_selector = selectors.get("login_button", 'button[type="submit"], input[type="submit"], button:has-text("Login")')
        await self.page.click(login_selector)
        
        # Wait for navigation
        await self.page.wait_for_load_state("networkidle")
        
        return {"status": "success", "url": self.page.url}
    
    async def _login_and_export_daily_orders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Login to WMS and export daily orders"""
        url = params.get("url", "https://wms.example.com")
        username = params.get("username")
        password = params.get("password")
        date = params.get("date")
        
        if not username or not password:
            raise ValueError("username and password are required")
        
        await self._initialize_browser()
        
        # Login
        login_result = await self._login(
            url,
            username,
            password,
            params.get("selectors", {})
        )
        
        # Navigate to orders page
        orders_url = params.get("orders_url", f"{url}/orders")
        await self.page.goto(orders_url)
        await self.page.wait_for_load_state("networkidle")
        
        # Set date filter if provided
        if date:
            date_selector = params.get("date_selector", 'input[name="date"], input[type="date"]')
            await self.page.fill(date_selector, date)
            await self.page.click(params.get("filter_button", 'button:has-text("Filter")'))
            await self.page.wait_for_load_state("networkidle")
        
        # Click export button
        export_selector = params.get("export_selector", 'button:has-text("Export"), a:has-text("Export")')
        async with self.page.expect_download() as download_info:
            await self.page.click(export_selector)
        download = await download_info.value
        
        # Save download
        download_path = params.get("download_path", f"/tmp/orders_{date or 'latest'}.csv")
        await download.save_as(download_path)
        
        return {
            "status": "success",
            "download_path": download_path,
            "filename": download.suggested_filename
        }
    
    async def _download_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Download a report from current page"""
        await self._initialize_browser()
        
        url = params.get("url")
        if url:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
        
        download_selector = params.get("download_selector", 'a:has-text("Download"), button:has-text("Download")')
        async with self.page.expect_download() as download_info:
            await self.page.click(download_selector)
        download = await download_info.value
        
        download_path = params.get("download_path", f"/tmp/{download.suggested_filename}")
        await download.save_as(download_path)
        
        return {
            "status": "success",
            "download_path": download_path,
            "filename": download.suggested_filename
        }
    
    async def execute(self, payload: Dict[str, Any]) -> Any:
        """Execute web automation task"""
        action = payload.get("action", "goto")
        
        try:
            await self._initialize_browser()
            
            if action == "run_script":
                # Run a named script
                script_name = payload.get("script")
                if script_name not in self.scripts:
                    raise ValueError(f"Unknown script: {script_name}")
                
                script_func = self.scripts[script_name]
                params = payload.get("params", {})
                return await script_func(params)
            
            elif action == "goto":
                url = payload.get("url")
                if not url:
                    raise ValueError("url is required for goto action")
                await self.page.goto(url)
                await self.page.wait_for_load_state("networkidle")
                return {"status": "success", "url": self.page.url}
            
            elif action == "click":
                selector = payload.get("selector")
                if not selector:
                    raise ValueError("selector is required for click action")
                await self.page.click(selector)
                await self.page.wait_for_load_state("networkidle")
                return {"status": "success"}
            
            elif action == "fill":
                selector = payload.get("selector")
                value = payload.get("value")
                if not selector or value is None:
                    raise ValueError("selector and value are required for fill action")
                await self.page.fill(selector, str(value))
                return {"status": "success"}
            
            elif action == "login":
                return await self._login(
                    payload.get("url"),
                    payload.get("username"),
                    payload.get("password"),
                    payload.get("selectors", {})
                )
            
            elif action == "download":
                return await self._download_report(payload)
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        
        finally:
            # Don't cleanup on every action - keep browser alive for session
            # Only cleanup if explicitly requested
            if payload.get("close_browser", False):
                await self._cleanup()
    
    @property
    def name(self) -> str:
        return "web"


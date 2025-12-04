"""
Communication tools for Email and Slack
"""
import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from app.config import settings
import os


class EmailTool:
    """Email sending tool"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM", self.smtp_user)
    
    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP credentials not configured")
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = ", ".join(to)
        
        # Add text and HTML parts
        if text_body:
            text_part = MIMEText(text_body, "plain")
            msg.attach(text_part)
        
        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)
        
        # Send email
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return {
                "status": "success",
                "to": to,
                "subject": subject
            }
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")


class SlackTool:
    """Slack messaging tool using webhooks"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    async def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send message to Slack via webhook"""
        if not self.webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL not configured")
        
        payload = {
            "text": text
        }
        
        if channel:
            payload["channel"] = channel
        if username:
            payload["username"] = username
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload)
            response.raise_for_status()
        
        return {
            "status": "success",
            "message": text,
            "channel": channel
        }


# Global instances
email_tool = EmailTool()
slack_tool = SlackTool()


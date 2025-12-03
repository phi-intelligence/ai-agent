from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Base class for all local agent tools"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Any:
        """Execute the tool with given payload"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass



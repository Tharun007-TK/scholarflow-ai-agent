from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel

class Tool(ABC):
    """Base class for ADK tools."""
    def __init__(self, name: str, description: str, args_schema: Type[BaseModel] = None):
        self.name = name
        self.description = description
        self.args_schema = args_schema

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute the tool."""
        pass

    def validate_args(self, **kwargs):
        if self.args_schema:
            return self.args_schema(**kwargs)
        return kwargs

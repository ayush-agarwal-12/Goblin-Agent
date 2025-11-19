from datetime import datetime
from typing import Any,Optional
from dataclasses import dataclass

@dataclass 
class ToolResult:
    """Simple result format for all tool"""
    success : bool
    error : Optional[str] = None
    data : Optional[Any] = None
    timestamp : Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

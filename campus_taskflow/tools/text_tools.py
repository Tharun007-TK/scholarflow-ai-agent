from dateutil import parser
from typing import Optional
from ..adk.tools import Tool
from pydantic import BaseModel, Field

class DateParserArgs(BaseModel):
    date_string: str = Field(..., description="The date string to parse")

class DateParserTool(Tool):
    def __init__(self):
        super().__init__(
            name="date_parser",
            description="Parses a date string into ISO 8601 format.",
            args_schema=DateParserArgs
        )

    def run(self, date_string: str) -> Optional[str]:
        try:
            dt = parser.parse(date_string)
            return dt.isoformat()
        except (ValueError, TypeError):
            return None

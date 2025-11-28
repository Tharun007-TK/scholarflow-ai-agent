from typing import Any, Dict, List
from ..adk.core import Agent, State
from ..tools.text_tools import DateParserTool
import re

class TaskParsingAgent(Agent):
    def __init__(self):
        super().__init__(
            name="TaskParsingAgent",
            description="Parses tasks and deadlines from extracted text.",
            tools=[DateParserTool()]
        )

    def run(self, state: State, input_data: Any) -> List[Dict[str, Any]]:
        # input_data is the result from PDFExtractionAgent
        extracted_content = input_data
        full_text = extracted_content.get("full_text", "")
        
        # In a real implementation, this would call an LLM
        # For this runnable version without an API key, we'll use a heuristic/regex approach
        # or a mock LLM call if we had one.
        # I will implement a simple heuristic parser for demonstration purposes
        # to ensure it runs without external dependencies if the user hasn't provided keys.
        
        tasks = []
        lines = full_text.split('\n')
        for line in lines:
            if "assignment" in line.lower() or "due" in line.lower() or "exam" in line.lower():
                # Simple extraction logic
                tasks.append({
                    "description": line.strip(),
                    "source_page": "unknown", # simplified
                    "deadline": None # would need LLM to extract specific date context
                })
        
        state.set("parsed_tasks", tasks)
        return tasks

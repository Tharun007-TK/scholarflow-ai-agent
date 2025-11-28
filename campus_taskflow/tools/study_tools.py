from typing import List, Dict, Any
from ..adk.tools import Tool
from pydantic import BaseModel, Field

class FlashcardFormatterArgs(BaseModel):
    qa_pairs: List[Dict[str, str]] = Field(..., description="List of Q/A pairs")

class FlashcardFormatterTool(Tool):
    def __init__(self):
        super().__init__(
            name="flashcard_formatter",
            description="Formats Q/A pairs into a standard flashcard schema.",
            args_schema=FlashcardFormatterArgs
        )

    def run(self, qa_pairs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        formatted = []
        for pair in qa_pairs:
            formatted.append({
                "front": pair.get("question", "").strip(),
                "back": pair.get("answer", "").strip(),
                "tags": ["academic"]
            })
        return formatted

class StudyPlanFormatterTool(Tool):
    def __init__(self):
        super().__init__(
            name="study_plan_formatter",
            description="Formats a schedule into a readable study plan.",
            args_schema=None
        )

    def run(self, schedule: List[Dict[str, Any]]) -> str:
        formatted_plan = "Study Plan:\n"
        for item in schedule:
            formatted_plan += f"- {item['date']}: {item['task']} ({item['duration_minutes']} mins)\n"
        return formatted_plan

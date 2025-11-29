from typing import Any, Dict, List
from ..adk.core import Agent, State
from ..adk.skills import LLMSkill
import json
import re

class TaskParsingAgent(Agent):
    def __init__(self):
        super().__init__(
            name="TaskParsingAgent",
            description="Parses tasks and deadlines from extracted text using LLM.",
            tools=[]
        )
        self.llm = LLMSkill()

    def run(self, state: State, input_data: Any) -> List[Dict[str, Any]]:
        # input_data is the result from PDFExtractionAgent
        extracted_content = input_data
        full_text = extracted_content.get("full_text", "")
        
        if self.llm.model:
            return self.extract_tasks_with_llm(full_text, state)
        else:
            return self.extract_tasks_heuristic(full_text, state)

    def extract_tasks_with_llm(self, text: str, state: State) -> List[Dict[str, Any]]:
        prompt = f"""
        You are an expert academic planner. Extract all actionable tasks, assignments, exams, and study goals from the following text.
        
        Return the output strictly as a JSON list of objects. Each object must have:
        - "description": The task description.
        - "deadline": The due date (YYYY-MM-DD) if found, else null.
        - "priority": "High", "Medium", or "Low" based on importance/urgency.
        - "estimated_hours": Estimated hours to complete (integer).
        
        Do not include markdown formatting like ```json.
        
        Text:
        {text[:15000]}
        """
        
        try:
            response = self.llm.execute(prompt)
            # Clean up response if it contains markdown
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            tasks = json.loads(cleaned_response)
            state.set("parsed_tasks", tasks)
            return tasks
        except Exception as e:
            print(f"LLM Extraction failed: {e}")
            return self.extract_tasks_heuristic(text, state)

    def extract_tasks_heuristic(self, text: str, state: State) -> List[Dict[str, Any]]:
        tasks = []
        lines = text.split('\n')
        for line in lines:
            if "assignment" in line.lower() or "due" in line.lower() or "exam" in line.lower():
                tasks.append({
                    "description": line.strip(),
                    "deadline": None,
                    "priority": "Medium",
                    "estimated_hours": 2
                })
        
        state.set("parsed_tasks", tasks)
        return tasks

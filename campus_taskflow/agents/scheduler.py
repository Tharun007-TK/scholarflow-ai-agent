from typing import Any, Dict, List
from ..adk.core import Agent, State
from ..adk.skills import LLMSkill
from datetime import datetime, timedelta
import json

class SchedulerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="SchedulerAgent",
            description="Creates a day-wise study schedule using LLM.",
            tools=[]
        )
        self.llm = LLMSkill()

    def run(self, state: State, input_data: Any) -> List[Dict[str, Any]]:
        tasks = state.get("parsed_tasks", [])
        
        if self.llm.model:
            return self.generate_schedule_with_llm(tasks, state)
        else:
            return self.generate_schedule_heuristic(tasks, state)

    def generate_schedule_with_llm(self, tasks: List[Dict], state: State) -> List[Dict[str, Any]]:
        start_date = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
        You are an expert academic scheduler. Create a realistic day-wise study schedule for the next 7 days based on the following tasks.
        
        Tasks:
        {json.dumps(tasks, indent=2)}
        
        Start Date: {start_date}
        
        Rules:
        - Distribute tasks evenly.
        - Prioritize High priority tasks.
        - Break down large tasks (high estimated_hours) across multiple days.
        - Include "Review" sessions.
        
        Return the output strictly as a JSON list of objects. Each object must have:
        - "date": YYYY-MM-DD
        - "task": Description of the study activity
        - "duration_minutes": Duration (integer)
        
        Do not include markdown formatting like ```json.
        """
        
        try:
            response = self.llm.execute(prompt)
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            schedule = json.loads(cleaned_response)
            state.set("schedule", schedule)
            return schedule
        except Exception as e:
            print(f"LLM Scheduling failed: {e}")
            return self.generate_schedule_heuristic(tasks, state)

    def generate_schedule_heuristic(self, tasks: List[Dict], state: State) -> List[Dict[str, Any]]:
        # Simple scheduling logic: distribute tasks over the next 5 days
        schedule = []
        start_date = datetime.now()
        
        for i, task in enumerate(tasks):
            day_offset = i % 5
            date = start_date + timedelta(days=day_offset)
            
            schedule.append({
                "date": date.strftime("%Y-%m-%d"),
                "task": task.get("description", "Study"),
                "duration_minutes": 60
            })
            
        # If no tasks, add some default study blocks
        if not schedule:
             for i in range(3):
                date = start_date + timedelta(days=i)
                schedule.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "task": "Review extracted material",
                    "duration_minutes": 45
                })

        state.set("schedule", schedule)
        return schedule

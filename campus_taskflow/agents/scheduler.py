from typing import Any, Dict, List
from ..adk.core import Agent, State
from datetime import datetime, timedelta

class SchedulerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="SchedulerAgent",
            description="Creates a day-wise study schedule.",
            tools=[]
        )

    def run(self, state: State, input_data: Any) -> List[Dict[str, Any]]:
        tasks = state.get("parsed_tasks", [])
        
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

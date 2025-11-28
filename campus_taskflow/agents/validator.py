from typing import Any, Dict, List
from ..adk.core import Agent, State

class ValidationAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ValidationAgent",
            description="Validates the outputs of the pipeline.",
            tools=[]
        )

    def run(self, state: State, input_data: Any) -> Dict[str, Any]:
        # Validate all artifacts in state
        validation_report = {
            "tasks_valid": False,
            "flashcards_valid": False,
            "schedule_valid": False,
            "errors": []
        }
        
        tasks = state.get("parsed_tasks")
        if tasks and isinstance(tasks, list):
            validation_report["tasks_valid"] = True
        else:
            validation_report["errors"].append("No tasks parsed or invalid format.")

        flashcards = state.get("flashcards")
        if flashcards and isinstance(flashcards, list):
             validation_report["flashcards_valid"] = True
        else:
             validation_report["errors"].append("No flashcards generated.")

        schedule = state.get("schedule")
        if schedule and isinstance(schedule, list):
             validation_report["schedule_valid"] = True
        else:
             validation_report["errors"].append("No schedule generated.")

        state.set("validation_report", validation_report)
        return validation_report

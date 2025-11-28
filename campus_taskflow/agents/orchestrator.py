from typing import Any, List
from ..adk.core import SequentialAgent, State, Agent
from .pdf_extractor import PDFExtractionAgent
from .task_parser import TaskParsingAgent
from .summarizer import SummarizationAgent
from .flashcard import FlashcardAgent
from .scheduler import SchedulerAgent
from .validator import ValidationAgent

class OrchestratorAgent(SequentialAgent):
    """
    Orchestrates the entire Campus TaskFlow pipeline.
    It executes the following agents in sequence:
    1. PDFExtractionAgent
    2. TaskParsingAgent
    3. SummarizationAgent
    4. FlashcardAgent
    5. SchedulerAgent
    6. ValidationAgent
    """
    def __init__(self, name: str = "Orchestrator"):
        # Initialize sub-agents
        # Note: These will be initialized with their specific tools and configurations
        agents = [
            PDFExtractionAgent(),
            TaskParsingAgent(),
            SummarizationAgent(),
            FlashcardAgent(),
            SchedulerAgent(),
            ValidationAgent()
        ]
        
        super().__init__(
            name=name,
            description="Orchestrates the academic workflow automation pipeline.",
            agents=agents
        )

    def run(self, state: State, input_data: Any) -> Any:
        # The input_data is expected to be the path to the PDF file
        state.set("pdf_path", input_data)
        return super().run(state, input_data)

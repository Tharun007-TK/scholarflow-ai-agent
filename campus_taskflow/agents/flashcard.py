from typing import Any, List, Dict
from ..adk.core import Agent, State
from ..adk.skills import LLMSkill
from ..tools.study_tools import FlashcardFormatterTool

class FlashcardAgent(Agent):
    def __init__(self):
        super().__init__(
            name="FlashcardAgent",
            description="Generates study flashcards.",
            tools=[FlashcardFormatterTool()]
        )
        self.llm_skill = LLMSkill()

    def run(self, state: State, input_data: Any) -> List[Dict[str, str]]:
        extracted_content = state.get("extracted_content", {})
        full_text = extracted_content.get("full_text", "")
        
        # Generate raw Q/A using LLM Skill
        # In a real app, we'd parse the LLM output. 
        # Here we simulate the output structure.
        raw_qa = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is 2+2?", "answer": "4"}
        ]
        
        formatter = self.tools[0]
        flashcards = formatter.run(qa_pairs=raw_qa)
        
        state.set("flashcards", flashcards)
        return flashcards

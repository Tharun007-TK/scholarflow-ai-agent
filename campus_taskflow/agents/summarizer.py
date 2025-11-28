from typing import Any, Dict
from ..adk.core import Agent, State
from ..adk.skills import LLMSkill

class SummarizationAgent(Agent):
    def __init__(self):
        super().__init__(
            name="SummarizationAgent",
            description="Summarizes academic content.",
            tools=[] # Uses Skill instead of Tool for LLM
        )
        self.llm_skill = LLMSkill()

    def run(self, state: State, input_data: Any) -> Dict[str, Any]:
        # input_data is the list of tasks from TaskParsingAgent, 
        # but we actually need the extracted text from state
        extracted_content = state.get("extracted_content", {})
        full_text = extracted_content.get("full_text", "")
        
        summary = self.llm_skill.summarize(full_text)
        
        result = {
            "summary": summary,
            "key_points": ["Point 1", "Point 2"] # Mocked for now
        }
        state.set("summary", result)
        return result

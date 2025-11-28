from abc import ABC, abstractmethod
from typing import Any, List

class Skill(ABC):
    """Base class for agent skills."""
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        pass

import google.generativeai as genai
import os

class LLMSkill(Skill):
    """Skill for interacting with Google Gemini models."""
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.model_name = model_name
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    def execute(self, prompt: str) -> str:
        if not self.model:
            # Fallback if no key provided yet (e.g. before UI input)
            return "[Error: GOOGLE_API_KEY not set. Please configure it in the UI.]"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[Error calling Gemini API: {str(e)}]"

    def summarize(self, text: str) -> str:
        prompt = f"Please provide a concise summary and key learning points for the following academic text:\n\n{text[:10000]}" # Truncate for safety
        return self.execute(prompt)

    def generate_flashcards(self, text: str) -> List[str]:
        prompt = f"""
        Generate 5-10 high-quality flashcards from the following text. 
        Format the output strictly as a JSON list of objects with 'question' and 'answer' keys.
        Do not include markdown formatting like ```json.
        
        Text:
        {text[:10000]}
        """
        # Note: In a real app we'd use structured output or json mode if available, 
        # or parse the text more robustly.
        return self.execute(prompt)

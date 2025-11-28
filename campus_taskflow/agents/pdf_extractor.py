from typing import Any, Dict
from ..adk.core import Agent, State
from ..tools.pdf_tools import PDFReaderTool, OCRTool

class PDFExtractionAgent(Agent):
    def __init__(self):
        super().__init__(
            name="PDFExtractionAgent",
            description="Extracts text and structure from PDFs.",
            tools=[PDFReaderTool(), OCRTool()]
        )

    def run(self, state: State, input_data: Any) -> Dict[str, Any]:
        # input_data is expected to be the pdf_path
        pdf_path = input_data
        self.logger.info(f"Extracting content from {pdf_path}")
        
        pdf_tool = self.tools[0] # PDFReaderTool
        result = pdf_tool.run(file_path=pdf_path)
        
        # Store extracted content in state/memory
        state.set("extracted_content", result)
        
        # Index content for RAG
        try:
            from ..tools.search_tools import EmbeddingSearchTool
            rag_tool = EmbeddingSearchTool()
            rag_tool.index_document(result["full_text"], {"source": pdf_path})
        except Exception as e:
            self.logger.warning(f"Failed to index document for RAG: {e}")
            # Do not fail the pipeline, just log the error
            state.set("rag_error", str(e))
        
        return result

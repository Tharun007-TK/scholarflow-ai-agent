import fitz  # pymupdf
import pytesseract
from PIL import Image
import io
from typing import Dict, Any, List
from ..adk.tools import Tool
from pydantic import BaseModel, Field

class PDFReaderArgs(BaseModel):
    file_path: str = Field(..., description="Path to the PDF file")

class PDFReaderTool(Tool):
    def __init__(self):
        super().__init__(
            name="pdf_reader",
            description="Extracts text and metadata from a PDF file.",
            args_schema=PDFReaderArgs
        )

    def run(self, file_path: str) -> Dict[str, Any]:
        doc = fitz.open(file_path)
        pages = []
        full_text = ""
        
        for i, page in enumerate(doc):
            text = page.get_text()
            # If text is empty, it might be a scanned page
            is_scanned = len(text.strip()) < 10
            
            pages.append({
                "page_number": i + 1,
                "text": text,
                "is_scanned": is_scanned
            })
            full_text += text + "\n"
            
        return {
            "metadata": doc.metadata,
            "pages": pages,
            "full_text": full_text,
            "page_count": len(pages)
        }

class OCRArgs(BaseModel):
    image_data: bytes = Field(..., description="Raw bytes of the image")

class OCRTool(Tool):
    def __init__(self):
        super().__init__(
            name="ocr_tool",
            description="Performs OCR on an image.",
            args_schema=OCRArgs
        )

    def run(self, image_data: bytes) -> str:
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return text

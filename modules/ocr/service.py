"""OCR service for extracting text from PDF and image documents using pymupdf."""

import io
from typing import Union
import fitz  # pymupdf


class OCRService:
    """Service for optical character recognition using PyMuPDF."""

    @staticmethod
    def extract_text_from_file(file_content: Union[bytes, io.BytesIO]) -> str:
        """
        Extract text from a PDF file using PyMuPDF.

        Args:
            file_content: The file content as bytes or BytesIO object.

        Returns:
            Extracted text from the document.

        Raises:
            ValueError: If the file cannot be processed.
        """
        try:
            # Convert to BytesIO if bytes
            if isinstance(file_content, bytes):
                file_content = io.BytesIO(file_content)

            # Open document with PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")

            extracted_text = ""

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                extracted_text += text

            doc.close()
            return extracted_text

        except Exception as e:
            raise ValueError(f"Error extracting text from file: {str(e)}")

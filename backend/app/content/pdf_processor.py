import io
import uuid
from typing import Dict, List, Tuple, Any

import fitz  # PyMuPDF
from fastapi import UploadFile

from ..models import Textbook, TextbookCreate
from ..models.database_utils import get_db
from ..services import PineconeClient, StorageClient


class PDFProcessor:
    """PDF processor for text extraction and chunking."""

    @staticmethod
    async def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF."""
        # Open PDF from memory
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        
        # Extract text from each page
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
        
        return text

    @staticmethod
    async def process_pdf(
        file: UploadFile, textbook_data: TextbookCreate, user_id: str
    ) -> Tuple[Textbook, List[str]]:
        """Process PDF file."""
        # Read file content
        file_content = await file.read()
        
        # Upload file to storage
        file_path, file_url = await StorageClient.upload_textbook(
            file_content, file.filename, user_id
        )
        
        # Extract text from PDF
        text = await PDFProcessor.extract_text_from_pdf(file_content)
        
        # Create textbook record
        textbook_id = str(uuid.uuid4())
        textbook = Textbook(
            id=textbook_id,
            title=textbook_data.title,
            author=textbook_data.author,
            description=textbook_data.description,
            file_path=file_path,
            created_by=user_id,
            indexed=False,
        )
        
        # Chunk text and create embeddings
        chunks = await PineconeClient.chunk_text(text)
        
        # Upsert chunks to Pinecone
        metadata = {
            "id": textbook_id,
            "title": textbook_data.title,
            "author": textbook_data.author or "",
        }
        chunk_ids = await PineconeClient.upsert_chunks(
            chunks, metadata, namespace="textbooks"
        )
        
        # Mark textbook as indexed
        textbook.indexed = True
        
        return textbook, chunk_ids

    @staticmethod
    async def search_textbook_content(
        textbook_id: str, query: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search textbook content."""
        # Search in Pinecone
        results = await PineconeClient.search(
            query, namespace="textbooks", top_k=top_k
        )
        
        # Filter results by textbook ID
        filtered_results = [
            result for result in results if result["metadata"]["id"] == textbook_id
        ]
        
        return filtered_results 
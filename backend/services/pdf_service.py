"""PDF processing service for document ingestion and Q&A."""
from typing import List, Dict, Any, Optional, Tuple
import os
from pathlib import Path
import pymupdf
from services.embedding_service import embedding_service
from services.vector_store import vector_store


class PDFService:
    """Service for PDF processing and document ingestion."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize PDF service.
        
        Args:
            chunk_size: Approximate size of text chunks
            chunk_overlap: Overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text or None if error
        """
        try:
            doc = pymupdf.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.get_text()
            
            doc.close()
            return text
        
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return None
    
    def chunk_text(self, text: str) -> List[Tuple[str, int]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
        
        Returns:
            List of (chunk_text, page_number) tuples
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return [(chunk, 0) for chunk in chunks]  # page number is simplified
    
    def process_pdf(
        self,
        file_path: str,
        user_id: str,
        document_name: str = "Uploaded PDF"
    ) -> Optional[Dict[str, Any]]:
        """
        Process a PDF file and store in vector database.
        
        Args:
            file_path: Path to PDF file
            user_id: User ID for memory isolation
            document_name: Name/title of document
        
        Returns:
            Processing results with summary
        """
        try:
            # Extract text
            text = self.extract_text_from_pdf(file_path)
            if not text:
                return {"error": "Could not extract text from PDF"}
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            # Store in vector DB
            stored_ids = []
            for chunk_text, page_num in chunks:
                memory_id = vector_store.add_memory(
                    user_id=user_id,
                    text=chunk_text,
                    memory_type="document",
                    metadata={
                        "document_name": document_name,
                        "page_number": page_num,
                        "source": "pdf",
                    }
                )
                if memory_id:
                    stored_ids.append(memory_id)
            
            # Generate summary (first few chunks)
            summary_text = " ".join([c[0] for c in chunks[:3]])[:500]
            
            return {
                "success": True,
                "document_name": document_name,
                "chunks_created": len(chunks),
                "chunks_stored": len(stored_ids),
                "text_length": len(text),
                "summary": summary_text + "...",
            }
        
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return {"error": str(e)}
    
    def get_page_count(self, file_path: str) -> Optional[int]:
        """Get number of pages in PDF."""
        try:
            doc = pymupdf.open(file_path)
            count = len(doc)
            doc.close()
            return count
        except:
            return None


# Global PDF service instance
pdf_service = PDFService()

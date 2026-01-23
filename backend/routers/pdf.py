"""PDF API routes for document processing."""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
import os
import tempfile
from services.pdf_service import pdf_service
from utils.config import config

router = APIRouter()


@router.post("/pdf/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    document_name: str = Form("Uploaded PDF"),
):
    """
    Upload and process a PDF file.
    
    Args:
        file: PDF file to process
        user_id: User ID
        document_name: Name for the document
    
    Returns:
        Processing results
    """
    try:
        # Check module is enabled
        if not config.is_module_enabled("pdf"):
            raise HTTPException(
                status_code=403,
                detail="PDF module is currently disabled."
            )
        
        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="File must be a PDF"
            )
        
        # Validate file size (max 50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="PDF file too large (max 50MB)"
            )
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Process PDF
            result = pdf_service.process_pdf(
                file_path=tmp_path,
                user_id=user_id,
                document_name=document_name
            )
            
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            
            # Update stats
            config.USAGE_STATS['features_used']['pdf'] += 1
            
            return result
        
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in PDF processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/info")
async def get_pdf_info():
    """Get PDF processing information."""
    return {
        "max_file_size": "50MB",
        "supported_formats": ["application/pdf"],
        "features": [
            "Text extraction",
            "Semantic chunking",
            "Vector storage for RAG",
            "Q&A support",
        ]
    }

"""OCR API routes for image text extraction."""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional
import os
import tempfile
from services.ocr_service import ocr_service
from utils.config import config

router = APIRouter()


@router.post("/ocr")
async def process_ocr(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    language: str = Form("eng"),
):
    """
    Extract text from an image using OCR.
    
    Args:
        file: Image file to process
        user_id: User ID
        language: Language code (eng, hin, asm)
    
    Returns:
        Extracted text and metadata
    """
    try:
        # Check if OCR is available
        if not ocr_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="OCR service is not available. Please ensure Tesseract is installed."
            )
        
        # Check module is enabled
        if not config.is_module_enabled("ocr"):
            raise HTTPException(
                status_code=403,
                detail="OCR module is currently disabled."
            )
        
        # Validate file type
        allowed_types = {"image/jpeg", "image/png", "image/tiff", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not supported. Allowed: {allowed_types}"
            )
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Extract text
            text = ocr_service.extract_text(tmp_path, language=language)
            
            if not text:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from image"
                )
            
            # Update stats
            config.USAGE_STATS['features_used']['ocr'] += 1
            
            return {
                "success": True,
                "text": text,
                "language": language,
                "char_count": len(text),
                "word_count": len(text.split()),
            }
        
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in OCR processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ocr/languages")
async def get_supported_languages():
    """Get list of supported OCR languages."""
    return {
        "languages": ocr_service.get_supported_languages(),
        "description": {
            "eng": "English",
            "hin": "Hindi",
            "asm": "Assamese",
        }
    }

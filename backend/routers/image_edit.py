"""Image editing API routes."""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional, Tuple
import os
import tempfile
import base64
from services.image_edit_service import image_edit_service
from utils.config import config

router = APIRouter()


@router.post("/image/crop")
async def crop_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    x: int = Form(0),
    y: int = Form(0),
    width: int = Form(100),
    height: int = Form(100),
):
    """Crop an image."""
    try:
        if not config.is_module_enabled("image_editing"):
            raise HTTPException(status_code=403, detail="Image editing module is disabled.")
        
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            cropped = image_edit_service.crop(tmp_path, x, y, width, height)
            
            if not cropped:
                raise HTTPException(status_code=400, detail="Failed to crop image")
            
            config.USAGE_STATS['features_used']['image_editing'] += 1
            
            return {
                "success": True,
                "image": base64.b64encode(cropped).decode(),
                "format": "base64",
                "operation": "crop",
            }
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/enhance")
async def enhance_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    operation: str = Form("brightness"),
    factor: float = Form(1.2),
):
    """Enhance image brightness, contrast, or sharpness."""
    try:
        if not config.is_module_enabled("image_editing"):
            raise HTTPException(status_code=403, detail="Image editing module is disabled.")
        
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            if operation == "brightness":
                enhanced = image_edit_service.enhance_brightness(tmp_path, factor)
            elif operation == "contrast":
                enhanced = image_edit_service.enhance_contrast(tmp_path, factor)
            elif operation == "sharpness":
                enhanced = image_edit_service.enhance_sharpness(tmp_path, factor)
            else:
                raise HTTPException(status_code=400, detail="Unknown operation")
            
            if not enhanced:
                raise HTTPException(status_code=400, detail="Failed to enhance image")
            
            config.USAGE_STATS['features_used']['image_editing'] += 1
            
            return {
                "success": True,
                "image": base64.b64encode(enhanced).decode(),
                "format": "base64",
                "operation": operation,
                "factor": factor,
            }
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/annotate")
async def annotate_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    text: str = Form(...),
    x: int = Form(10),
    y: int = Form(10),
):
    """Add text annotation to image."""
    try:
        if not config.is_module_enabled("image_editing"):
            raise HTTPException(status_code=403, detail="Image editing module is disabled.")
        
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            annotated = image_edit_service.annotate_text(tmp_path, text, x, y)
            
            if not annotated:
                raise HTTPException(status_code=400, detail="Failed to annotate image")
            
            config.USAGE_STATS['features_used']['image_editing'] += 1
            
            return {
                "success": True,
                "image": base64.b64encode(annotated).decode(),
                "format": "base64",
                "operation": "annotate",
                "text": text,
            }
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/info")
async def get_image_operations():
    """Get available image operations."""
    return {
        "operations": [
            "crop",
            "resize",
            "enhance (brightness, contrast, sharpness)",
            "annotate",
            "grayscale",
        ],
        "supported_formats": ["image/jpeg", "image/png", "image/webp"],
    }

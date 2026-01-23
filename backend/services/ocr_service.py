"""OCR service for image text extraction."""
from typing import Optional, Dict, Any
import pytesseract
from PIL import Image
import io
import os


class OCRService:
    """Service for optical character recognition."""
    
    def __init__(self):
        """Initialize OCR service."""
        # Check if Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
            self.available = True
        except Exception:
            self.available = False
            print("Warning: Tesseract OCR not available. Install with: apt-get install tesseract-ocr")
    
    def extract_text(
        self,
        image_path: str,
        language: str = "eng"
    ) -> Optional[str]:
        """
        Extract text from image file.
        
        Args:
            image_path: Path to image file
            language: Language code for Tesseract (eng, hin, asm for Assamese)
        
        Returns:
            Extracted text or None
        """
        if not self.available:
            return None
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Extract text with language support
            text = pytesseract.image_to_string(image, lang=language)
            
            return text.strip()
        
        except Exception as e:
            print(f"Error extracting OCR text: {str(e)}")
            return None
    
    def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        language: str = "eng"
    ) -> Optional[str]:
        """
        Extract text from image bytes.
        
        Args:
            image_bytes: Image file as bytes
            language: Language code
        
        Returns:
            Extracted text
        """
        if not self.available:
            return None
        
        try:
            # Load from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            return text.strip()
        
        except Exception as e:
            print(f"Error extracting OCR text from bytes: {str(e)}")
            return None
    
    def extract_text_with_boxes(
        self,
        image_path: str,
        language: str = "eng"
    ) -> Optional[Dict[str, Any]]:
        """
        Extract text with bounding box information.
        
        Args:
            image_path: Path to image
            language: Language code
        
        Returns:
            Dictionary with text and box data
        """
        if not self.available:
            return None
        
        try:
            image = Image.open(image_path)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Get data with bounding boxes
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            return {
                "text": text.strip(),
                "boxes": data,
                "confidence": {
                    "mean": sum(int(c) for c in data['conf'] if int(c) > 0) / max(len([c for c in data['conf'] if int(c) > 0]), 1),
                }
            }
        
        except Exception as e:
            print(f"Error extracting OCR data with boxes: {str(e)}")
            return None
    
    def detect_language(self, image_path: str) -> Optional[str]:
        """
        Try to detect language in image.
        Returns best guess for language code.
        """
        if not self.available:
            return "eng"
        
        try:
            image = Image.open(image_path)
            # Tesseract can output language info, but this is simplified
            # In production, use proper language detection
            return "eng"  # Default
        
        except:
            return "eng"
    
    def is_available(self) -> bool:
        """Check if OCR is available."""
        return self.available
    
    def get_supported_languages(self) -> list:
        """Get list of supported language codes."""
        return [
            "eng",    # English
            "hin",    # Hindi
            "asm",    # Assamese
        ]


# Global OCR service instance
ocr_service = OCRService()

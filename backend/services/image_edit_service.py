"""Image editing service for basic image manipulations."""
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import io
import os


class ImageEditingService:
    """Service for basic image editing operations."""
    
    def __init__(self, max_image_size: int = 10 * 1024 * 1024):  # 10MB max
        """
        Initialize image editing service.
        
        Args:
            max_image_size: Maximum image file size in bytes
        """
        self.max_image_size = max_image_size
    
    def crop(
        self,
        image_path: str,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> Optional[bytes]:
        """
        Crop an image.
        
        Args:
            image_path: Path to image
            x, y: Top-left coordinates
            width, height: Crop dimensions
        
        Returns:
            Cropped image as bytes
        """
        try:
            image = Image.open(image_path)
            
            # Ensure coordinates are within bounds
            box = (x, y, min(x + width, image.width), min(y + height, image.height))
            cropped = image.crop(box)
            
            # Save to bytes
            output = io.BytesIO()
            cropped.save(output, format='PNG')
            output.seek(0)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"Error cropping image: {str(e)}")
            return None
    
    def resize(
        self,
        image_path: str,
        width: int,
        height: int,
        maintain_aspect: bool = True
    ) -> Optional[bytes]:
        """
        Resize an image.
        
        Args:
            image_path: Path to image
            width, height: New dimensions
            maintain_aspect: Keep aspect ratio
        
        Returns:
            Resized image as bytes
        """
        try:
            image = Image.open(image_path)
            
            if maintain_aspect:
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='PNG')
            output.seek(0)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return None
    
    def enhance_brightness(
        self,
        image_path: str,
        factor: float
    ) -> Optional[bytes]:
        """
        Enhance image brightness.
        
        Args:
            image_path: Path to image
            factor: Brightness factor (1.0 = no change, <1 = darker, >1 = brighter)
        
        Returns:
            Enhanced image as bytes
        """
        try:
            image = Image.open(image_path)
            enhancer = ImageEnhance.Brightness(image)
            enhanced = enhancer.enhance(factor)
            
            output = io.BytesIO()
            enhanced.save(output, format='PNG')
            output.seek(0)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"Error enhancing brightness: {str(e)}")
            return None
    
    def enhance_contrast(
        self,
        image_path: str,
        factor: float
    ) -> Optional[bytes]:
        """
        Enhance image contrast.
        
        Args:
            image_path: Path to image
            factor: Contrast factor (1.0 = no change)
        
        Returns:
            Enhanced image as bytes
        """
        try:
            image = Image.open(image_path)
            enhancer = ImageEnhance.Contrast(image)
            enhanced = enhancer.enhance(factor)
            
            output = io.BytesIO()
            enhanced.save(output, format='PNG')
            output.seek(0)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"Error enhancing contrast: {str(e)}")
            return None
    
    def enhance_sharpness(
        self,
        image_path: str,
        factor: float
    ) -> Optional[bytes]:
        """
        Enhance image sharpness.
        
        Args:
            image_path: Path to image
            factor: Sharpness factor
        
        Returns:
            Enhanced image as bytes
        """
        try:
            image = Image.open(image_path)
            enhancer = ImageEnhance.Sharpness(image)
            enhanced = enhancer.enhance(factor)
            
            output = io.BytesIO()
            enhanced.save(output, format='PNG')
            output.seek(0)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"Error enhancing sharpness: {str(e)}")
            return None
    
    def annotate_text(
        self,
        image_path: str,
        text: str,
        x: int,
        y: int,
        text_color: Tuple[int, int, int] = (255, 0, 0)
    ) -> Optional[bytes]:
        """
        Add text annotation to image.
        
        Args:
            image_path: Path to image
            text: Text to add
            x, y: Position coordinates
            text_color: RGB color tuple
        
        Returns:
            Annotated image as bytes
        """
        try:
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            
            # Use default font
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.text((x, y), text, fill=text_color, font=font)
            
            output = io.BytesIO()
            image.save(output, format='PNG')
            output.seek(0)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"Error annotating image: {str(e)}")
            return None
    
    def grayscale(self, image_path: str) -> Optional[bytes]:
        """Convert image to grayscale."""
        try:
            image = Image.open(image_path)
            gray = image.convert('L')
            
            output = io.BytesIO()
            gray.save(output, format='PNG')
            output.seek(0)
            
            return output.getvalue()
        
        except Exception as e:
            print(f"Error converting to grayscale: {str(e)}")
            return None
    
    def get_image_info(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Get image information."""
        try:
            image = Image.open(image_path)
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size": os.path.getsize(image_path) if os.path.exists(image_path) else 0,
            }
        except Exception as e:
            print(f"Error getting image info: {str(e)}")
            return None


# Global image editing service instance
image_edit_service = ImageEditingService()

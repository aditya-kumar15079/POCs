"""
Image Document Processor for TestFoundry Framework
Handles image document parsing with OCR and analysis
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import pytesseract
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

class ImageProcessor:
    """Image document processor with OCR and content extraction"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize Image processor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.image_config = config.get('document_processing', {}).get('image', {})
        
        # Settings
        self.ocr_enabled = self.image_config.get('ocr_enabled', True)
        self.confidence_threshold = self.image_config.get('confidence_threshold', 0.8)
        self.max_image_size = self.image_config.get('max_image_size_mb', 20) * 1024 * 1024
        
        # OCR configuration
        self.ocr_config = '--psm 6'  # Assume uniform block of text
    
    async def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process image document and extract content
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            self.logger.info(f"Processing image document: {file_path.name}")
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_image_size:
                raise ValueError(f"Image size ({file_size / 1024 / 1024:.1f} MB) exceeds limit ({self.max_image_size / 1024 / 1024:.1f} MB)")
            
            # Load and analyze image
            image_analysis = await self._analyze_image(file_path)
            
            # Extract text content if OCR is enabled
            text_content = ""
            ocr_confidence = 0
            
            if self.ocr_enabled:
                text_content, ocr_confidence = await self._extract_text_ocr(file_path)
            
            # Create page content
            page_content = {
                'page_number': 1,
                'content': text_content,
                'image_analysis': image_analysis,
                'ocr_confidence': ocr_confidence,
                'has_text': len(text_content.strip()) > 0,
                'character_count': len(text_content)
            }
            
            # Create document structure
            doc_content = {
                'name': file_path.stem,
                'file_path': str(file_path),
                'file_type': 'image',
                'processor': 'ImageProcessor',
                'pages': [page_content],
                'image_properties': image_analysis
            }
            
            # Calculate statistics
            doc_content['statistics'] = {
                'total_pages': 1,
                'total_characters': len(text_content),
                'total_words': len(text_content.split()) if text_content else 0,
                'ocr_confidence': ocr_confidence,
                'image_width': image_analysis.get('width', 0),
                'image_height': image_analysis.get('height', 0),
                'file_size_bytes': file_size
            }
            
            self.logger.info(f"Image processing complete: {len(text_content)} characters extracted, "
                           f"OCR confidence: {ocr_confidence:.2f}")
            
            return doc_content
            
        except Exception as e:
            self.logger.error(f"Error processing image document {file_path.name}: {e}")
            return {
                'name': file_path.stem,
                'file_path': str(file_path),
                'file_type': 'image',
                'pages': [],
                'error': str(e)
            }
    
    async def _analyze_image(self, file_path: Path) -> Dict[str, Any]:
        """Analyze image properties and characteristics
        
        Args:
            file_path: Path to image file
            
        Returns:
            Image analysis results
        """
        analysis = {
            'width': 0,
            'height': 0,
            'format': '',
            'mode': '',
            'has_transparency': False,
            'color_analysis': {},
            'quality_metrics': {}
        }
        
        try:
            # Basic image properties
            with Image.open(file_path) as img:
                analysis['width'] = img.width
                analysis['height'] = img.height
                analysis['format'] = img.format
                analysis['mode'] = img.mode
                analysis['has_transparency'] = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                
                # Color analysis
                analysis['color_analysis'] = await self._analyze_colors(img)
                
                # Quality metrics
                analysis['quality_metrics'] = await self._assess_image_quality(img)
            
        except Exception as e:
            self.logger.warning(f"Error analyzing image: {e}")
        
        return analysis
    
    async def _analyze_colors(self, img: Image.Image) -> Dict[str, Any]:
        """Analyze image colors
        
        Args:
            img: PIL Image object
            
        Returns:
            Color analysis results
        """
        color_analysis = {
            'dominant_colors': [],
            'is_grayscale': False,
            'brightness': 0,
            'contrast': 0
        }
        
        try:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img_rgb = img.convert('RGB')
            else:
                img_rgb = img
            
            # Check if grayscale
            img_gray = img_rgb.convert('L')
            color_analysis['is_grayscale'] = img_rgb.convert('L').convert('RGB') == img_rgb
            
            # Calculate brightness (average pixel intensity)
            pixels = np.array(img_gray)
            color_analysis['brightness'] = float(np.mean(pixels) / 255.0)
            
            # Calculate contrast (standard deviation of pixel intensities)
            color_analysis['contrast'] = float(np.std(pixels) / 255.0)
            
            # Find dominant colors (simplified approach)
            img_small = img_rgb.resize((50, 50))  # Reduce size for faster processing
            pixels = np.array(img_small).reshape(-1, 3)
            
            # Use k-means clustering to find dominant colors
            try:
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                kmeans.fit(pixels)
                
                dominant_colors = []
                for color in kmeans.cluster_centers_:
                    dominant_colors.append({
                        'rgb': [int(c) for c in color],
                        'hex': '#{:02x}{:02x}{:02x}'.format(int(color[0]), int(color[1]), int(color[2]))
                    })
                
                color_analysis['dominant_colors'] = dominant_colors
                
            except ImportError:
                # Fallback without sklearn
                self.logger.debug("sklearn not available, skipping dominant color analysis")
                
        except Exception as e:
            self.logger.warning(f"Error in color analysis: {e}")
        
        return color_analysis
    
    async def _assess_image_quality(self, img: Image.Image) -> Dict[str, Any]:
        """Assess image quality metrics
        
        Args:
            img: PIL Image object
            
        Returns:
            Quality assessment results
        """
        quality_metrics = {
            'resolution_score': 0,
            'sharpness_score': 0,
            'noise_level': 0,
            'overall_quality': 'unknown'
        }
        
        try:
            # Resolution score (based on pixel count)
            total_pixels = img.width * img.height
            if total_pixels > 2000000:  # > 2MP
                quality_metrics['resolution_score'] = 1.0
            elif total_pixels > 500000:  # > 0.5MP
                quality_metrics['resolution_score'] = 0.7
            else:
                quality_metrics['resolution_score'] = 0.4
            
            # Convert to OpenCV format for advanced analysis
            img_cv = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
            
            # Sharpness assessment using Laplacian variance
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness_score'] = min(laplacian_var / 1000.0, 1.0)  # Normalize
            
            # Noise level assessment (simplified)
            # Calculate standard deviation in small patches
            patch_size = 20
            noise_estimates = []
            
            for y in range(0, gray.shape[0] - patch_size, patch_size):
                for x in range(0, gray.shape[1] - patch_size, patch_size):
                    patch = gray[y:y+patch_size, x:x+patch_size]
                    noise_estimates.append(np.std(patch))
            
            if noise_estimates:
                avg_noise = np.mean(noise_estimates)
                quality_metrics['noise_level'] = min(avg_noise / 50.0, 1.0)  # Normalize
            
            # Overall quality assessment
            overall_score = (
                quality_metrics['resolution_score'] * 0.4 +
                quality_metrics['sharpness_score'] * 0.4 +
                (1 - quality_metrics['noise_level']) * 0.2
            )
            
            if overall_score > 0.8:
                quality_metrics['overall_quality'] = 'excellent'
            elif overall_score > 0.6:
                quality_metrics['overall_quality'] = 'good'
            elif overall_score > 0.4:
                quality_metrics['overall_quality'] = 'fair'
            else:
                quality_metrics['overall_quality'] = 'poor'
                
        except Exception as e:
            self.logger.warning(f"Error in quality assessment: {e}")
        
        return quality_metrics
    
    async def _extract_text_ocr(self, file_path: Path) -> tuple[str, float]:
        """Extract text from image using OCR
        
        Args:
            file_path: Path to image file
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        text_content = ""
        confidence = 0.0
        
        try:
            # Load and preprocess image
            img = Image.open(file_path)
            processed_img = await self._preprocess_for_ocr(img)
            
            # Extract text with confidence data
            ocr_data = pytesseract.image_to_data(processed_img, config=self.ocr_config, output_type=pytesseract.Output.DICT)
            
            # Filter results by confidence and build text
            words = []
            confidences = []
            
            for i in range(len(ocr_data['text'])):
                word = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])
                
                if word and conf > 0:  # Only include words with positive confidence
                    words.append(word)
                    confidences.append(conf)
            
            # Calculate overall confidence
            if confidences:
                confidence = sum(confidences) / len(confidences) / 100.0  # Normalize to 0-1
                
                # Filter words by confidence threshold
                filtered_words = [
                    word for word, conf in zip(words, confidences)
                    if conf >= self.confidence_threshold * 100
                ]
                
                text_content = ' '.join(filtered_words)
            
            # If confidence is too low, try alternative preprocessing
            if confidence < self.confidence_threshold:
                self.logger.debug("Low OCR confidence, trying enhanced preprocessing")
                enhanced_img = await self._enhance_for_ocr(img)
                
                # Try OCR again with enhanced image
                try:
                    enhanced_text = pytesseract.image_to_string(enhanced_img, config=self.ocr_config)
                    if len(enhanced_text.strip()) > len(text_content.strip()):
                        text_content = enhanced_text.strip()
                        # Re-calculate confidence for enhanced result
                        enhanced_data = pytesseract.image_to_data(enhanced_img, config=self.ocr_config, output_type=pytesseract.Output.DICT)
                        enhanced_confidences = [int(c) for c in enhanced_data['conf'] if int(c) > 0]
                        if enhanced_confidences:
                            confidence = sum(enhanced_confidences) / len(enhanced_confidences) / 100.0
                except Exception:
                    pass
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
        
        return text_content.strip(), confidence
    
    async def _preprocess_for_ocr(self, img: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results
        
        Args:
            img: PIL Image object
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale for better OCR
            if img.mode != 'L':
                img = img.convert('L')
            
            # Resize if image is too small
            if img.width < 300 or img.height < 300:
                scale_factor = max(300 / img.width, 300 / img.height)
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            return img
            
        except Exception as e:
            self.logger.warning(f"Error in OCR preprocessing: {e}")
            return img
    
    async def _enhance_for_ocr(self, img: Image.Image) -> Image.Image:
        """Apply additional enhancement for OCR
        
        Args:
            img: PIL Image object
            
        Returns:
            Enhanced image
        """
        try:
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((2, 2), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # Convert back to PIL
            enhanced_img = Image.fromarray(binary)
            
            return enhanced_img
            
        except Exception as e:
            self.logger.warning(f"Error in OCR enhancement: {e}")
            return img
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions
        
        Returns:
            List of supported extensions
        """
        return ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
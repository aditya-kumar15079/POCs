"""
PDF Document Processor for TestFoundry Framework
Handles PDF document parsing with text, image, and table extraction
"""

import io
import fitz  # PyMuPDF
import PyPDF2
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from PIL import Image
import pytesseract

class PDFProcessor:
    """PDF document processor with comprehensive content extraction"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize PDF processor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.pdf_config = config.get('document_processing', {}).get('pdf', {})
        
        # Settings
        self.extract_images = self.pdf_config.get('extract_images', True)
        self.extract_tables = self.pdf_config.get('extract_tables', True)
        self.ocr_enabled = self.pdf_config.get('ocr_enabled', True)
    
    async def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process PDF document and extract content
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            self.logger.info(f"Processing PDF document: {file_path.name}")
            
            # Extract content using PyMuPDF (primary method)
            doc_content = await self._extract_with_pymupdf(file_path)
            
            # Fallback to PyPDF2 if PyMuPDF fails
            if not doc_content or not doc_content.get('pages'):
                self.logger.warning("PyMuPDF extraction failed, trying PyPDF2")
                doc_content = await self._extract_with_pypdf2(file_path)
            
            # Add metadata
            doc_content['name'] = file_path.stem
            doc_content['file_path'] = str(file_path)
            doc_content['file_type'] = 'pdf'
            doc_content['processor'] = 'PDFProcessor'
            
            # Calculate statistics
            total_text = sum(len(page.get('content', '')) for page in doc_content.get('pages', []))
            doc_content['statistics'] = {
                'total_pages': len(doc_content.get('pages', [])),
                'total_characters': total_text,
                'total_words': len(' '.join(page.get('content', '') for page in doc_content.get('pages', [])).split()),
                'images_extracted': sum(len(page.get('images', [])) for page in doc_content.get('pages', [])),
                'tables_extracted': sum(len(page.get('tables', [])) for page in doc_content.get('pages', []))
            }
            
            self.logger.info(f"PDF processing complete: {doc_content['statistics']['total_pages']} pages, "
                           f"{doc_content['statistics']['total_characters']} characters")
            
            return doc_content
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {file_path.name}: {e}")
            return {
                'name': file_path.stem,
                'file_path': str(file_path),
                'file_type': 'pdf',
                'pages': [],
                'error': str(e)
            }
    
    async def _extract_with_pymupdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract content using PyMuPDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted content dictionary
        """
        try:
            doc = fitz.open(str(file_path))
            pages = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text
                text = page.get_text()
                
                # Extract images if enabled
                images = []
                if self.extract_images:
                    images = await self._extract_images_pymupdf(page, page_num)
                
                # Extract tables if enabled
                tables = []
                if self.extract_tables:
                    tables = await self._extract_tables_pymupdf(page, page_num)
                
                # OCR for scanned pages if needed
                if self.ocr_enabled and len(text.strip()) < 50:
                    ocr_text = await self._ocr_page_pymupdf(page)
                    if ocr_text:
                        text = ocr_text
                
                page_content = {
                    'page_number': page_num + 1,
                    'content': text,
                    'images': images,
                    'tables': tables,
                    'has_text': len(text.strip()) > 0,
                    'character_count': len(text)
                }
                
                pages.append(page_content)
            
            doc.close()
            
            return {
                'pages': pages,
                'metadata': {
                    'total_pages': len(pages),
                    'created_with': 'PyMuPDF'
                }
            }
            
        except Exception as e:
            self.logger.error(f"PyMuPDF extraction failed: {e}")
            return {}
    
    async def _extract_with_pypdf2(self, file_path: Path) -> Dict[str, Any]:
        """Extract content using PyPDF2 (fallback method)
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted content dictionary
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    page_content = {
                        'page_number': page_num + 1,
                        'content': text,
                        'images': [],  # PyPDF2 doesn't extract images easily
                        'tables': [],  # PyPDF2 doesn't extract tables
                        'has_text': len(text.strip()) > 0,
                        'character_count': len(text)
                    }
                    
                    pages.append(page_content)
                
                return {
                    'pages': pages,
                    'metadata': {
                        'total_pages': len(pages),
                        'created_with': 'PyPDF2'
                    }
                }
                
        except Exception as e:
            self.logger.error(f"PyPDF2 extraction failed: {e}")
            return {}
    
    async def _extract_images_pymupdf(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from PDF page using PyMuPDF
        
        Args:
            page: PyMuPDF page object
            page_num: Page number
            
        Returns:
            List of image information dictionaries
        """
        images = []
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        
                        # OCR on image if enabled
                        text_content = ""
                        if self.ocr_enabled:
                            try:
                                image_pil = Image.open(io.BytesIO(img_data))
                                text_content = pytesseract.image_to_string(image_pil)
                            except Exception:
                                pass
                        
                        image_info = {
                            'index': img_index,
                            'page_number': page_num + 1,
                            'width': pix.width,
                            'height': pix.height,
                            'text_content': text_content.strip(),
                            'size_bytes': len(img_data)
                        }
                        
                        images.append(image_info)
                    
                    pix = None  # Free memory
                    
                except Exception as e:
                    self.logger.warning(f"Error extracting image {img_index} from page {page_num + 1}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error extracting images from page {page_num + 1}: {e}")
        
        return images
    
    async def _extract_tables_pymupdf(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables from PDF page using PyMuPDF
        
        Args:
            page: PyMuPDF page object
            page_num: Page number
            
        Returns:
            List of table information dictionaries
        """
        tables = []
        
        try:
            # Find tables using PyMuPDF's table detection
            tabs = page.find_tables()
            
            for tab_index, tab in enumerate(tabs):
                try:
                    # Extract table data
                    table_data = tab.extract()
                    
                    if table_data and len(table_data) > 1:  # Must have at least header and one row
                        # Convert table to text representation
                        table_text = ""
                        for row in table_data:
                            table_text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                        
                        table_info = {
                            'index': tab_index,
                            'page_number': page_num + 1,
                            'rows': len(table_data),
                            'columns': len(table_data[0]) if table_data else 0,
                            'content': table_text.strip(),
                            'bbox': tab.bbox  # Bounding box coordinates
                        }
                        
                        tables.append(table_info)
                        
                except Exception as e:
                    self.logger.warning(f"Error extracting table {tab_index} from page {page_num + 1}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error extracting tables from page {page_num + 1}: {e}")
        
        return tables
    
    async def _ocr_page_pymupdf(self, page) -> str:
        """Perform OCR on PDF page using PyMuPDF
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            OCR extracted text
        """
        try:
            # Render page as image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_data))
            
            # Perform OCR
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            return text.strip()
            
        except Exception as e:
            self.logger.warning(f"OCR failed on page: {e}")
            return ""
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions
        
        Returns:
            List of supported extensions
        """
        return ['.pdf']
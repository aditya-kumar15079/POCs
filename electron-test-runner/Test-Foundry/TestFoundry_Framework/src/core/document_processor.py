"""
Main Document Processor for TestFoundry Framework
Coordinates processing of different document types
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

from ..processors.pdf_processor import PDFProcessor
from ..processors.word_processor import WordProcessor
from ..processors.excel_processor import ExcelProcessor
from ..processors.text_processor import TextProcessor
from ..processors.image_processor import ImageProcessor
from ..utils.file_utils import get_file_info, validate_file

class DocumentProcessor:
    """Main document processor that delegates to specific processors"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize document processor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Initialize specific processors
        self.processors = {
            'pdf': PDFProcessor(config, logger),
            'word': WordProcessor(config, logger),
            'excel': ExcelProcessor(config, logger),
            'text': TextProcessor(config, logger),
            'image': ImageProcessor(config, logger)
        }
        
        # File extension to processor mapping
        self.extension_mapping = {
            '.pdf': 'pdf',
            '.docx': 'word',
            '.doc': 'word',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.txt': 'text',
            '.md': 'text',
            '.rtf': 'text',
            '.log': 'text',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.bmp': 'image',
            '.tiff': 'image',
            '.webp': 'image'
        }
    
    async def process_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a document based on its type
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary containing extracted content or None if failed
        """
        try:
            self.logger.info(f"Starting document processing: {file_path.name}")
            
            # Validate file
            is_valid, error_msg = validate_file(file_path)
            if not is_valid:
                self.logger.error(f"File validation failed for {file_path.name}: {error_msg}")
                return None
            
            # Get file information
            file_info = get_file_info(file_path)
            self.logger.debug(f"File info: {file_info}")
            
            # Determine processor type
            file_extension = file_info['suffix'].lower()
            processor_type = self.extension_mapping.get(file_extension)
            
            if not processor_type:
                self.logger.error(f"Unsupported file type: {file_extension}")
                return None
            
            # Get appropriate processor
            processor = self.processors.get(processor_type)
            if not processor:
                self.logger.error(f"No processor available for type: {processor_type}")
                return None
            
            # Process document
            self.logger.info(f"Processing {file_path.name} with {processor_type} processor")
            doc_content = await processor.process_document(file_path)
            
            if not doc_content:
                self.logger.warning(f"No content extracted from {file_path.name}")
                return None
            
            # Add processing metadata
            doc_content['processing_info'] = {
                'processor_type': processor_type,
                'file_info': file_info,
                'supported_features': self._get_processor_features(processor_type)
            }
            
            # Validate extracted content
            if not self._validate_extracted_content(doc_content):
                self.logger.warning(f"Extracted content validation failed for {file_path.name}")
                return None
            
            self.logger.info(f"Successfully processed {file_path.name}")
            return doc_content
            
        except Exception as e:
            self.logger.error(f"Error processing document {file_path.name}: {e}")
            return None
    
    def _get_processor_features(self, processor_type: str) -> Dict[str, bool]:
        """Get features supported by processor type
        
        Args:
            processor_type: Type of processor
            
        Returns:
            Dictionary of supported features
        """
        features = {
            'text_extraction': True,
            'image_extraction': False,
            'table_extraction': False,
            'ocr_support': False,
            'formula_extraction': False,
            'metadata_extraction': True
        }
        
        if processor_type == 'pdf':
            features.update({
                'image_extraction': True,
                'table_extraction': True,
                'ocr_support': True
            })
        elif processor_type == 'word':
            features.update({
                'image_extraction': True,
                'table_extraction': True
            })
        elif processor_type == 'excel':
            features.update({
                'table_extraction': True,
                'formula_extraction': True
            })
        elif processor_type == 'image':
            features.update({
                'ocr_support': True,
                'text_extraction': True  # Via OCR
            })
        
        return features
    
    def _validate_extracted_content(self, doc_content: Dict[str, Any]) -> bool:
        """Validate extracted document content
        
        Args:
            doc_content: Extracted document content
            
        Returns:
            True if content is valid
        """
        try:
            # Check required fields
            required_fields = ['name', 'file_path', 'file_type', 'processor']
            for field in required_fields:
                if field not in doc_content:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Check content structure
            if 'pages' in doc_content:
                pages = doc_content['pages']
                if not isinstance(pages, list):
                    self.logger.error("Pages must be a list")
                    return False
                
                # Validate each page
                for i, page in enumerate(pages):
                    if not isinstance(page, dict):
                        self.logger.error(f"Page {i} must be a dictionary")
                        return False
                    
                    if 'content' not in page:
                        self.logger.error(f"Page {i} missing content field")
                        return False
            
            elif 'sheets' in doc_content:
                sheets = doc_content['sheets']
                if not isinstance(sheets, list):
                    self.logger.error("Sheets must be a list")
                    return False
                
                # Validate each sheet
                for i, sheet in enumerate(sheets):
                    if not isinstance(sheet, dict):
                        self.logger.error(f"Sheet {i} must be a dictionary")
                        return False
                    
                    if 'content' not in sheet:
                        self.logger.error(f"Sheet {i} missing content field")
                        return False
            
            else:
                # Check for basic content field
                if 'content' not in doc_content:
                    self.logger.error("Document missing content field")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating content: {e}")
            return False
    
    def get_supported_extensions(self) -> list[str]:
        """Get all supported file extensions
        
        Returns:
            List of supported extensions
        """
        return list(self.extension_mapping.keys())
    
    def get_processor_for_extension(self, extension: str) -> Optional[str]:
        """Get processor type for file extension
        
        Args:
            extension: File extension (with dot)
            
        Returns:
            Processor type or None
        """
        return self.extension_mapping.get(extension.lower())
    
    async def test_processors(self) -> Dict[str, bool]:
        """Test all processors for basic functionality
        
        Returns:
            Dictionary of processor test results
        """
        test_results = {}
        
        for processor_type, processor in self.processors.items():
            try:
                # Test basic functionality
                supported_extensions = processor.get_supported_extensions()
                test_results[processor_type] = len(supported_extensions) > 0
                self.logger.info(f"Processor {processor_type}: {'PASS' if test_results[processor_type] else 'FAIL'}")
                
            except Exception as e:
                test_results[processor_type] = False
                self.logger.error(f"Processor {processor_type} test failed: {e}")
        
        return test_results
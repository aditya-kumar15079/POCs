"""
Text Document Processor for TestFoundry Framework
Handles plain text document parsing and analysis
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import chardet

class TextProcessor:
    """Text document processor with content analysis"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize Text processor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.text_config = config.get('document_processing', {}).get('text', {})
        
        # Settings
        self.max_file_size = self.text_config.get('max_file_size_mb', 50) * 1024 * 1024  # Convert to bytes
        self.auto_detect_encoding = self.text_config.get('auto_detect_encoding', True)
    
    async def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process text document and extract content
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            self.logger.info(f"Processing text document: {file_path.name}")
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds limit ({self.max_file_size / 1024 / 1024:.1f} MB)")
            
            # Detect encoding
            encoding = await self._detect_encoding(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                content = file.read()
            
            # Analyze content structure
            analysis = await self._analyze_content(content)
            
            # Organize content into pages/sections
            pages = await self._organize_content(content, analysis)
            
            # Create document structure
            doc_content = {
                'name': file_path.stem,
                'file_path': str(file_path),
                'file_type': 'text',
                'processor': 'TextProcessor',
                'encoding': encoding,
                'pages': pages,
                'analysis': analysis
            }
            
            # Calculate statistics
            total_text = sum(len(page.get('content', '')) for page in pages)
            doc_content['statistics'] = {
                'total_pages': len(pages),
                'total_characters': total_text,
                'total_words': len(content.split()),
                'total_lines': len(content.splitlines()),
                'total_paragraphs': analysis.get('paragraph_count', 0),
                'file_size_bytes': file_size
            }
            
            self.logger.info(f"Text processing complete: {doc_content['statistics']['total_pages']} pages, "
                           f"{doc_content['statistics']['total_characters']} characters")
            
            return doc_content
            
        except Exception as e:
            self.logger.error(f"Error processing text document {file_path.name}: {e}")
            return {
                'name': file_path.stem,
                'file_path': str(file_path),
                'file_type': 'text',
                'pages': [],
                'error': str(e)
            }
    
    async def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding
        
        Args:
            file_path: Path to text file
            
        Returns:
            Detected encoding
        """
        if not self.auto_detect_encoding:
            return 'utf-8'
        
        try:
            # Read a sample to detect encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read(min(32768, file_path.stat().st_size))  # Read up to 32KB
            
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            
            self.logger.debug(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
            
            # Fallback to utf-8 if confidence is too low
            if confidence < 0.7:
                encoding = 'utf-8'
            
            return encoding
            
        except Exception as e:
            self.logger.warning(f"Encoding detection failed: {e}, using utf-8")
            return 'utf-8'
    
    async def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze text content structure
        
        Args:
            content: Text content
            
        Returns:
            Analysis results
        """
        analysis = {
            'line_count': 0,
            'paragraph_count': 0,
            'word_count': 0,
            'character_count': 0,
            'sections': [],
            'structure_type': 'plain',
            'has_headers': False,
            'has_bullet_points': False,
            'has_numbered_lists': False,
            'language_hints': []
        }
        
        try:
            lines = content.splitlines()
            analysis['line_count'] = len(lines)
            analysis['character_count'] = len(content)
            analysis['word_count'] = len(content.split())
            
            # Detect paragraphs (separated by empty lines)
            paragraphs = re.split(r'\n\s*\n', content.strip())
            analysis['paragraph_count'] = len([p for p in paragraphs if p.strip()])
            
            # Detect headers and structure
            headers = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Detect various header patterns
                if self._is_header_line(line, lines, i):
                    headers.append({
                        'line_number': i + 1,
                        'text': line,
                        'level': self._get_header_level(line)
                    })
            
            analysis['sections'] = headers
            analysis['has_headers'] = len(headers) > 0
            
            # Detect lists
            analysis['has_bullet_points'] = bool(re.search(r'^[\s]*[-*•]\s+', content, re.MULTILINE))
            analysis['has_numbered_lists'] = bool(re.search(r'^[\s]*\d+[\.\)]\s+', content, re.MULTILINE))
            
            # Determine structure type
            if len(headers) > 0:
                analysis['structure_type'] = 'structured'
            elif analysis['has_bullet_points'] or analysis['has_numbered_lists']:
                analysis['structure_type'] = 'list'
            elif analysis['paragraph_count'] > 1:
                analysis['structure_type'] = 'prose'
            
            # Basic language detection hints
            analysis['language_hints'] = self._detect_language_hints(content)
            
        except Exception as e:
            self.logger.warning(f"Error in content analysis: {e}")
        
        return analysis
    
    def _is_header_line(self, line: str, lines: List[str], index: int) -> bool:
        """Check if a line is likely a header
        
        Args:
            line: Current line
            lines: All lines
            index: Current line index
            
        Returns:
            True if line is likely a header
        """
        # Skip very long lines
        if len(line) > 100:
            return False
        
        # Check for markdown-style headers
        if line.startswith('#'):
            return True
        
        # Check for all-caps headers
        if line.isupper() and len(line.split()) <= 10:
            return True
        
        # Check for underlined headers
        if index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if next_line and set(next_line) <= set('=-_*~'):
                return True
        
        # Check for numbered sections
        if re.match(r'^\d+(\.\d+)*\.?\s+[A-Z]', line):
            return True
        
        # Check for short lines that could be headers
        if len(line.split()) <= 8 and line.endswith(':'):
            return True
        
        return False
    
    def _get_header_level(self, line: str) -> int:
        """Determine header level
        
        Args:
            line: Header line
            
        Returns:
            Header level (1-6)
        """
        if line.startswith('#'):
            return min(line.count('#'), 6)
        
        if line.isupper():
            return 1
        
        if re.match(r'^\d+\.', line):
            return 2
        
        if re.match(r'^\d+\.\d+\.', line):
            return 3
        
        return 2  # Default level
    
    def _detect_language_hints(self, content: str) -> List[str]:
        """Detect language hints from content
        
        Args:
            content: Text content
            
        Returns:
            List of language hints
        """
        hints = []
        
        # Check for common patterns
        if re.search(r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b', content, re.IGNORECASE):
            hints.append('english')
        
        if re.search(r'\b(el|la|y|o|pero|en|con|de|para|por)\b', content, re.IGNORECASE):
            hints.append('spanish')
        
        if re.search(r'\b(le|la|et|ou|mais|dans|sur|avec|de|pour|par)\b', content, re.IGNORECASE):
            hints.append('french')
        
        # Check for code patterns
        if re.search(r'(function|class|import|def|var|let|const)', content):
            hints.append('code')
        
        # Check for markup patterns
        if re.search(r'<[^>]+>', content):
            hints.append('markup')
        
        return hints
    
    async def _organize_content(self, content: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Organize content into pages/sections
        
        Args:
            content: Text content
            analysis: Content analysis results
            
        Returns:
            List of page/section dictionaries
        """
        pages = []
        
        try:
            # If content has clear sections (headers), split by sections
            if analysis['has_headers'] and len(analysis['sections']) > 1:
                pages = await self._split_by_sections(content, analysis['sections'])
            else:
                # Split by character count for manageable chunks
                pages = await self._split_by_size(content)
            
        except Exception as e:
            self.logger.warning(f"Error organizing content: {e}")
            # Fallback: treat entire content as single page
            pages = [{
                'page_number': 1,
                'content': content,
                'section': None,
                'has_text': len(content.strip()) > 0,
                'character_count': len(content),
                'word_count': len(content.split()),
                'line_count': len(content.splitlines())
            }]
        
        return pages
    
    async def _split_by_sections(self, content: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split content by detected sections
        
        Args:
            content: Text content
            sections: List of detected sections
            
        Returns:
            List of page dictionaries
        """
        pages = []
        lines = content.splitlines()
        
        for i, section in enumerate(sections):
            start_line = section['line_number'] - 1  # Convert to 0-based index
            
            # Determine end line
            if i + 1 < len(sections):
                end_line = sections[i + 1]['line_number'] - 1
            else:
                end_line = len(lines)
            
            # Extract section content
            section_lines = lines[start_line:end_line]
            section_content = '\n'.join(section_lines).strip()
            
            if section_content:
                page = {
                    'page_number': i + 1,
                    'content': section_content,
                    'section': section['text'],
                    'section_level': section['level'],
                    'has_text': True,
                    'character_count': len(section_content),
                    'word_count': len(section_content.split()),
                    'line_count': len(section_lines)
                }
                pages.append(page)
        
        return pages
    
    async def _split_by_size(self, content: str, target_size: int = 2000) -> List[Dict[str, Any]]:
        """Split content by character size
        
        Args:
            content: Text content
            target_size: Target size per page
            
        Returns:
            List of page dictionaries
        """
        pages = []
        
        if len(content) <= target_size:
            pages.append({
                'page_number': 1,
                'content': content,
                'section': None,
                'has_text': len(content.strip()) > 0,
                'character_count': len(content),
                'word_count': len(content.split()),
                'line_count': len(content.splitlines())
            })
        else:
            # Split into chunks
            paragraphs = re.split(r'\n\s*\n', content)
            current_page = 1
            current_content = ""
            
            for paragraph in paragraphs:
                if len(current_content) + len(paragraph) > target_size and current_content:
                    # Create page
                    pages.append({
                        'page_number': current_page,
                        'content': current_content.strip(),
                        'section': None,
                        'has_text': True,
                        'character_count': len(current_content),
                        'word_count': len(current_content.split()),
                        'line_count': len(current_content.splitlines())
                    })
                    
                    current_page += 1
                    current_content = paragraph
                else:
                    if current_content:
                        current_content += "\n\n" + paragraph
                    else:
                        current_content = paragraph
            
            # Add final page
            if current_content.strip():
                pages.append({
                    'page_number': current_page,
                    'content': current_content.strip(),
                    'section': None,
                    'has_text': True,
                    'character_count': len(current_content),
                    'word_count': len(current_content.split()),
                    'line_count': len(current_content.splitlines())
                })
        
        return pages
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions
        
        Returns:
            List of supported extensions
        """
        return ['.txt', '.md', '.rtf', '.log']
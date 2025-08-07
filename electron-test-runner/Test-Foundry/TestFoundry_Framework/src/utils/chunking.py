"""
Text chunking strategies for TestFoundry Framework
Provides intelligent text segmentation with context preservation
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata"""
    content: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    start_index: int = 0
    end_index: int = 0
    chunk_id: str = ""
    document_name: str = ""

class TextChunker:
    """Advanced text chunking with context preservation"""
    
    def __init__(self, 
                 chunk_size: int = 2000,
                 overlap_size: int = 200,
                 preserve_sentences: bool = True,
                 preserve_paragraphs: bool = True):
        """Initialize text chunker
        
        Args:
            chunk_size: Target size for each chunk
            overlap_size: Overlap between consecutive chunks
            preserve_sentences: Whether to preserve sentence boundaries
            preserve_paragraphs: Whether to preserve paragraph boundaries
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.preserve_sentences = preserve_sentences
        self.preserve_paragraphs = preserve_paragraphs
        
        # Sentence boundary regex
        self.sentence_pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
        
        # Paragraph boundary regex
        self.paragraph_pattern = re.compile(r'\n\s*\n')
    
    def chunk_text(self, 
                   text: str, 
                   document_name: str = "",
                   page_number: Optional[int] = None,
                   section: Optional[str] = None) -> List[TextChunk]:
        """Chunk text into manageable pieces
        
        Args:
            text: Text to chunk
            document_name: Name of the source document
            page_number: Page number (if applicable)
            section: Section name (if applicable)
            
        Returns:
            List of text chunks
        """
        if not text.strip():
            return []
        
        # Clean text
        clean_text = self._clean_text(text)
        
        if len(clean_text) <= self.chunk_size:
            return [TextChunk(
                content=clean_text,
                page_number=page_number,
                section=section,
                start_index=0,
                end_index=len(clean_text),
                chunk_id=f"{document_name}_chunk_1",
                document_name=document_name
            )]
        
        # Choose chunking strategy based on preferences
        if self.preserve_paragraphs:
            chunks = self._chunk_by_paragraphs(clean_text)
        elif self.preserve_sentences:
            chunks = self._chunk_by_sentences(clean_text)
        else:
            chunks = self._chunk_by_size(clean_text)
        
        # Add metadata to chunks
        return self._add_metadata(chunks, document_name, page_number, section)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove weird characters
        text = re.sub(r'[^\w\s\.,!?;:()\-"\']', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # In some contexts
        
        return text.strip()
    
    def _chunk_by_paragraphs(self, text: str) -> List[str]:
        """Chunk text by paragraph boundaries
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        paragraphs = self.paragraph_pattern.split(text)
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap = self._get_overlap(current_chunk)
                current_chunk = overlap + paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk text by sentence boundaries
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        sentences = self.sentence_pattern.split(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap = self._get_overlap(current_chunk)
                current_chunk = overlap + sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_size(self, text: str) -> List[str]:
        """Chunk text by character count with word boundaries
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:].strip())
                break
            
            # Find word boundary
            while end > start and not text[end].isspace():
                end -= 1
            
            if end == start:  # No word boundary found
                end = start + self.chunk_size
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - self.overlap_size
            if start < 0:
                start = 0
        
        return chunks
    
    def _get_overlap(self, chunk: str) -> str:
        """Get overlap text from the end of a chunk
        
        Args:
            chunk: Text chunk
            
        Returns:
            Overlap text
        """
        if len(chunk) <= self.overlap_size:
            return chunk + " "
        
        overlap_text = chunk[-self.overlap_size:]
        
        # Try to find sentence boundary for cleaner overlap
        if self.preserve_sentences:
            sentences = self.sentence_pattern.split(overlap_text)
            if len(sentences) > 1:
                overlap_text = " ".join(sentences[1:])
        
        return overlap_text + " "
    
    def _add_metadata(self, 
                     chunks: List[str],
                     document_name: str,
                     page_number: Optional[int],
                     section: Optional[str]) -> List[TextChunk]:
        """Add metadata to chunks
        
        Args:
            chunks: List of text chunks
            document_name: Source document name
            page_number: Page number
            section: Section name
            
        Returns:
            List of TextChunk objects with metadata
        """
        text_chunks = []
        current_index = 0
        
        for i, chunk_content in enumerate(chunks):
            chunk_id = f"{document_name}_chunk_{i+1}"
            
            text_chunk = TextChunk(
                content=chunk_content,
                page_number=page_number,
                section=section,
                start_index=current_index,
                end_index=current_index + len(chunk_content),
                chunk_id=chunk_id,
                document_name=document_name
            )
            
            text_chunks.append(text_chunk)
            current_index += len(chunk_content)
        
        return text_chunks

class DocumentChunker:
    """Document-aware chunking for different document types"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize document chunker
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        qa_config = config.get('qa_generation', {})
        
        self.text_chunker = TextChunker(
            chunk_size=qa_config.get('chunk_size', 2000),
            overlap_size=qa_config.get('chunk_overlap', 200)
        )
    
    def chunk_document(self, doc_content: Dict[str, Any]) -> List[TextChunk]:
        """Chunk document content based on type
        
        Args:
            doc_content: Document content dictionary
            
        Returns:
            List of text chunks
        """
        chunks = []
        document_name = doc_content.get('name', 'unknown')
        
        # Handle different content types
        if 'pages' in doc_content:
            # Document with pages (PDF, Word) - Use SMART CHUNKING
            chunks = self._chunk_pages_smartly(doc_content['pages'], document_name)
        
        elif 'sheets' in doc_content:
            # Spreadsheet content
            for sheet_info in doc_content['sheets']:
                sheet_chunks = self.text_chunker.chunk_text(
                    sheet_info['content'],
                    document_name=document_name,
                    section=sheet_info.get('sheet_name')
                )
                chunks.extend(sheet_chunks)
        
        elif 'content' in doc_content:
            # Simple text content
            chunks = self.text_chunker.chunk_text(
                doc_content['content'],
                document_name=document_name
            )
        
        # Log chunking statistics
        total_pages = len(doc_content.get('pages', []))
        self._log_chunking_stats(chunks, total_pages, document_name)
        
        return chunks
    
    def _chunk_pages_smartly(self, pages: List[Dict[str, Any]], document_name: str) -> List[TextChunk]:
        """Smart chunking strategy for multi-page documents - FORCES page combination
        
        Args:
            pages: List of page dictionaries
            document_name: Name of the document
            
        Returns:
            List of text chunks with proper page distribution
        """
        chunks = []
        current_chunk_content = ""
        current_chunk_pages = []
        chunk_counter = 0
        
        target_chunk_size = self.config.get('qa_generation', {}).get('chunk_size', 2500)
        overlap_size = self.config.get('qa_generation', {}).get('chunk_overlap', 300)
        min_pages_per_chunk = 2  # FORCE at least 2 pages per chunk
        max_pages_per_chunk = 8  # Don't exceed 8 pages per chunk
        
        # Filter out empty pages first
        valid_pages = []
        for page_info in pages:
            page_content = page_info.get('content', '').strip()
            if page_content and len(page_content) > 50:  # Must have at least 50 characters
                valid_pages.append(page_info)
        
        if not valid_pages:
            return []  # No valid content found
        
        print(f"📄 Processing {len(valid_pages)} valid pages from {len(pages)} total pages")
        
        i = 0
        while i < len(valid_pages):
            current_chunk_content = ""
            current_chunk_pages = []
            pages_in_chunk = 0
            
            # FORCE combining multiple pages into each chunk
            while (i < len(valid_pages) and 
                   (len(current_chunk_content) < target_chunk_size or pages_in_chunk < min_pages_per_chunk) and
                   pages_in_chunk < max_pages_per_chunk):
                
                page_info = valid_pages[i]
                page_number = page_info.get('page_number', i + 1)
                page_content = page_info.get('content', '').strip()
                
                # Add page to current chunk
                if current_chunk_content:
                    current_chunk_content += "\n\n" + page_content
                else:
                    current_chunk_content = page_content
                
                current_chunk_pages.append(page_number)
                pages_in_chunk += 1
                i += 1
                
                # Break if we have enough content and minimum pages
                if (len(current_chunk_content) >= target_chunk_size and 
                    pages_in_chunk >= min_pages_per_chunk):
                    break
            
            # Create chunk if we have content
            if current_chunk_content.strip() and current_chunk_pages:
                chunk = self._create_page_chunk(
                    current_chunk_content, 
                    current_chunk_pages, 
                    chunk_counter, 
                    document_name
                )
                chunks.append(chunk)
                chunk_counter += 1
                
                # Add overlap for next chunk (if there are more pages)
                if i < len(valid_pages):
                    # Step back by 1 page to create overlap
                    overlap_pages = max(1, len(current_chunk_pages) // 4)  # 25% of pages overlap
                    i = max(i - overlap_pages, i - 1)  # At least 1 page overlap
        
        # Verify we have good chunking
        total_pages = len(valid_pages)
        avg_pages_per_chunk = total_pages / max(len(chunks), 1)
        
        print(f"📊 Chunking Results:")
        print(f"   Total Valid Pages: {total_pages}")
        print(f"   Total Chunks Created: {len(chunks)}")
        print(f"   Average Pages per Chunk: {avg_pages_per_chunk:.1f}")
        
        # Show sample chunks
        for i, chunk in enumerate(chunks[:3]):
            pages_in_chunk = len(chunk.section.split('-')) if '-' in chunk.section else 1
            print(f"   Chunk {i+1}: {chunk.section}, {len(chunk.content)} chars")
        
        if avg_pages_per_chunk < 1.5:
            print(f"⚠️  Still creating small chunks - your pages likely have very little text content")
            print(f"   This is normal for image-heavy or table-heavy documents")
        
        return chunks
    
    def _create_page_chunk(self, content: str, page_numbers: List[int], chunk_index: int, document_name: str) -> TextChunk:
        """Create a text chunk from page content
        
        Args:
            content: Combined content from pages
            page_numbers: List of page numbers in this chunk
            chunk_index: Index of the chunk
            document_name: Name of the document
            
        Returns:
            TextChunk object
        """
        # Determine primary page (middle page of the range)
        if len(page_numbers) == 1:
            primary_page = page_numbers[0]
            page_range = f"Page {page_numbers[0]}"
        else:
            primary_page = page_numbers[len(page_numbers) // 2]  # Middle page
            min_page = min(page_numbers)
            max_page = max(page_numbers)
            if min_page == max_page:
                page_range = f"Page {min_page}"
            else:
                page_range = f"Pages {min_page}-{max_page}"
        
        chunk_id = f"{document_name}_chunk_{chunk_index + 1}"
        
        return TextChunk(
            content=content.strip(),
            page_number=primary_page,
            section=page_range,
            start_index=0,
            end_index=len(content),
            chunk_id=chunk_id,
            document_name=document_name
        )
    
    def _get_overlap_from_content(self, content: str, overlap_size: int) -> str:
        """Get overlap content from the end of current content
        
        Args:
            content: Current content
            overlap_size: Size of overlap
            
        Returns:
            Overlap content
        """
        if len(content) <= overlap_size:
            return content
        
        # Get the last part of content
        overlap = content[-overlap_size:]
        
        # Try to find a sentence boundary for cleaner overlap
        sentences = overlap.split('.')
        if len(sentences) > 1:
            # Use complete sentences for overlap
            return '.'.join(sentences[1:]) + '.'
        
        return overlap
    
    def _log_chunking_stats(self, chunks: List[TextChunk], total_pages: int, document_name: str):
        """Log chunking statistics for analysis
        
        Args:
            chunks: Generated chunks
            total_pages: Total pages in document
            document_name: Name of document
        """
        if not hasattr(self, 'logger'):
            return
            
        chunk_count = len(chunks)
        avg_pages_per_chunk = total_pages / max(chunk_count, 1)
        
        # Calculate page distribution
        pages_covered = set()
        for chunk in chunks:
            if chunk.page_number:
                pages_covered.add(chunk.page_number)
        
        coverage_percentage = (len(pages_covered) / max(total_pages, 1)) * 100
        
        print(f"📊 Chunking Statistics for {document_name}:")
        print(f"   Total Pages: {total_pages}")
        print(f"   Total Chunks: {chunk_count}")
        print(f"   Avg Pages per Chunk: {avg_pages_per_chunk:.1f}")
        print(f"   Page Coverage: {coverage_percentage:.1f}%")
        print(f"   Pages Covered: {len(pages_covered)}/{total_pages}")
        
        # Warning for inefficient chunking
        if avg_pages_per_chunk < 2 and total_pages > 10:
            print(f"⚠️  WARNING: Very small chunks detected!")
            print(f"   Consider increasing chunk_size in config.yaml")
            print(f"   Current: {self.config.get('qa_generation', {}).get('chunk_size', 2000)} characters")
            print(f"   Suggested: {self.config.get('qa_generation', {}).get('chunk_size', 2000) * 2} characters")
        
        # Show chunk distribution sample
        if chunk_count > 0:
            print(f"   Sample Chunks:")
            for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
                page_info = f"Page {chunk.page_number}" if chunk.page_number else "No page"
                char_count = len(chunk.content)
                print(f"     Chunk {i+1}: {page_info}, {char_count} chars")
            if chunk_count > 5:
                print(f"     ... and {chunk_count - 5} more chunks")
        print()
    
    def get_chunk_summary(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """Get summary statistics for chunks
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Summary statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'avg_chunk_size': 0,
                'total_characters': 0,
                'pages_covered': 0,
                'sections_covered': 0
            }
        
        total_chars = sum(len(chunk.content) for chunk in chunks)
        pages = set(chunk.page_number for chunk in chunks if chunk.page_number)
        sections = set(chunk.section for chunk in chunks if chunk.section)
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': total_chars // len(chunks),
            'total_characters': total_chars,
            'pages_covered': len(pages),
            'sections_covered': len(sections)
        }
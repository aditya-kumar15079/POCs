"""
Q&A Generator for TestFoundry Framework
Generates question-answer pairs from document content using AI
"""

import asyncio
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ..ai_clients.openai_client import OpenAIClient
from ..ai_clients.azure_openai_client import AzureOpenAIClient
from ..utils.chunking import DocumentChunker, TextChunk

class QAGenerator:
    """Generates Q&A pairs from document content"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize Q&A generator
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.qa_config = config.get('qa_generation', {})
        
        # Initialize AI client
        self.ai_client = self._initialize_ai_client()
        
        # Initialize chunker
        self.chunker = DocumentChunker(config)
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        # Settings
        self.questions_per_document = self.qa_config.get('questions_per_document', 25)
        self.concurrent_requests = self.qa_config.get('concurrent_requests', 3)
        self.include_context = self.qa_config.get('include_context', True)
    
    def _initialize_ai_client(self):
        """Initialize appropriate AI client based on configuration"""
        ai_config = self.config.get('ai_service', {})
        provider = ai_config.get('provider', '').lower()
        
        if provider == 'openai':
            return OpenAIClient(ai_config['openai'], self.logger)
        elif provider == 'azure_openai':
            return AzureOpenAIClient(ai_config['azure_openai'], self.logger)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates from files
        
        Returns:
            Dictionary of prompts by document type
        """
        prompts = {}
        prompt_dir = Path("prompts")
        
        prompt_files = {
            'pdf': 'pdf_prompts.yaml',
            'word': 'word_prompts.yaml',
            'excel': 'excel_prompts.yaml',
            'text': 'text_prompts.yaml',
            'image': 'image_prompts.yaml'
        }
        
        for doc_type, filename in prompt_files.items():
            try:
                prompt_file = prompt_dir / filename
                if prompt_file.exists():
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        file_prompts = yaml.safe_load(f)
                        prompts[doc_type] = file_prompts.get('qa_generation', {})
                else:
                    self.logger.warning(f"Prompt file not found: {filename}")
                    prompts[doc_type] = self._get_default_prompts()
            except Exception as e:
                self.logger.error(f"Error loading prompts from {filename}: {e}")
                prompts[doc_type] = self._get_default_prompts()
        
        return prompts
    
    def _get_default_prompts(self) -> Dict[str, str]:
        """Get default prompt templates
        
        Returns:
            Default prompt templates
        """
        return {
            'main_prompt': """
Based on the following document content, generate {num_questions} comprehensive question-answer pairs that test understanding of the material.

Document Content:
{content}

Requirements:
1. Generate diverse question types (factual, analytical, conceptual)
2. Ensure questions are specific to the provided content
3. Provide complete, accurate answers
4. Include page/section references where applicable
5. Format as Q: [question] A: [answer]

Question-Answer Pairs:
""",
            'context_prompt': """
Generate questions that test understanding of this specific content from {document_name}.
Focus on key concepts, important details, and relationships within the material.
"""
        }
    
    async def generate_qa_pairs(self, doc_content: Dict[str, Any], document_name: str) -> List[Dict[str, Any]]:
        """Generate Q&A pairs from document content
        
        Args:
            doc_content: Document content dictionary
            document_name: Name of the document
            
        Returns:
            List of Q&A pair dictionaries
        """
        try:
            self.logger.info(f"Generating Q&A pairs for {document_name}")
            
            # Chunk the document content
            chunks = self.chunker.chunk_document(doc_content)
            
            if not chunks:
                self.logger.warning(f"No chunks generated for {document_name}")
                return []
            
            self.logger.info(f"Generated {len(chunks)} chunks from document")
            
            # Calculate questions per chunk
            questions_per_chunk = max(1, self.questions_per_document // len(chunks))
            
            # Generate Q&A pairs for each chunk concurrently
            chunk_tasks = []
            semaphore = asyncio.Semaphore(self.concurrent_requests)
            
            for i, chunk in enumerate(chunks):
                task = self._generate_qa_for_chunk(
                    chunk, doc_content.get('file_type', 'unknown'), 
                    document_name, questions_per_chunk, semaphore, chunk_index=i
                )
                chunk_tasks.append(task)
            
            # Execute tasks concurrently
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            # Combine results and create sequential IDs
            all_qa_pairs = []
            global_qa_counter = 1  # Global counter for sequential numbering
            
            for i, result in enumerate(chunk_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error generating Q&A for chunk {i}: {result}")
                    continue
                
                if result:
                    # Assign sequential IDs across all chunks
                    for qa_pair in result:
                        # Create proper chunk-based ID with sequential numbering
                        chunk_number = qa_pair.get('chunk_index', 0) + 1  # 1-based indexing
                        qa_pair['id'] = f"{self._sanitize_doc_name(document_name)}_chunk_{chunk_number}_qa_{global_qa_counter}"
                        qa_pair['sequential_id'] = global_qa_counter
                        global_qa_counter += 1
                        all_qa_pairs.append(qa_pair)
            
            # Limit to requested number of questions
            if len(all_qa_pairs) > self.questions_per_document:
                all_qa_pairs = all_qa_pairs[:self.questions_per_document]
                # Update IDs after limiting
                for i, qa_pair in enumerate(all_qa_pairs, 1):
                    qa_pair['sequential_id'] = i
            
            # Enhance Q&A pairs with additional metadata
            enhanced_qa_pairs = await self.enhance_qa_pairs(all_qa_pairs)
            
            self.logger.info(f"Generated {len(enhanced_qa_pairs)} Q&A pairs for {document_name}")
            return enhanced_qa_pairs
            
        except Exception as e:
            self.logger.error(f"Error generating Q&A pairs for {document_name}: {e}")
            return []
    
    async def _generate_qa_for_chunk(self, 
                                   chunk: TextChunk, 
                                   doc_type: str, 
                                   document_name: str, 
                                   num_questions: int,
                                   semaphore: asyncio.Semaphore,
                                   chunk_index: int = 0) -> List[Dict[str, Any]]:
        """Generate Q&A pairs for a single chunk
        
        Args:
            chunk: Text chunk to process
            doc_type: Document type
            document_name: Name of the document
            num_questions: Number of questions to generate
            semaphore: Semaphore for concurrency control
            chunk_index: Index of the chunk (0-based)
            
        Returns:
            List of Q&A pairs for the chunk
        """
        async with semaphore:
            try:
                # Log chunk processing info
                self.logger.debug(f"Processing chunk {chunk_index + 1}: Page {chunk.page_number}, {len(chunk.content)} characters")
                
                # Get appropriate prompt template
                prompts = self.prompts.get(doc_type, self._get_default_prompts())
                prompt_template = prompts.get('main_prompt', self._get_default_prompts()['main_prompt'])
                
                # Add context if enabled
                context_info = ""
                if self.include_context:
                    context_parts = []
                    if chunk.page_number:
                        context_parts.append(f"Page {chunk.page_number}")
                    if chunk.section:
                        context_parts.append(f"Section: {chunk.section}")
                    if context_parts:
                        context_info = f" (Reference: {', '.join(context_parts)})"
                
                # Generate Q&A pairs using AI client
                qa_pairs = await self.ai_client.generate_qa_pairs(
                    content=chunk.content,
                    prompt_template=prompt_template,
                    num_questions=num_questions
                )
                
                # Add metadata to each Q&A pair
                enhanced_qa_pairs = []
                for i, qa_pair in enumerate(qa_pairs):
                    enhanced_qa = {
                        'question': qa_pair.get('question', ''),
                        'answer': qa_pair.get('answer', ''),
                        'document_name': document_name,
                        'document_type': doc_type,
                        'chunk_id': chunk.chunk_id,
                        'chunk_index': chunk_index,  # Store chunk index for proper ID generation
                        'page_number': chunk.page_number,
                        'section': chunk.section,
                        'context_reference': context_info,
                        'source_content': chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                        'generated_at': self._get_timestamp()
                    }
                    
                    # Validate Q&A pair
                    if self._validate_qa_pair(enhanced_qa):
                        enhanced_qa_pairs.append(enhanced_qa)
                    else:
                        self.logger.warning(f"Invalid Q&A pair generated for chunk {chunk_index + 1}")
                
                self.logger.debug(f"Generated {len(enhanced_qa_pairs)} valid Q&A pairs from chunk {chunk_index + 1}")
                return enhanced_qa_pairs
                
            except Exception as e:
                self.logger.error(f"Error generating Q&A for chunk {chunk_index + 1}: {e}")
                return []
    
    def _sanitize_doc_name(self, doc_name: str) -> str:
        """Sanitize document name for use in IDs
        
        Args:
            doc_name: Original document name
            
        Returns:
            Sanitized name suitable for IDs
        """
        import re
        # Remove file extension
        name = doc_name.rsplit('.', 1)[0] if '.' in doc_name else doc_name
        # Replace spaces and special chars with underscores
        name = re.sub(r'[^\w\-_]', '_', name)
        # Remove multiple consecutive underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Limit length
        if len(name) > 20:
            name = name[:20]
        return name or "document"
    
    def _validate_qa_pair(self, qa_pair: Dict[str, Any]) -> bool:
        """Validate a Q&A pair
        
        Args:
            qa_pair: Q&A pair dictionary
            
        Returns:
            True if valid
        """
        # Check required fields
        required_fields = ['question', 'answer']
        for field in required_fields:
            if not qa_pair.get(field, '').strip():
                return False
        
        # Check minimum lengths
        question = qa_pair['question'].strip()
        answer = qa_pair['answer'].strip()
        
        if len(question) < 10 or len(answer) < 10:
            return False
        
        # Check for question marks in questions
        if not question.endswith('?') and not any(word in question.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who']):
            return False
        
        return True
    
    def _get_timestamp(self) -> str:
        """Get current timestamp
        
        Returns:
            Formatted timestamp string
        """
        import datetime
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    async def generate_follow_up_questions(self, 
                                         base_qa_pairs: List[Dict[str, Any]], 
                                         document_name: str) -> List[Dict[str, Any]]:
        """Generate follow-up questions based on existing Q&A pairs
        
        Args:
            base_qa_pairs: Base Q&A pairs
            document_name: Name of the document
            
        Returns:
            List of follow-up Q&A pairs
        """
        try:
            if not base_qa_pairs:
                return []
            
            # Sample a few Q&A pairs for follow-up generation
            sample_size = min(5, len(base_qa_pairs))
            sample_pairs = base_qa_pairs[:sample_size]
            
            follow_up_pairs = []
            
            for qa_pair in sample_pairs:
                try:
                    # Create follow-up prompt
                    follow_up_prompt = f"""
Based on this question and answer from {document_name}:

Q: {qa_pair['question']}
A: {qa_pair['answer']}

Generate 2 follow-up questions that:
1. Dig deeper into the topic
2. Test application or analysis of the concept
3. Connect to related ideas

Format as Q: [question] A: [answer]
"""
                    
                    # Generate follow-up Q&A pairs
                    follow_ups = await self.ai_client.generate_qa_pairs(
                        content=qa_pair['source_content'],
                        prompt_template=follow_up_prompt,
                        num_questions=2
                    )
                    
                    # Add metadata
                    for i, follow_up in enumerate(follow_ups):
                        enhanced_follow_up = {
                            'id': f"{qa_pair['id']}_followup_{i+1}",
                            'question': follow_up.get('question', ''),
                            'answer': follow_up.get('answer', ''),
                            'document_name': document_name,
                            'document_type': qa_pair.get('document_type', ''),
                            'chunk_id': qa_pair.get('chunk_id', ''),
                            'page_number': qa_pair.get('page_number'),
                            'section': qa_pair.get('section'),
                            'context_reference': qa_pair.get('context_reference', ''),
                            'source_content': qa_pair.get('source_content', ''),
                            'is_follow_up': True,
                            'base_question_id': qa_pair['id'],
                            'generated_at': self._get_timestamp()
                        }
                        
                        if self._validate_qa_pair(enhanced_follow_up):
                            follow_up_pairs.append(enhanced_follow_up)
                
                except Exception as e:
                    self.logger.warning(f"Error generating follow-up for Q&A {qa_pair.get('id', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Generated {len(follow_up_pairs)} follow-up questions for {document_name}")
            return follow_up_pairs
            
        except Exception as e:
            self.logger.error(f"Error generating follow-up questions: {e}")
            return []
    
    async def enhance_qa_pairs(self, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance Q&A pairs with additional metadata and analysis
        
        Args:
            qa_pairs: List of Q&A pairs
            
        Returns:
            Enhanced Q&A pairs
        """
        try:
            enhanced_pairs = []
            
            for qa_pair in qa_pairs:
                enhanced_qa = qa_pair.copy()
                
                # Analyze question type
                enhanced_qa['question_type'] = self._classify_question_type(qa_pair['question'])
                
                # Analyze difficulty level
                enhanced_qa['difficulty_level'] = self._assess_difficulty_level(qa_pair['question'], qa_pair['answer'])
                
                # Add keywords
                enhanced_qa['keywords'] = self._extract_keywords(qa_pair['question'] + " " + qa_pair['answer'])
                
                # Calculate quality score
                enhanced_qa['quality_score'] = self._calculate_quality_score(qa_pair)
                
                enhanced_pairs.append(enhanced_qa)
            
            return enhanced_pairs
            
        except Exception as e:
            self.logger.error(f"Error enhancing Q&A pairs: {e}")
            return qa_pairs
    
    def _classify_question_type(self, question: str) -> str:
        """Classify question type
        
        Args:
            question: Question text
            
        Returns:
            Question type classification
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what is', 'define', 'meaning of']):
            return 'definition'
        elif any(word in question_lower for word in ['how', 'process', 'steps']):
            return 'procedure'
        elif any(word in question_lower for word in ['why', 'reason', 'cause']):
            return 'explanation'
        elif any(word in question_lower for word in ['compare', 'difference', 'similar']):
            return 'comparison'
        elif any(word in question_lower for word in ['analyze', 'evaluate', 'assess']):
            return 'analysis'
        elif any(word in question_lower for word in ['apply', 'use', 'implement']):
            return 'application'
        else:
            return 'factual'
    
    def _assess_difficulty_level(self, question: str, answer: str) -> str:
        """Assess difficulty level of Q&A pair
        
        Args:
            question: Question text
            answer: Answer text
            
        Returns:
            Difficulty level (easy, medium, hard)
        """
        # Simple heuristic based on complexity indicators
        complexity_score = 0
        
        # Length of answer
        if len(answer.split()) > 50:
            complexity_score += 1
        
        # Complex words in question
        complex_words = ['analyze', 'evaluate', 'synthesize', 'compare', 'contrast', 'critique']
        if any(word in question.lower() for word in complex_words):
            complexity_score += 2
        
        # Multiple sentences in answer
        if answer.count('.') > 2:
            complexity_score += 1
        
        # Technical terms (simple check for capitalized words that might be technical terms)
        import re
        technical_terms = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', answer))
        if technical_terms > 3:
            complexity_score += 1
        
        if complexity_score >= 3:
            return 'hard'
        elif complexity_score >= 1:
            return 'medium'
        else:
            return 'easy'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of keywords
        """
        import re
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'that','with', 'by'}
        keywords = [word for word in words if word not in stop_words]
        
        # Return unique keywords (limited)
        return list(set(keywords))[:10]
    
    def _calculate_quality_score(self, qa_pair: Dict[str, Any]) -> float:
        """Calculate quality score for Q&A pair
        
        Args:
            qa_pair: Q&A pair dictionary
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        score = 0.0
        
        question = qa_pair.get('question', '')
        answer = qa_pair.get('answer', '')
        
        # Length checks
        if 15 <= len(question.split()) <= 25:
            score += 0.2
        if 20 <= len(answer.split()) <= 100:
            score += 0.3
        
        # Question format
        if question.endswith('?'):
            score += 0.1
        
        # Answer completeness
        if len(answer.split()) >= 10:
            score += 0.2
        
        # Context reference
        if qa_pair.get('context_reference'):
            score += 0.2
        
        return min(score, 1.0)
    
    async def generate_quality_report(self, qa_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate quality analysis report for Q&A pairs
        
        Args:
            qa_pairs: List of Q&A pairs
            
        Returns:
            Quality analysis report
        """
        try:
            if not qa_pairs:
                return {'total_pairs': 0, 'average_quality': 0, 'distribution': {}}
            
            quality_scores = [qa.get('quality_score', 0) for qa in qa_pairs]
            question_types = [qa.get('question_type', 'unknown') for qa in qa_pairs]
            difficulty_levels = [qa.get('difficulty_level', 'unknown') for qa in qa_pairs]
            
            # Calculate statistics
            report = {
                'total_pairs': len(qa_pairs),
                'average_quality': sum(quality_scores) / len(quality_scores),
                'quality_distribution': {
                    'high': len([s for s in quality_scores if s >= 0.8]),
                    'medium': len([s for s in quality_scores if 0.6 <= s < 0.8]),
                    'low': len([s for s in quality_scores if s < 0.6])
                },
                'question_type_distribution': {},
                'difficulty_distribution': {},
                'recommendations': []
            }
            
            # Count distributions
            for q_type in question_types:
                report['question_type_distribution'][q_type] = report['question_type_distribution'].get(q_type, 0) + 1
            
            for difficulty in difficulty_levels:
                report['difficulty_distribution'][difficulty] = report['difficulty_distribution'].get(difficulty, 0) + 1
            
            # Generate recommendations
            if report['average_quality'] < 0.6:
                report['recommendations'].append("Consider improving prompt templates for higher quality Q&A pairs")
            
            if report['quality_distribution']['low'] > len(qa_pairs) * 0.3:
                report['recommendations'].append("High number of low-quality pairs detected - review generation parameters")
            
            # Check type diversity
            if len(report['question_type_distribution']) < 3:
                report['recommendations'].append("Consider generating more diverse question types")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating quality report: {e}")
            return {'error': str(e)}
    
    async def export_qa_pairs(self, qa_pairs: List[Dict[str, Any]], output_path: Path) -> bool:
        """Export Q&A pairs to JSON format
        
        Args:
            qa_pairs: List of Q&A pairs
            output_path: Path to export file
            
        Returns:
            True if export successful
        """
        try:
            import json
            
            export_data = {
                'metadata': {
                    'total_pairs': len(qa_pairs),
                    'generated_at': self._get_timestamp(),
                    'framework_version': '1.0.0'
                },
                'qa_pairs': qa_pairs
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Q&A pairs exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting Q&A pairs: {e}")
            return False
    
    async def close(self):
        """Close the AI client connection"""
        if self.ai_client:
            await self.ai_client.close()
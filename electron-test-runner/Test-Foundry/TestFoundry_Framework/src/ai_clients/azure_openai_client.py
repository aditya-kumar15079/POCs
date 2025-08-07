"""
Azure OpenAI Client for TestFoundry Framework
Handles Azure OpenAI API interactions for Q&A generation
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import AsyncAzureOpenAI
import openai

class AzureOpenAIClient:
    """Azure OpenAI API client with retry logic and error handling"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize Azure OpenAI client
        
        Args:
            config: Azure OpenAI configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Initialize Azure OpenAI client
        self.client = AsyncAzureOpenAI(
            api_key=config['api_key'],
            azure_endpoint=config['endpoint'],
            api_version=config.get('api_version', '2024-02-15-preview')
        )
        
        # Configuration
        self.deployment_name = config['deployment_name']
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
        self.timeout = config.get('timeout', 60)
        
        self.logger.info(f"Azure OpenAI client initialized with deployment: {self.deployment_name}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_completion(self, 
                                messages: List[Dict[str, str]],
                                **kwargs) -> Optional[str]:
        """Generate completion from Azure OpenAI
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Returns:
            Generated completion text or None if failed
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                timeout=self.timeout
            )
            
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
            
            return None
            
        except openai.RateLimitError as e:
            self.logger.warning(f"Rate limit exceeded: {e}")
            await asyncio.sleep(60)  # Wait 1 minute
            raise
        
        except openai.APIError as e:
            self.logger.error(f"Azure OpenAI API error: {e}")
            raise
        
        except Exception as e:
            self.logger.error(f"Unexpected error in Azure OpenAI completion: {e}")
            raise
    
    async def generate_qa_pairs(self, 
                              content: str,
                              prompt_template: str,
                              num_questions: int = 5) -> List[Dict[str, str]]:
        """Generate Q&A pairs from content
        
        Args:
            content: Content to generate Q&A from
            prompt_template: Prompt template
            num_questions: Number of questions to generate
            
        Returns:
            List of Q&A pair dictionaries
        """
        try:
            # Format prompt
            prompt = prompt_template.format(
                content=content,
                num_questions=num_questions
            )
            
            messages = [
                {"role": "system", "content": "You are an expert at creating comprehensive question-answer pairs from documents. Generate diverse, meaningful questions that test understanding of the content."},
                {"role": "user", "content": prompt}
            ]
            
            # Generate response
            response = await self.generate_completion(messages)
            
            if not response:
                self.logger.warning("No response received for Q&A generation")
                return []
            
            # Parse Q&A pairs from response
            qa_pairs = self._parse_qa_response(response)
            
            self.logger.info(f"Generated {len(qa_pairs)} Q&A pairs")
            return qa_pairs
            
        except Exception as e:
            self.logger.error(f"Error generating Q&A pairs: {e}")
            return []
    
    async def generate_test_cases(self,
                                content: str,
                                prompt_template: str,
                                test_type: str,
                                num_cases: int = 5) -> List[Dict[str, Any]]:
        """Generate test cases for specific testing type
        
        Args:
            content: Content to generate test cases from
            prompt_template: Prompt template
            test_type: Type of test (adversarial, bias, hallucination)
            num_cases: Number of test cases to generate
            
        Returns:
            List of test case dictionaries
        """
        try:
            # Format prompt
            prompt = prompt_template.format(
                content=content,
                test_type=test_type,
                num_cases=num_cases
            )
            
            messages = [
                {"role": "system", "content": f"You are an expert at creating {test_type} test cases for AI systems. Generate challenging, realistic test scenarios."},
                {"role": "user", "content": prompt}
            ]
            
            # Generate response
            response = await self.generate_completion(messages)
            
            if not response:
                self.logger.warning(f"No response received for {test_type} test generation")
                return []
            
            # Parse test cases from response
            test_cases = self._parse_test_cases(response, test_type)
            
            self.logger.info(f"Generated {len(test_cases)} {test_type} test cases")
            return test_cases
            
        except Exception as e:
            self.logger.error(f"Error generating {test_type} test cases: {e}")
            return []
    
    def _parse_qa_response(self, response: str) -> List[Dict[str, str]]:
        """Parse Q&A pairs from API response
        
        Args:
            response: Raw API response
            
        Returns:
            List of parsed Q&A pairs
        """
        qa_pairs = []
        lines = response.strip().split('\n')
        
        current_question = ""
        current_answer = ""
        in_answer = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for question markers
            if line.startswith(('Q:', 'Question:', '**Q:', '**Question:')):
                # Save previous Q&A if exists
                if current_question and current_answer:
                    qa_pairs.append({
                        'question': current_question.strip(),
                        'answer': current_answer.strip()
                    })
                
                # Start new question
                current_question = line.split(':', 1)[1].strip() if ':' in line else line
                current_answer = ""
                in_answer = False
            
            # Check for answer markers
            elif line.startswith(('A:', 'Answer:', '**A:', '**Answer:')):
                current_answer = line.split(':', 1)[1].strip() if ':' in line else line
                in_answer = True
            
            # Continue building current answer
            elif in_answer and current_question:
                current_answer += " " + line
            
            # Continue building current question
            elif not in_answer and current_question:
                current_question += " " + line
        
        # Add last Q&A pair
        if current_question and current_answer:
            qa_pairs.append({
                'question': current_question.strip(),
                'answer': current_answer.strip()
            })
        
        return qa_pairs
    
    def _parse_test_cases(self, response: str, test_type: str) -> List[Dict[str, Any]]:
        """Parse test cases from API response
        
        Args:
            response: Raw API response
            test_type: Type of test case
            
        Returns:
            List of parsed test cases
        """
        test_cases = []
        lines = response.strip().split('\n')
        
        current_case = {}
        current_field = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for test case markers
            if line.startswith(('Test Case', 'Case', 'Scenario')):
                # Save previous case if exists
                if current_case:
                    current_case['test_type'] = test_type
                    test_cases.append(current_case)
                
                # Start new case
                current_case = {'title': line}
                current_field = ""
            
            # Check for field markers
            elif ':' in line:
                field_name, field_value = line.split(':', 1)
                field_name = field_name.strip().lower()
                field_value = field_value.strip()
                
                if field_name in ['input', 'question', 'prompt']:
                    current_case['input'] = field_value
                    current_field = 'input'
                elif field_name in ['expected', 'expected_output', 'answer']:
                    current_case['expected'] = field_value
                    current_field = 'expected'
                elif field_name in ['description', 'rationale', 'explanation']:
                    current_case['description'] = field_value
                    current_field = 'description'
            
            # Continue building current field
            elif current_field and current_case:
                if current_field not in current_case:
                    current_case[current_field] = ""
                current_case[current_field] += " " + line
        
        # Add last test case
        if current_case:
            current_case['test_type'] = test_type
            test_cases.append(current_case)
        
        return test_cases
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()
        self.logger.info("Azure OpenAI client closed")
    
    async def generate_qa_pairs(self, 
                              content: str,
                              prompt_template: str,
                              num_questions: int = 5) -> List[Dict[str, str]]:
        """Generate Q&A pairs from content
        
        Args:
            content: Content to generate Q&A from
            prompt_template: Prompt template
            num_questions: Number of questions to generate
            
        Returns:
            List of Q&A pair dictionaries
        """
        try:
            # Format prompt
            prompt = prompt_template.format(
                content=content,
                num_questions=num_questions
            )
            
            messages = [
                {"role": "system", "content": "You are an expert at creating comprehensive question-answer pairs from documents. Generate diverse, meaningful questions that test understanding of the content."},
                {"role": "user", "content": prompt}
            ]
            
            # Generate response
            response = await self.generate_completion(messages)
            
            if not response:
                self.logger.warning("No response received for Q&A generation")
                return []
            
            # Parse Q&A pairs from response
            qa_pairs = self._parse_qa_response(response)
            
            self.logger.info(f"Generated {len(qa_pairs)} Q&A pairs")
            return qa_pairs
            
        except Exception as e:
            self.logger.error(f"Error generating Q&A pairs: {e}")
            return []
    
    async def generate_test_cases(self,
                                content: str,
                                prompt_template: str,
                                test_type: str,
                                num_cases: int = 5) -> List[Dict[str, Any]]:
        """Generate test cases for specific testing type
        
        Args:
            content: Content to generate test cases from
            prompt_template: Prompt template
            test_type: Type of test (adversarial, bias, hallucination)
            num_cases: Number of test cases to generate
            
        Returns:
            List of test case dictionaries
        """
        try:
            # Format prompt
            prompt = prompt_template.format(
                content=content,
                test_type=test_type,
                num_cases=num_cases
            )
            
            messages = [
                {"role": "system", "content": f"You are an expert at creating {test_type} test cases for AI systems. Generate challenging, realistic test scenarios."},
                {"role": "user", "content": prompt}
            ]
            
            # Generate response
            response = await self.generate_completion(messages)
            
            if not response:
                self.logger.warning(f"No response received for {test_type} test generation")
                return []
            
            # Parse test cases from response
            test_cases = self._parse_test_cases(response, test_type)
            
            self.logger.info(f"Generated {len(test_cases)} {test_type} test cases")
            return test_cases
            
        except Exception as e:
            self.logger.error(f"Error generating {test_type} test cases: {e}")
            return []
    
    def _parse_qa_response(self, response: str) -> List[Dict[str, str]]:
        """Parse Q&A pairs from API response
        
        Args:
            response: Raw API response
            
        Returns:
            List of parsed Q&A pairs
        """
        qa_pairs = []
        lines = response.strip().split('\n')
        
        current_question = ""
        current_answer = ""
        in_answer = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for question markers
            if line.startswith(('Q:', 'Question:', '**Q:', '**Question:')):
                # Save previous Q&A if exists
                if current_question and current_answer:
                    qa_pairs.append({
                        'question': current_question.strip(),
                        'answer': current_answer.strip()
                    })
                
                # Start new question
                current_question = line.split(':', 1)[1].strip() if ':' in line else line
                current_answer = ""
                in_answer = False
            
            # Check for answer markers
            elif line.startswith(('A:', 'Answer:', '**A:', '**Answer:')):
                current_answer = line.split(':', 1)[1].strip() if ':' in line else line
                in_answer = True
            
            # Continue building current answer
            elif in_answer and current_question:
                current_answer += " " + line
            
            # Continue building current question
            elif not in_answer and current_question:
                current_question += " " + line
        
        # Add last Q&A pair
        if current_question and current_answer:
            qa_pairs.append({
                'question': current_question.strip(),
                'answer': current_answer.strip()
            })
        
        return qa_pairs
    
    def _parse_test_cases(self, response: str, test_type: str) -> List[Dict[str, Any]]:
        """Parse test cases from API response
        
        Args:
            response: Raw API response
            test_type: Type of test case
            
        Returns:
            List of parsed test cases
        """
        test_cases = []
        lines = response.strip().split('\n')
        
        current_case = {}
        current_field = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for test case markers
            if line.startswith(('Test Case', 'Case', 'Scenario')):
                # Save previous case if exists
                if current_case:
                    current_case['test_type'] = test_type
                    test_cases.append(current_case)
                
                # Start new case
                current_case = {'title': line}
                current_field = ""
            
            # Check for field markers
            elif ':' in line:
                field_name, field_value = line.split(':', 1)
                field_name = field_name.strip().lower()
                field_value = field_value.strip()
                
                if field_name in ['input', 'question', 'prompt']:
                    current_case['input'] = field_value
                    current_field = 'input'
                elif field_name in ['expected', 'expected_output', 'answer']:
                    current_case['expected'] = field_value
                    current_field = 'expected'
                elif field_name in ['description', 'rationale', 'explanation']:
                    current_case['description'] = field_value
                    current_field = 'description'
            
            # Continue building current field
            elif current_field and current_case:
                if current_field not in current_case:
                    current_case[current_field] = ""
                current_case[current_field] += " " + line
        
        # Add last test case
        if current_case:
            current_case['test_type'] = test_type
            test_cases.append(current_case)
        
        return test_cases
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()
        self.logger.info("Azure OpenAI client closed")
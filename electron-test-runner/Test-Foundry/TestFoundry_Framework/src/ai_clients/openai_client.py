"""
OpenAI Client for TestFoundry Framework
Handles OpenAI API interactions for Q&A generation with enhanced error handling
"""

import asyncio
import openai
from typing import List, Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import aiohttp
import ssl
import certifi

class OpenAIClient:
    """OpenAI API client with retry logic and enhanced error handling"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize OpenAI client
        
        Args:
            config: OpenAI configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Configuration
        self.api_key = config['api_key']
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
        self.timeout = config.get('timeout', 60)
        
        # Initialize OpenAI client with enhanced configuration
        self.client = self._create_client()
        
        self.logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def _create_client(self):
        """Create OpenAI client with enhanced configuration"""
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            # Create HTTP connector with custom settings
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            # Create HTTP client with custom connector
            http_client = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # Initialize OpenAI client
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                http_client=http_client,
                max_retries=3,
                timeout=self.timeout
            )
            
            return client
            
        except Exception as e:
            self.logger.error(f"Error creating OpenAI client: {e}")
            # Fallback to default client
            return openai.AsyncOpenAI(api_key=self.api_key)
    
    async def test_connection(self) -> bool:
        """Test the OpenAI API connection
        
        Returns:
            True if connection successful
        """
        try:
            self.logger.info("Testing OpenAI API connection...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello, can you respond with just 'OK'?"}
                ],
                max_tokens=10,
                timeout=30
            )
            
            if response.choices and response.choices[0].message:
                self.logger.info("✅ OpenAI API connection test successful")
                return True
            else:
                self.logger.error("❌ OpenAI API connection test failed: No response content")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ OpenAI API connection test failed: {e}")
            self._log_detailed_error(e)
            return False
    
    def _log_detailed_error(self, error: Exception):
        """Log detailed error information for debugging"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        self.logger.error(f"Error type: {error_type}")
        self.logger.error(f"Error message: {error_msg}")
        
        # Specific error handling and suggestions
        if "authentication" in error_msg.lower() or "401" in error_msg:
            self.logger.error("💡 Authentication error - check your API key")
        elif "connection" in error_msg.lower():
            self.logger.error("💡 Connection error - check internet/firewall/proxy settings")
        elif "timeout" in error_msg.lower():
            self.logger.error("💡 Timeout error - try increasing timeout or check network speed")
        elif "rate" in error_msg.lower() or "429" in error_msg:
            self.logger.error("💡 Rate limit error - wait before retrying")
        elif "ssl" in error_msg.lower() or "certificate" in error_msg.lower():
            self.logger.error("💡 SSL/Certificate error - check network security settings")
        elif "proxy" in error_msg.lower():
            self.logger.error("💡 Proxy error - check proxy configuration")
        else:
            self.logger.error("💡 Try: 1) Check internet connection 2) Verify API key 3) Check firewall/proxy")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20)
    )
    async def generate_completion(self, 
                                messages: List[Dict[str, str]],
                                **kwargs) -> Optional[str]:
        """Generate completion from OpenAI with enhanced error handling
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Returns:
            Generated completion text or None if failed
        """
        try:
            self.logger.debug(f"Generating completion with {len(messages)} messages")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                timeout=kwargs.get('timeout', self.timeout)
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content.strip()
                self.logger.debug(f"Generated completion: {len(content)} characters")
                return content
            
            self.logger.warning("No content in OpenAI response")
            return None
            
        except openai.RateLimitError as e:
            self.logger.warning(f"Rate limit exceeded: {e}")
            await asyncio.sleep(60)  # Wait 1 minute
            raise
        
        except openai.AuthenticationError as e:
            self.logger.error(f"Authentication error: {e}")
            self.logger.error("💡 Check your OpenAI API key is correct and active")
            raise
        
        except openai.APIConnectionError as e:
            self.logger.error(f"API connection error: {e}")
            self.logger.error("💡 Check your internet connection and firewall settings")
            # Try alternative connection method
            return await self._try_alternative_connection(messages, **kwargs)
        
        except openai.APITimeoutError as e:
            self.logger.error(f"API timeout error: {e}")
            self.logger.error("💡 Try increasing timeout or check network speed")
            raise
        
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            self._log_detailed_error(e)
            raise
        
        except Exception as e:
            self.logger.error(f"Unexpected error in OpenAI completion: {e}")
            self._log_detailed_error(e)
            raise
    
    async def _try_alternative_connection(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """Try alternative connection method as fallback"""
        try:
            self.logger.info("Trying alternative connection method...")
            
            # Create a new client with different settings
            fallback_client = openai.AsyncOpenAI(
                api_key=self.api_key,
                timeout=120,  # Longer timeout
                max_retries=1
            )
            
            response = await fallback_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content.strip()
                self.logger.info("✅ Alternative connection method successful")
                return content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Alternative connection also failed: {e}")
            return None
    
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
        try:
            await self.client.close()
            self.logger.info("OpenAI client closed")
        except Exception as e:
            self.logger.warning(f"Error closing OpenAI client: {e}")
    
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
        self.logger.info("OpenAI client closed")
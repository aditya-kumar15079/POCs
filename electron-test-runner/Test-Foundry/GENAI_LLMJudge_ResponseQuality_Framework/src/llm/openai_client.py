"""
OpenAI client for LLM Judge Framework.
Responsible for making API calls to OpenAI services.
"""

import openai
from typing import Dict, Any, List, Optional

from src.utils.logger import Logger



class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OpenAI client.
        
        Args:
            config: Configuration for OpenAI API
        """
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-4")
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_tokens", 2000)
        
        # Set OpenAI API key
        openai.api_key = self.api_key
        
        Logger.info(f"Initialized OpenAI client with model: {self.model}")
    
    async def generate_evaluation(
        self, 
        prompt: str, 
        reference_answer: str, 
        generated_answer: str,
        metric: str,
        system_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate evaluation for a specific metric.
        
        Args:
            prompt: The original prompt
            reference_answer: The reference answer
            generated_answer: The generated answer to evaluate
            metric: The metric to evaluate
            system_prompt: The system prompt for evaluation
        
        Returns:
            Dict containing evaluation results including score and explanation
        
        Raises:
            Exception: If there's an error with the API call
        """
        try:
            # Create messages for the conversation
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"""
                    Please evaluate the following:
                    
                    ORIGINAL PROMPT:
                    {prompt}
                    
                    REFERENCE ANSWER:
                    {reference_answer}
                    
                    GENERATED ANSWER:
                    {generated_answer}
                    
                    Evaluate the generated answer on {metric} on a scale of 0-100 with detailed explanation.
                    Return your response in the following JSON format:
                    {{
                        "score": <numerical_score>,
                        "explanation": "<detailed explanation for the score>"
                    }}
                    """
                }
            ]
            
            # Make API call
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                n=1,
                stop=None,
            )
            
            # Extract and parse result
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON directly
            import json
            try:
                result = json.loads(result_text)
                if "score" not in result or "explanation" not in result:
                    raise ValueError("Response missing required fields")
                return result
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text
                Logger.warning(f"Failed to parse direct JSON response for {metric}, attempting extraction")
                import re
                json_match = re.search(r'({.*})', result_text.replace('\n', ' '), re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        if "score" not in result or "explanation" not in result:
                            raise ValueError("Extracted JSON missing required fields")
                        return result
                    except:
                        pass
                
                # If all parsing fails, create a result with error
                Logger.error(f"Failed to parse JSON from response for {metric}")
                return {
                    "score": 0,
                    "explanation": f"Error: Could not parse evaluation result. Raw response: {result_text[:100]}..."
                }
        
        except Exception as e:
            Logger.error(f"Error generating evaluation with OpenAI: {str(e)}")
            return {
                "score": 0,
                "explanation": f"Error: {str(e)}"
            }
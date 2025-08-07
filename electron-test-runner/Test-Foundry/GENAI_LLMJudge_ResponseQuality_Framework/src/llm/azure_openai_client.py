"""
Azure OpenAI client for LLM Judge Framework.
Responsible for making API calls to Azure OpenAI services.
"""

import json
import openai
from typing import Dict, Any, List, Optional

from src.utils.logger import Logger



class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI API."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Azure OpenAI client.
        
        Args:
            config: Configuration for Azure OpenAI API
        """
        self.api_key = config.get("api_key")
        self.endpoint = config.get("endpoint")
        self.deployment_name = config.get("deployment_name")
        self.api_version = config.get("api_version", "2023-05-15")
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_tokens", 2000)
        
        # Configure Azure OpenAI
        openai.api_type = "azure"
        openai.api_key = self.api_key
        openai.api_base = self.endpoint
        openai.api_version = self.api_version
        
        Logger.info(f"Initialized Azure OpenAI client with deployment: {self.deployment_name}")
    
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
                engine=self.deployment_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                n=1,
                stop=None,
            )
            
            # Extract and parse result
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON directly
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
            Logger.error(f"Error generating evaluation with Azure OpenAI: {str(e)}")
            return {
                "score": 0,
                "explanation": f"Error: {str(e)}"
            }
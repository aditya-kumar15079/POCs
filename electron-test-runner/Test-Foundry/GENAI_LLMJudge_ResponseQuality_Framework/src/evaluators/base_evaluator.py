"""
Base evaluator for LLM Judge Framework.
Provides the foundation for all specific metric evaluators.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from src.utils.logger import Logger


class BaseEvaluator(ABC):
    """Abstract base class for all evaluators."""

    def __init__(self, llm_client):
        """
        Initialize the base evaluator.
        
        Args:
            llm_client: Client for LLM API
        """
        self.llm_client = llm_client
    
    @property
    @abstractmethod
    def metric_name(self) -> str:
        """
        Get the name of the metric.
        
        Returns:
            String name of the metric
        """
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Get the system prompt for evaluation.
        
        Returns:
            String system prompt
        """
        pass
    
    @property
    def requires_reference_answer(self) -> bool:
        """
        Whether this metric requires a reference answer for evaluation.
        
        Returns:
            True if a reference answer is required, False otherwise
        """
        # By default, most metrics require a reference answer
        return True

    @property
    def empty_reference_explanation(self) -> str:
        """
        Get explanation for when reference answer is empty.
        
        Returns:
            Explanation string
        """
        return f"No reference answer provided. {self.metric_name} evaluation was skipped."
    
    def _is_empty_reference(self, reference_answer: str) -> bool:
        """
        Check if reference answer is empty.
        
        Args:
            reference_answer: The reference answer
            
        Returns:
            True if empty, False otherwise
        """
        # Check for None, empty string, NaN, etc.
        if reference_answer is None:
            return True
        
        if isinstance(reference_answer, str) and reference_answer.strip() == "":
            return True
            
        if isinstance(reference_answer, float) and pd.isna(reference_answer):
            return True
            
        return False
    
    async def evaluate(
        self, 
        prompt: str, 
        reference_answer: str, 
        generated_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate the generated answer based on the metric.
        
        Args:
            prompt: The original prompt
            reference_answer: The reference answer
            generated_answer: The generated answer to evaluate
        
        Returns:
            Dict containing evaluation results including score and explanation
        """
        Logger.info(f"Evaluating {self.metric_name} for prompt: {prompt[:50]}...")
        
        # Check if reference answer is empty and this metric requires it
        if self.requires_reference_answer and self._is_empty_reference(reference_answer):
            Logger.warning(f"Empty reference answer for {self.metric_name}. Skipping evaluation.")
            return {
                f"{self.metric_name}Score": None,  # Use None instead of a score
                f"{self.metric_name}Remarks": self.empty_reference_explanation
            }
        
        # Get evaluation from LLM
        result = await self.llm_client.generate_evaluation(
            prompt=prompt,
            reference_answer=reference_answer,
            generated_answer=generated_answer,
            metric=self.metric_name,
            system_prompt=self.system_prompt
        )
        
        Logger.info(f"{self.metric_name} evaluation score: {result.get('score', 0)}")
        
        return {
            f"{self.metric_name}Score": result.get("score", 0),
            f"{self.metric_name}Remarks": result.get("explanation", "No explanation provided")
        }
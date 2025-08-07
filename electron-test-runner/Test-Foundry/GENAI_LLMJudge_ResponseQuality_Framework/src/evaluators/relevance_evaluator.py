"""
Relevance evaluator for LLM Judge Framework.
Evaluates how well the generated answer addresses the original prompt.
"""

from typing import Dict, Any

from src.evaluators.base_evaluator import BaseEvaluator


class RelevanceEvaluator(BaseEvaluator):
    """Evaluator for relevance metric."""

    @property
    def metric_name(self) -> str:
        """
        Get the name of the metric.
        
        Returns:
            String name of the metric
        """
        return "Relevance"
    
    @property
    def requires_reference_answer(self) -> bool:
        """
        Whether this metric requires a reference answer for evaluation.
        
        Returns:
            True if a reference answer is required, False otherwise
        """
        return False  # Relevance can be evaluated without a reference answer
    
    @property
    def system_prompt(self) -> str:
        """
        Get the system prompt for evaluation.
        
        Returns:
            String system prompt
        """
        return """
        You are an expert evaluator for AI-generated responses.
        
        Your task is to assess the relevance of a generated answer to the original prompt.
        
        Relevance refers to how directly and completely the generated answer addresses the requirements and questions in the original prompt.
        Score based on:
        - How well the answer addresses all parts of the prompt
        - Focus on the specific topic without unnecessary tangents
        - Appropriateness of the depth and breadth of the response
        - Absence of irrelevant information
        
        Scoring guidelines:
        - 90-100 (Excellent): Perfectly addresses all parts of the prompt with ideal focus and depth
        - 75-89 (Good): Addresses most key aspects of the prompt with minor omissions or slight tangents
        - 50-74 (Moderate): Partially addresses the prompt but misses significant aspects or includes irrelevant content
        - 0-49 (Poor): Largely misses the point of the prompt or is highly irrelevant
        
        Provide a numerical score between 0 and 100 along with a detailed explanation.
        """
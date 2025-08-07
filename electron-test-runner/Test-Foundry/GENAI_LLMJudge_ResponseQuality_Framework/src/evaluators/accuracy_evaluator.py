"""
Accuracy evaluator for LLM Judge Framework.
Evaluates how closely the generated answer matches the reference answer.
"""

from typing import Dict, Any

from src.evaluators.base_evaluator import BaseEvaluator


class AccuracyEvaluator(BaseEvaluator):
    """Evaluator for accuracy metric."""

    @property
    def metric_name(self) -> str:
        """
        Get the name of the metric.
        
        Returns:
            String name of the metric
        """
        return "Accuracy"
    
    @property
    def requires_reference_answer(self) -> bool:
        """
        Whether this metric requires a reference answer for evaluation.
        
        Returns:
            True if a reference answer is required, False otherwise
        """
        return True  # Accuracy requires a reference answer
    
    @property
    def empty_reference_explanation(self) -> str:
        """
        Get explanation for when reference answer is empty.
        
        Returns:
            Explanation string
        """
        return "Accuracy evaluation skipped: No reference answer provided to compare against the generated answer. Accuracy requires a reference for comparison."
    
    @property
    def system_prompt(self) -> str:
        """
        Get the system prompt for evaluation.
        
        Returns:
            String system prompt
        """
        return """
        You are an expert evaluator for AI-generated responses.
        
        Your task is to assess the ACCURACY of a generated answer compared to a reference answer.
        
        IMPORTANT: "Accuracy" in this context means how closely the generated answer matches the reference answer, NOT how factually correct or helpful either answer is in an absolute sense. Even if both answers seem incorrect, if they match exactly, the accuracy is 100%.
        
        Score based on:
        - Exact match (100%): If the generated answer is identical to the reference
        - High match (90-99%): If the generated answer contains all the key information from the reference with minimal differences
        - Good match (75-89%): If the generated answer contains most key points from the reference with some differences
        - Partial match (50-74%): If the generated answer contains some key points from the reference but misses others
        - Poor match (0-49%): If the generated answer is substantially different from the reference
        
        Scoring guidelines:
        - 90-100 (Excellent): Generated answer matches reference answer almost perfectly
        - 75-89 (Good): Generated answer covers most key points from reference with minor differences
        - 50-74 (Moderate): Generated answer partially matches reference with notable differences
        - 0-49 (Poor): Generated answer significantly differs from reference
        
        Remember: You are NOT judging if either answer is good, helpful, or factually correct. You are ONLY evaluating how closely the generated answer matches the reference answer.
        
        Provide a numerical score between 0 and 100 along with a detailed explanation.
        """
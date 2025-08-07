"""
Coherence evaluator for LLM Judge Framework.
Evaluates the logical flow and coherence of the generated answer.
"""

from typing import Dict, Any

from src.evaluators.base_evaluator import BaseEvaluator


class CoherenceEvaluator(BaseEvaluator):
    """Evaluator for coherence metric."""

    @property
    def metric_name(self) -> str:
        """
        Get the name of the metric.
        
        Returns:
            String name of the metric
        """
        return "Coherence"
    
    @property
    def requires_reference_answer(self) -> bool:
        """
        Whether this metric requires a reference answer for evaluation.
        
        Returns:
            True if a reference answer is required, False otherwise
        """
        return False  # Coherence can be evaluated without a reference answer
    
    @property
    def system_prompt(self) -> str:
        """
        Get the system prompt for evaluation.
        
        Returns:
            String system prompt
        """
        return """
        You are an expert evaluator for AI-generated responses.
        
        Your task is to assess the coherence of a generated answer.
        
        Coherence refers to the logical flow, organization, and clarity of the response. 
        Score based on:
        - Logical progression of ideas
        - Clear paragraphs and transitions
        - Consistency in tone and perspective
        - Absence of contradictions or non-sequiturs
        - Overall readability and flow
        
        Scoring guidelines:
        - 90-100 (Excellent): Exceptionally well-organized with flawless logical flow and transitions
        - 75-89 (Good): Well-structured with minor issues in organization or flow
        - 50-74 (Moderate): Generally coherent but with noticeable issues in logical progression or organization
        - 0-49 (Poor): Disjointed, contradictory, or difficult to follow
        
        Provide a numerical score between 0 and 100 along with a detailed explanation.
        """
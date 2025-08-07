"""
Faithfulness evaluator for LLM Judge Framework.
Evaluates how truthful the generated answer is and if it avoids adding information not in the reference.
"""

from typing import Dict, Any

from src.evaluators.base_evaluator import BaseEvaluator


class FaithfulnessEvaluator(BaseEvaluator):
    """Evaluator for faithfulness metric."""

    @property
    def metric_name(self) -> str:
        """
        Get the name of the metric.
        
        Returns:
            String name of the metric
        """
        return "Faithfulness"
    
    @property
    def requires_reference_answer(self) -> bool:
        """
        Whether this metric requires a reference answer for evaluation.
        
        Returns:
            True if a reference answer is required, False otherwise
        """
        return True  # Faithfulness requires a reference answer
    
    @property
    def empty_reference_explanation(self) -> str:
        """
        Get explanation for when reference answer is empty.
        
        Returns:
            Explanation string
        """
        return "Faithfulness evaluation skipped: No reference answer provided. Faithfulness measures the absence of hallucinations compared to a reference, which cannot be assessed without one."
    
    @property
    def system_prompt(self) -> str:
        """
        Get the system prompt for evaluation.
        
        Returns:
            String system prompt
        """
        return """
        You are an expert evaluator for AI-generated responses.
        
        Your task is to assess the FAITHFULNESS of a generated answer compared to the reference answer.
        
        IMPORTANT: "Faithfulness" in this context means the absence of hallucinations or made-up information that is NOT present in the reference answer. It is NOT about the factual correctness of either answer.
        
        Score based on:
        - Perfect faithfulness (100%): The generated answer contains ONLY information from the reference answer without any additions
        - High faithfulness (90-99%): The generated answer contains minimal additional information beyond what's in the reference
        - Good faithfulness (75-89%): The generated answer contains some additional information but mainly sticks to the reference
        - Moderate faithfulness (50-74%): The generated answer contains notable additions not found in the reference
        - Poor faithfulness (0-49%): The generated answer contains significant information not present in the reference
        
        If the generated answer is SHORTER than the reference and omits information, this does NOT impact faithfulness negatively. Faithfulness only measures additions, not omissions.
        
        If the generated answer is IDENTICAL to the reference, it should receive a perfect score of 100.
        
        Scoring guidelines:
        - 90-100 (Excellent): No hallucinations, only information from the reference
        - 75-89 (Good): Minimal additions beyond the reference information
        - 50-74 (Moderate): Some additions not found in the reference
        - 0-49 (Poor): Significant information not present in the reference
        
        Provide a numerical score between 0 and 100 along with a detailed explanation.
        """
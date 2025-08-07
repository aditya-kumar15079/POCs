"""
Tests for evaluators in LLM Judge Framework.
"""

import unittest
import asyncio
from unittest.mock import MagicMock, patch

from src.evaluators.accuracy_evaluator import AccuracyEvaluator
from src.evaluators.coherence_evaluator import CoherenceEvaluator
from src.evaluators.relevance_evaluator import RelevanceEvaluator
from src.evaluators.faithfulness_evaluator import FaithfulnessEvaluator
from src.evaluators.bias_evaluator import BiasEvaluator
from src.evaluators.toxicity_evaluator import ToxicityEvaluator


class TestEvaluators(unittest.TestCase):
    """Tests for evaluator classes."""

    def setUp(self):
        """Set up tests."""
        # Mock LLM client
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.generate_evaluation = MagicMock()
        
        # Sample evaluation result
        self.sample_evaluation = {
            "score": 85,
            "explanation": "This is a test explanation."
        }
        
        # Configure mock to return the sample evaluation
        async def mock_generate(*args, **kwargs):
            return self.sample_evaluation
        
        self.mock_llm_client.generate_evaluation.side_effect = mock_generate
        
        # Test data
        self.prompt = "Test prompt"
        self.reference_answer = "Test reference answer"
        self.generated_answer = "Test generated answer"
    
    def test_accuracy_evaluator(self):
        """Test AccuracyEvaluator."""
        evaluator = AccuracyEvaluator(self.mock_llm_client)
        
        # Check properties
        self.assertEqual(evaluator.metric_name, "Bias")
        self.assertTrue(isinstance(evaluator.system_prompt, str))
        self.assertIn("bias", evaluator.system_prompt.lower())
        
        # Test evaluate method
        result = asyncio.run(evaluator.evaluate(
            self.prompt, 
            self.reference_answer, 
            self.generated_answer
        ))
        
        # Verify result
        self.assertIn("BiasScore", result)
        self.assertIn("BiasRemarks", result)
    
    def test_toxicity_evaluator(self):
        """Test ToxicityEvaluator."""
        evaluator = ToxicityEvaluator(self.mock_llm_client)
        
        # Check properties
        self.assertEqual(evaluator.metric_name, "Toxicity")
        self.assertTrue(isinstance(evaluator.system_prompt, str))
        self.assertIn("toxic", evaluator.system_prompt.lower())
        
        # Test evaluate method
        result = asyncio.run(evaluator.evaluate(
            self.prompt, 
            self.reference_answer, 
            self.generated_answer
        ))
        
        # Verify result
        self.assertIn("ToxicityScore", result)
        self.assertIn("ToxicityRemarks", result)


if __name__ == "__main__":
    unittest.main()(evaluator.metric_name, "Accuracy")
        self.assertTrue(isinstance(evaluator.system_prompt, str))
        self.assertIn("accuracy", evaluator.system_prompt.lower())
        
        # Test evaluate method
        result = asyncio.run(evaluator.evaluate(
            self.prompt, 
            self.reference_answer, 
            self.generated_answer
        ))
        
        # Verify result
        self.assertIn("AccuracyScore", result)
        self.assertIn("AccuracyRemarks", result)
        self.assertEqual(result["AccuracyScore"], 85)
        self.assertEqual(result["AccuracyRemarks"], "This is a test explanation.")
        
        # Verify LLM client was called with correct parameters
        self.mock_llm_client.generate_evaluation.assert_called_once()
        call_args = self.mock_llm_client.generate_evaluation.call_args[1]
        self.assertEqual(call_args["prompt"], self.prompt)
        self.assertEqual(call_args["reference_answer"], self.reference_answer)
        self.assertEqual(call_args["generated_answer"], self.generated_answer)
        self.assertEqual(call_args["metric"], "Accuracy")
        self.assertEqual(call_args["system_prompt"], evaluator.system_prompt)
    
    def test_coherence_evaluator(self):
        """Test CoherenceEvaluator."""
        evaluator = CoherenceEvaluator(self.mock_llm_client)
        
        # Check properties
        self.assertEqual(evaluator.metric_name, "Coherence")
        self.assertTrue(isinstance(evaluator.system_prompt, str))
        self.assertIn("coherence", evaluator.system_prompt.lower())
        
        # Test evaluate method
        result = asyncio.run(evaluator.evaluate(
            self.prompt, 
            self.reference_answer, 
            self.generated_answer
        ))
        
        # Verify result
        self.assertIn("CoherenceScore", result)
        self.assertIn("CoherenceRemarks", result)
    
    def test_relevance_evaluator(self):
        """Test RelevanceEvaluator."""
        evaluator = RelevanceEvaluator(self.mock_llm_client)
        
        # Check properties
        self.assertEqual(evaluator.metric_name, "Relevance")
        self.assertTrue(isinstance(evaluator.system_prompt, str))
        self.assertIn("relevance", evaluator.system_prompt.lower())
        
        # Test evaluate method
        result = asyncio.run(evaluator.evaluate(
            self.prompt, 
            self.reference_answer, 
            self.generated_answer
        ))
        
        # Verify result
        self.assertIn("RelevanceScore", result)
        self.assertIn("RelevanceRemarks", result)
    
    def test_faithfulness_evaluator(self):
        """Test FaithfulnessEvaluator."""
        evaluator = FaithfulnessEvaluator(self.mock_llm_client)
        
        # Check properties
        self.assertEqual(evaluator.metric_name, "Faithfulness")
        self.assertTrue(isinstance(evaluator.system_prompt, str))
        self.assertIn("faithfulness", evaluator.system_prompt.lower())
        
        # Test evaluate method
        result = asyncio.run(evaluator.evaluate(
            self.prompt, 
            self.reference_answer, 
            self.generated_answer
        ))
        
        # Verify result
        self.assertIn("FaithfulnessScore", result)
        self.assertIn("FaithfulnessRemarks", result)
    
    def test_bias_evaluator(self):
        """Test BiasEvaluator."""
        evaluator = BiasEvaluator(self.mock_llm_client)
        
        # Check properties
        self.assertEqual
"""
Main module for LLM Judge Framework.
Coordinates the evaluation of GenAI responses.
"""

import os
import asyncio
import pandas as pd
from typing import Dict, List, Any, Optional, Type

# Import path fixing (use only if needed)
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Utils imports
from src.utils.logger import Logger
from src.utils.config_handler import ConfigHandler
from src.utils.excel_handler import ExcelHandler

# LLM client imports
from src.llm.openai_client import OpenAIClient
from src.llm.azure_openai_client import AzureOpenAIClient

# Import BaseEvaluator directly
from src.evaluators.base_evaluator import BaseEvaluator

# Import specific evaluator classes directly
# Import these individually to avoid issues with the __init__.py file
from src.evaluators.accuracy_evaluator import AccuracyEvaluator
from src.evaluators.coherence_evaluator import CoherenceEvaluator
from src.evaluators.relevance_evaluator import RelevanceEvaluator
from src.evaluators.faithfulness_evaluator import FaithfulnessEvaluator
from src.evaluators.bias_evaluator import BiasEvaluator
from src.evaluators.toxicity_evaluator import ToxicityEvaluator


class LLMJudge:
    """Main class for LLM Judge Framework."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the LLM Judge.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        # Initialize configuration
        self.config_handler = ConfigHandler(config_path)
        
        # Set up logging
        Logger.setup(self.config_handler.get_log_config())
        
        # Initialize Excel handler
        self.excel_handler = ExcelHandler(
            input_path=self.config_handler.get_input_path(),
            output_folder=self.config_handler.get_output_folder(),
            scoring_config=self.config_handler.get_scoring_config()
        )
        
        # Initialize LLM client
        llm_config = self.config_handler.get_llm_config()
        if llm_config["type"] == "openai":
            self.llm_client = OpenAIClient(llm_config["config"])
        elif llm_config["type"] == "azure_openai":
            self.llm_client = AzureOpenAIClient(llm_config["config"])
        else:
            raise ValueError(f"Unsupported LLM provider type: {llm_config['type']}")
        
        # Initialize evaluators
        self.evaluators = self._initialize_evaluators()
        
        Logger.info("LLM Judge initialized successfully")
    
    def _initialize_evaluators(self) -> Dict[str, BaseEvaluator]:
        """
        Initialize evaluators based on configuration.
        
        Returns:
            Dict of metric names to evaluator instances
        """
        # Dictionary of available evaluator classes keyed by lowercase metric name
        evaluator_classes = {
            "accuracy": AccuracyEvaluator,
            "coherence": CoherenceEvaluator,
            "relevance": RelevanceEvaluator,
            "faithfulness": FaithfulnessEvaluator,
            "bias": BiasEvaluator,
            "toxicity": ToxicityEvaluator
        }
        
        # Get enabled metrics from configuration
        enabled_metrics = self.config_handler.get_enabled_metrics()
        
        # Create and return dictionary of enabled evaluator instances
        evaluators = {}
        for metric, evaluator_class in evaluator_classes.items():
            if enabled_metrics.get(metric.lower(), False):
                evaluators[metric] = evaluator_class(self.llm_client)
        
        return evaluators
    
    async def _evaluate_test_case(
        self, 
        prompt: str, 
        reference_answer: str, 
        generated_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single test case using all enabled evaluators.
        
        Args:
            prompt: The original prompt
            reference_answer: The reference answer
            generated_answer: The generated answer to evaluate
        
        Returns:
            Dict containing evaluation results for all metrics
        """
        results = {}
        
        # Run all evaluators concurrently
        evaluation_tasks = []
        for evaluator in self.evaluators.values():
            task = evaluator.evaluate(
                prompt=prompt,
                reference_answer=reference_answer,
                generated_answer=generated_answer
            )
            evaluation_tasks.append(task)
        
        # Await all evaluation tasks
        evaluation_results = await asyncio.gather(*evaluation_tasks)
        
        # Merge results from all evaluators
        for result in evaluation_results:
            results.update(result)
        
        return results
    
    async def run(self) -> str:
        """
        Run the LLM Judge framework.
        
        Returns:
            Path to the generated output report
        """
        try:
            Logger.info("Starting LLM Judge evaluation")
            
            # Read test cases from Excel file
            test_cases_df, excel_metrics = self.excel_handler.read_test_cases()
            
            # Update metrics configuration from Excel if available
            if excel_metrics:
                Logger.info("Updating metrics configuration from Excel")
                self.config_handler.update_from_excel(excel_metrics)
                # Reinitialize evaluators with updated configuration
                self.evaluators = self._initialize_evaluators()
            
            # Create results DataFrame
            results_df = test_cases_df.copy()
            
            # Process each test case
            for index, row in test_cases_df.iterrows():
                Logger.info(f"Processing test case {row['TestID']}")
                
                # Evaluate test case
                evaluation_results = await self._evaluate_test_case(
                    prompt=row["Prompt"],
                    reference_answer=row["ReferenceAnswer"],
                    generated_answer=row["GeneratedAnswer"]
                )
                
                # Update results DataFrame
                for key, value in evaluation_results.items():
                    results_df.at[index, key] = value
            
            # Generate output report with specified file format
            output_path = self.excel_handler.generate_output_report(
                results_df, 
                file_format=self.config_handler.get_output_file_format()
            )
            
            Logger.info(f"LLM Judge evaluation completed. Output report: {output_path}")
            return output_path
        
        except Exception as e:
            Logger.error(f"Error running LLM Judge: {str(e)}")
            raise


def main():
    """Main entry point for the framework."""
    asyncio.run(LLMJudge().run())


if __name__ == "__main__":
    main()
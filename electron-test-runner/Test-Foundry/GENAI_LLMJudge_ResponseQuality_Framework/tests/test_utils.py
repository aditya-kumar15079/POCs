"""
Tests for utility modules in LLM Judge Framework.
"""

import unittest
import os
import tempfile
import shutil
import pandas as pd
from unittest.mock import patch, MagicMock

from src.utils.config_handler import ConfigHandler
from src.utils.excel_handler import ExcelHandler
from src.utils.logger import Logger


class TestConfigHandler(unittest.TestCase):
    """Tests for ConfigHandler class."""

    def setUp(self):
        """Set up tests."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample config content
        self.config_content = """
        llm_provider:
          type: "openai"
          openai:
            api_key: "test_api_key"
            model: "gpt-4"
            temperature: 0.0
            max_tokens: 2000
        
        paths:
          input_folder: "input"
          output_folder: "output"
          input_file: "test_cases.xlsx"
        
        evaluation:
          metrics:
            accuracy: true
            coherence: true
            relevance: false
            faithfulness: true
            bias: false
            toxicity: true
          
          scoring:
            excellent: 
              min: 90
              max: 100
              color: "green"
            good:
              min: 75
              max: 89
              color: "light_green"
            moderate:
              min: 50
              max: 74
              color: "amber"
            poor:
              min: 0
              max: 49
              color: "red"
        """
        
        # Create config file
        self.config_path = os.path.join(self.temp_dir, "config.yaml")
        with open(self.config_path, "w") as f:
            f.write(self.config_content)
    
    def tearDown(self):
        """Tear down tests."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """Test loading configuration from file."""
        # Create ConfigHandler
        config_handler = ConfigHandler(self.config_path)
        
        # Check config
        self.assertEqual(config_handler.config["llm_provider"]["type"], "openai")
        self.assertEqual(config_handler.config["llm_provider"]["openai"]["api_key"], "test_api_key")
        self.assertEqual(config_handler.config["paths"]["input_folder"], "input")
    
    def test_get_llm_config(self):
        """Test getting LLM configuration."""
        # Create ConfigHandler
        config_handler = ConfigHandler(self.config_path)
        
        # Get LLM config
        llm_config = config_handler.get_llm_config()
        
        # Check config
        self.assertEqual(llm_config["type"], "openai")
        self.assertEqual(llm_config["config"]["api_key"], "test_api_key")
        self.assertEqual(llm_config["config"]["model"], "gpt-4")
    
    def test_get_enabled_metrics(self):
        """Test getting enabled metrics."""
        # Create ConfigHandler
        config_handler = ConfigHandler(self.config_path)
        
        # Get enabled metrics
        enabled_metrics = config_handler.get_enabled_metrics()
        
        # Check metrics
        self.assertTrue(enabled_metrics["accuracy"])
        self.assertTrue(enabled_metrics["coherence"])
        self.assertFalse(enabled_metrics["relevance"])
        self.assertTrue(enabled_metrics["faithfulness"])
        self.assertFalse(enabled_metrics["bias"])
        self.assertTrue(enabled_metrics["toxicity"])
    
    def test_update_from_excel(self):
        """Test updating metrics from Excel."""
        # Create ConfigHandler
        config_handler = ConfigHandler(self.config_path)
        
        # Excel metrics
        excel_metrics = {
            "accuracy": False,
            "coherence": True,
            "relevance": True,
            "faithfulness": False
        }
        
        # Update from Excel
        config_handler.update_from_excel(excel_metrics)
        
        # Get updated metrics
        updated_metrics = config_handler.get_enabled_metrics()
        
        # Check metrics
        self.assertFalse(updated_metrics["accuracy"])
        self.assertTrue(updated_metrics["coherence"])
        self.assertTrue(updated_metrics["relevance"])
        self.assertFalse(updated_metrics["faithfulness"])
        self.assertFalse(updated_metrics["bias"])  # Unchanged
        self.assertTrue(updated_metrics["toxicity"])  # Unchanged
    
    def test_invalid_config_file(self):
        """Test handling of invalid config file."""
        # Invalid config path
        invalid_path = os.path.join(self.temp_dir, "nonexistent.yaml")
        
        # Check exception
        with self.assertRaises(FileNotFoundError):
            ConfigHandler(invalid_path)


class TestExcelHandler(unittest.TestCase):
    """Tests for ExcelHandler class."""

    def setUp(self):
        """Set up tests."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, "input")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.input_dir, exist_ok=True)
        
        # Sample scoring config
        self.scoring_config = {
            "excellent": {"min": 90, "max": 100, "color": "green"},
            "good": {"min": 75, "max": 89, "color": "light_green"},
            "moderate": {"min": 50, "max": 74, "color": "amber"},
            "poor": {"min": 0, "max": 49, "color": "red"}
        }
        
        # Create sample input Excel file
        self.input_path = os.path.join(self.input_dir, "test_cases.xlsx")
        
        # Create sample test cases DataFrame
        test_cases_data = {
            "TestID": [1, 2, 3],
            "Prompt": ["Prompt 1", "Prompt 2", "Prompt 3"],
            "ReferenceAnswer": ["Ref 1", "Ref 2", "Ref 3"],
            "GeneratedAnswer": ["Gen 1", "Gen 2", "Gen 3"]
        }
        test_cases_df = pd.DataFrame(test_cases_data)
        
        # Create metrics DataFrame
        metrics_data = {
            "Metric": ["accuracy", "coherence", "relevance", "faithfulness", "bias", "toxicity"],
            "Enabled": [True, True, False, True, False, True]
        }
        metrics_df = pd.DataFrame(metrics_data)
        
        # Save to Excel
        with pd.ExcelWriter(self.input_path, engine='openpyxl') as writer:
            test_cases_df.to_excel(writer, sheet_name="TestCases", index=False)
            metrics_df.to_excel(writer, sheet_name="Metrics", index=False)
    
    def tearDown(self):
        """Tear down tests."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_read_test_cases(self):
        """Test reading test cases from Excel."""
        # Create ExcelHandler
        excel_handler = ExcelHandler(self.input_path, self.output_dir, self.scoring_config)
        
        # Read test cases
        test_cases_df, metrics_config = excel_handler.read_test_cases()
        
        # Check test cases
        self.assertEqual(len(test_cases_df), 3)
        self.assertEqual(test_cases_df.iloc[0]["Prompt"], "Prompt 1")
        self.assertEqual(test_cases_df.iloc[1]["ReferenceAnswer"], "Ref 2")
        self.assertEqual(test_cases_df.iloc[2]["GeneratedAnswer"], "Gen 3")
        
        # Check metrics config
        self.assertTrue(metrics_config["accuracy"])
        self.assertTrue(metrics_config["coherence"])
        self.assertFalse(metrics_config["relevance"])
        self.assertTrue(metrics_config["faithfulness"])
        self.assertFalse(metrics_config["bias"])
        self.assertTrue(metrics_config["toxicity"])
    
    def test_missing_input_file(self):
        """Test handling of missing input file."""
        # Non-existent input path
        nonexistent_path = os.path.join(self.input_dir, "nonexistent.xlsx")
        
        # Create ExcelHandler
        excel_handler = ExcelHandler(nonexistent_path, self.output_dir, self.scoring_config)
        
        # Check exception
        with self.assertRaises(FileNotFoundError):
            excel_handler.read_test_cases()
    
    @patch('pandas.ExcelWriter')
    def test_generate_output_report(self, mock_excel_writer):
        """Test generating output report."""
        # Create ExcelHandler
        excel_handler = ExcelHandler(self.input_path, self.output_dir, self.scoring_config)
        
        # Sample results DataFrame
        results_data = {
            "TestID": [1, 2, 3],
            "Prompt": ["Prompt 1", "Prompt 2", "Prompt 3"],
            "ReferenceAnswer": ["Ref 1", "Ref 2", "Ref 3"],
            "GeneratedAnswer": ["Gen 1", "Gen 2", "Gen 3"],
            "AccuracyScore": [95, 85, 65],
            "AccuracyRemarks": ["Excellent", "Good", "Moderate"],
            "CoherenceScore": [80, 75, 60],
            "CoherenceRemarks": ["Good", "Good", "Moderate"]
        }
        results_df = pd.DataFrame(results_data)
        
        # Generate report
        output_path = excel_handler.generate_output_report(results_df)
        
        # Check output path
        self.assertTrue(output_path.startswith(self.output_dir))
        self.assertTrue("llm_judge_results_" in output_path)
        self.assertTrue(output_path.endswith(".xlsx"))


class TestLogger(unittest.TestCase):
    """Tests for Logger class."""

    def setUp(self):
        """Set up tests."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        
        # Log config
        self.log_config = {
            "level": "INFO",
            "file": self.log_file
        }
    
    def tearDown(self):
        """Tear down tests."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_setup(self):
        """Test logger setup."""
        # Setup logger
        Logger.setup(self.log_config)
        
        # Get logger
        logger = Logger.get_logger()
        
        # Check logger
        self.assertEqual(logger.level, 20)  # INFO level
        self.assertEqual(len(logger.handlers), 2)  # File and console handlers
    
    def test_logging_methods(self):
        """Test logging methods."""
        # Setup logger
        Logger.setup(self.log_config)
        
        # Mock logger
        mock_logger = MagicMock()
        Logger._logger = mock_logger
        
        # Call logging methods
        Logger.debug("Debug message")
        Logger.info("Info message")
        Logger.warning("Warning message")
        Logger.error("Error message")
        Logger.critical("Critical message")
        
        # Check method calls
        mock_logger.debug.assert_called_once_with("Debug message")
        mock_logger.info.assert_called_once_with("Info message")
        mock_logger.warning.assert_called_once_with("Warning message")
        mock_logger.error.assert_called_once_with("Error message")
        mock_logger.critical.assert_called_once_with("Critical message")


if __name__ == "__main__":
    unittest.main()
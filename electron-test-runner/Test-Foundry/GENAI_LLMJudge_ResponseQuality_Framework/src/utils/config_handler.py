"""
Configuration handler for LLM Judge Framework.
Responsible for loading and validating the configuration from YAML files.
"""

import os
import yaml
from typing import Dict, Any, Optional


class ConfigHandler:
    """Handler for loading and accessing configuration settings."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the ConfigHandler.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dict containing the configuration settings
        
        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the config file has invalid YAML
        """
        try:
            with open(self.config_path, 'r') as config_file:
                return yaml.safe_load(config_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML configuration: {str(e)}")
    
    def _validate_config(self) -> None:
        """
        Validate the loaded configuration.
        
        Raises:
            ValueError: If required configuration values are missing or invalid
        """
        # Check if required sections exist
        required_sections = ["llm_provider", "paths", "evaluation"]
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Required configuration section '{section}' is missing")
        
        # Validate LLM provider configuration
        provider_type = self.config["llm_provider"].get("type")
        if provider_type not in ["openai", "azure_openai"]:
            raise ValueError(f"Invalid LLM provider type: {provider_type}")
        
        # Validate that corresponding provider config exists
        if provider_type == "openai" and "openai" not in self.config["llm_provider"]:
            raise ValueError("OpenAI configuration missing")
        elif provider_type == "azure_openai" and "azure_openai" not in self.config["llm_provider"]:
            raise ValueError("Azure OpenAI configuration missing")
        
        # Validate evaluation metrics
        if "metrics" not in self.config["evaluation"]:
            raise ValueError("Evaluation metrics configuration missing")
        
        # Set default output file name format if not specified
        if "output_file_format" not in self.config.get("paths", {}):
            self.config["paths"]["output_file_format"] = "LLM_Judge_ResponseQuality_Results_{timestamp}.xlsx"

    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM provider configuration.
        
        Returns:
            Dict containing LLM configuration
        """
        provider_type = self.config["llm_provider"]["type"]
        return {
            "type": provider_type,
            "config": self.config["llm_provider"][provider_type]
        }
    
    def get_input_path(self) -> str:
        """
        Get the input file path.
        
        Returns:
            Path to the input Excel file
        """
        input_folder = self.config["paths"]["input_folder"]
        input_file = self.config["paths"]["input_file"]
        return os.path.join(input_folder, input_file)
    
    def get_output_folder(self) -> str:
        """
        Get the output folder path.
        
        Returns:
            Path to the output folder
        """
        return self.config["paths"]["output_folder"]
    
    def get_output_file_format(self) -> str:
        """
        Get the output file name format.
        
        Returns:
            Format string for output file name
        """
        return self.config["paths"].get("output_file_format", "LLM_Judge_ResponseQuality_Results_{timestamp}.xlsx")
    
    def get_enabled_metrics(self) -> Dict[str, bool]:
        """
        Get configuration for which metrics are enabled.
        
        Returns:
            Dict of metric names and their enabled status
        """
        return self.config["evaluation"]["metrics"]
    
    def get_scoring_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Get scoring category configuration.
        
        Returns:
            Dict of scoring categories with min/max values and colors
        """
        return self.config["evaluation"]["scoring"]
    
    def get_log_config(self) -> Dict[str, str]:
        """
        Get logging configuration.
        
        Returns:
            Dict containing logging configuration
        """
        return self.config.get("logging", {"level": "INFO", "file": "logs/llm_judge.log"})
    
    def update_from_excel(self, excel_metrics: Dict[str, bool]) -> None:
        """
        Update metrics configuration from Excel file settings.
        
        Args:
            excel_metrics: Dict of metric names and their enabled status from Excel
        """
        # Update metrics configuration with values from Excel
        for metric, enabled in excel_metrics.items():
            if metric in self.config["evaluation"]["metrics"]:
                self.config["evaluation"]["metrics"][metric] = enabled
"""
Configuration Manager for TestFoundry Framework
Handles loading and validation of configuration settings
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or "config.yaml"
        self.config = {}
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file
        
        Returns:
            Dictionary containing configuration settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
                
            # Validate configuration
            self._validate_config()
            
            # Set environment variables for API keys if not already set
            self._set_environment_variables()
            
            return self.config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file: {e}")
    
    def _validate_config(self):
        """Validate configuration settings"""
        required_sections = [
            'ai_service',
            'qa_generation',
            'test_case_generation',
            'document_processing',
            'output',
            'logging'
        ]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate AI service configuration
        ai_service = self.config['ai_service']
        provider = ai_service.get('provider', '').lower()
        
        if provider not in ['openai', 'azure_openai']:
            raise ValueError("ai_service.provider must be 'openai' or 'azure_openai'")
        
        # Validate provider-specific configuration
        if provider == 'openai':
            if 'openai' not in ai_service:
                raise ValueError("OpenAI configuration section missing")
            if not ai_service['openai'].get('api_key'):
                raise ValueError("OpenAI API key is required")
        
        elif provider == 'azure_openai':
            if 'azure_openai' not in ai_service:
                raise ValueError("Azure OpenAI configuration section missing")
            azure_config = ai_service['azure_openai']
            required_azure_fields = ['api_key', 'endpoint', 'deployment_name']
            for field in required_azure_fields:
                if not azure_config.get(field):
                    raise ValueError(f"Azure OpenAI {field} is required")
        
        # Validate numeric settings
        qa_gen = self.config['qa_generation']
        if qa_gen.get('questions_per_document', 0) <= 0:
            raise ValueError("qa_generation.questions_per_document must be positive")
        
        if qa_gen.get('concurrent_requests', 0) <= 0:
            raise ValueError("qa_generation.concurrent_requests must be positive")
    
    def _set_environment_variables(self):
        """Set environment variables for API keys"""
        ai_service = self.config['ai_service']
        provider = ai_service.get('provider', '').lower()
        
        if provider == 'openai':
            api_key = ai_service['openai'].get('api_key')
            if api_key and not os.getenv('OPENAI_API_KEY'):
                os.environ['OPENAI_API_KEY'] = api_key
        
        elif provider == 'azure_openai':
            api_key = ai_service['azure_openai'].get('api_key')
            if api_key and not os.getenv('AZURE_OPENAI_API_KEY'):
                os.environ['AZURE_OPENAI_API_KEY'] = api_key
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """Get a specific setting using dot notation
        
        Args:
            key_path: Dot-separated path to setting (e.g., 'ai_service.provider')
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def update_setting(self, key_path: str, value: Any):
        """Update a specific setting using dot notation
        
        Args:
            key_path: Dot-separated path to setting
            value: New value for the setting
        """
        keys = key_path.split('.')
        current = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def save_config(self, output_path: Optional[str] = None):
        """Save current configuration to file
        
        Args:
            output_path: Path to save config (defaults to original path)
        """
        output_path = output_path or self.config_path
        
        with open(output_path, 'w', encoding='utf-8') as file:
            yaml.dump(self.config, file, default_flow_style=False, indent=2)
    
    def get_ai_client_config(self) -> Dict[str, Any]:
        """Get AI client configuration based on selected provider
        
        Returns:
            Configuration dictionary for the selected AI provider
        """
        ai_service = self.config['ai_service']
        provider = ai_service.get('provider', '').lower()
        
        if provider == 'openai':
            return {
                'provider': 'openai',
                'config': ai_service['openai']
            }
        elif provider == 'azure_openai':
            return {
                'provider': 'azure_openai',
                'config': ai_service['azure_openai']
            }
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ConfigManager(config_path='{self.config_path}', provider='{self.get_setting('ai_service.provider')}')"
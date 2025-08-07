"""
Tests for LLM clients in LLM Judge Framework.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock

from src.llm.openai_client import OpenAIClient
from src.llm.azure_openai_client import AzureOpenAIClient


class TestOpenAIClient(unittest.TestCase):
    """Tests for OpenAI client."""

    def setUp(self):
        """Set up tests."""
        self.config = {
            "api_key": "test_api_key",
            "model": "test-model",
            "temperature": 0.0,
            "max_tokens": 2000
        }
        
        # Test data
        self.prompt = "Test prompt"
        self.reference_answer = "Test reference answer"
        self.generated_answer = "Test generated answer"
        self.metric = "Accuracy"
        self.system_prompt = "Test system prompt"
        
        # Sample response
        self.sample_response = MagicMock()
        self.sample_response.choices = [MagicMock()]
        self.sample_response.choices[0].message = MagicMock()
        self.sample_response.choices[0].message.content = '{"score": 85, "explanation": "Test explanation"}'

    @patch('openai.ChatCompletion.acreate')
    def test_generate_evaluation(self, mock_acreate):
        """Test generate_evaluation method."""
        # Configure mock
        mock_acreate.return_value = asyncio.Future()
        mock_acreate.return_value.set_result(self.sample_response)
        
        # Create client
        client = OpenAIClient(self.config)
        
        # Call method
        result = asyncio.run(client.generate_evaluation(
            prompt=self.prompt,
            reference_answer=self.reference_answer,
            generated_answer=self.generated_answer,
            metric=self.metric,
            system_prompt=self.system_prompt
        ))
        
        # Verify API call
        mock_acreate.assert_called_once()
        call_args = mock_acreate.call_args[1]
        self.assertEqual(call_args["model"], self.config["model"])
        self.assertEqual(call_args["temperature"], self.config["temperature"])
        self.assertEqual(call_args["max_tokens"], self.config["max_tokens"])
        
        # Verify messages
        messages = call_args["messages"]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], self.system_prompt)
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn(self.prompt, messages[1]["content"])
        self.assertIn(self.reference_answer, messages[1]["content"])
        self.assertIn(self.generated_answer, messages[1]["content"])
        
        # Verify result
        self.assertEqual(result["score"], 85)
        self.assertEqual(result["explanation"], "Test explanation")

    @patch('openai.ChatCompletion.acreate')
    def test_invalid_json_response(self, mock_acreate):
        """Test handling of invalid JSON response."""
        # Configure mock with invalid JSON
        sample_response = MagicMock()
        sample_response.choices = [MagicMock()]
        sample_response.choices[0].message = MagicMock()
        sample_response.choices[0].message.content = 'Not a valid JSON response'
        
        mock_acreate.return_value = asyncio.Future()
        mock_acreate.return_value.set_result(sample_response)
        
        # Create client
        client = OpenAIClient(self.config)
        
        # Call method
        result = asyncio.run(client.generate_evaluation(
            prompt=self.prompt,
            reference_answer=self.reference_answer,
            generated_answer=self.generated_answer,
            metric=self.metric,
            system_prompt=self.system_prompt
        ))
        
        # Verify error handling
        self.assertEqual(result["score"], 0)
        self.assertIn("Error", result["explanation"])
        self.assertIn("Not a valid JSON", result["explanation"])


class TestAzureOpenAIClient(unittest.TestCase):
    """Tests for Azure OpenAI client."""

    def setUp(self):
        """Set up tests."""
        self.config = {
            "api_key": "test_api_key",
            "endpoint": "https://test-endpoint.openai.azure.com/",
            "deployment_name": "test-deployment",
            "api_version": "2023-05-15",
            "temperature": 0.0,
            "max_tokens": 2000
        }
        
        # Test data
        self.prompt = "Test prompt"
        self.reference_answer = "Test reference answer"
        self.generated_answer = "Test generated answer"
        self.metric = "Accuracy"
        self.system_prompt = "Test system prompt"
        
        # Sample response
        self.sample_response = MagicMock()
        self.sample_response.choices = [MagicMock()]
        self.sample_response.choices[0].message = MagicMock()
        self.sample_response.choices[0].message.content = '{"score": 85, "explanation": "Test explanation"}'

    @patch('openai.ChatCompletion.acreate')
    def test_generate_evaluation(self, mock_acreate):
        """Test generate_evaluation method."""
        # Configure mock
        mock_acreate.return_value = asyncio.Future()
        mock_acreate.return_value.set_result(self.sample_response)
        
        # Create client
        client = AzureOpenAIClient(self.config)
        
        # Call method
        result = asyncio.run(client.generate_evaluation(
            prompt=self.prompt,
            reference_answer=self.reference_answer,
            generated_answer=self.generated_answer,
            metric=self.metric,
            system_prompt=self.system_prompt
        ))
        
        # Verify API call
        mock_acreate.assert_called_once()
        call_args = mock_acreate.call_args[1]
        self.assertEqual(call_args["engine"], self.config["deployment_name"])
        self.assertEqual(call_args["temperature"], self.config["temperature"])
        self.assertEqual(call_args["max_tokens"], self.config["max_tokens"])
        
        # Verify messages
        messages = call_args["messages"]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], self.system_prompt)
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn(self.prompt, messages[1]["content"])
        self.assertIn(self.reference_answer, messages[1]["content"])
        self.assertIn(self.generated_answer, messages[1]["content"])
        
        # Verify result
        self.assertEqual(result["score"], 85)
        self.assertEqual(result["explanation"], "Test explanation")


if __name__ == "__main__":
    unittest.main()
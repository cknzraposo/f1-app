"""Configuration loader for F1 AI Assistant."""
import json
import os
from pathlib import Path
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json and override with environment variables.
    If config.json doesn't exist, returns default configuration with LLM disabled.
    
    Returns:
        Dict containing application configuration
    """
    # Load base config from JSON file
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        # Return default config with LLM disabled
        print(f"⚠️  Configuration file not found: {config_path}")
        print("ℹ️  Running with default config (LLM disabled)")
        print("ℹ️  Create config.json to enable LLM features (Ollama/Azure OpenAI)")
        
        return {
            "llm": {
                "ollama": {
                    "enabled": False,
                    "endpoint": "http://localhost:11434",
                    "model": "llama3.2",
                    "timeout": 30
                },
                "azure_openai": {
                    "enabled": False,
                    "endpoint": "",
                    "api_key": "",
                    "api_version": "2024-08-01-preview",
                    "deployment_name": ""
                }
            }
        }
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Override Azure OpenAI settings with environment variables if present
    if os.getenv("AZURE_OPENAI_API_KEY"):
        config["llm"]["azure_openai"]["api_key"] = os.getenv("AZURE_OPENAI_API_KEY")
    
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        config["llm"]["azure_openai"]["endpoint"] = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    return config


# Global config instance
CONFIG = load_config()

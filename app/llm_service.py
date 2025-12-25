"""LLM service for natural language query processing."""
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from app.config import CONFIG

logger = logging.getLogger(__name__)


class LLMService:
    """Unified LLM service with Ollama primary and Azure OpenAI fallback."""
    
    def __init__(self):
        self.config = CONFIG["llm"]
        self.ollama_endpoint = self.config["ollama"]["endpoint"]
        self.ollama_model = self.config["ollama"]["model"]
        self.ollama_timeout = self.config["ollama"]["timeout"]
        
        # Initialize Azure OpenAI client if enabled
        self.azure_client = None
        if self.config["azure_openai"]["enabled"]:
            try:
                from openai import AzureOpenAI
                azure_config = self.config["azure_openai"]
                self.azure_client = AzureOpenAI(
                    api_key=azure_config.get("api_key", ""),
                    api_version=azure_config["api_version"],
                    azure_endpoint=azure_config["endpoint"]
                )
                self.azure_deployment = azure_config["deployment_name"]
                logger.info("Azure OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI: {e}")
                self.azure_client = None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for F1 query processing."""
        return """You are an F1 data assistant with access to Formula 1 historical data from 1984-2024.

Available API endpoints:
- /api/seasons/{year}/standings - Get championship standings (drivers and constructors)
- /api/seasons/{year} - Get complete season with all race results
- /api/seasons/{year}/races/{round} - Get specific race result
- /api/drivers/search?name={name} - Search for drivers by name
- /api/drivers/{driver_id}/stats - Get driver career statistics
- /api/constructors/{constructor_id} - Get constructor information
- /api/constructors/{constructor_id}/stats - Get constructor statistics

When a user asks an F1 question, analyze it and return a JSON response with:
{
    "action": "api_call",
    "endpoint": "/api/...",
    "params": {"key": "value"},
    "context": "brief description of what data is needed"
}

For follow-up questions or questions requiring data synthesis, you may need multiple API calls.

Examples:
- "Who won the 2010 championship?" -> {"action": "api_call", "endpoint": "/api/seasons/2010/standings", "params": {}}
- "How many wins does Hamilton have?" -> {"action": "api_call", "endpoint": "/api/drivers/search", "params": {"name": "Hamilton"}}
- "Tell me about Red Bull" -> {"action": "api_call", "endpoint": "/api/constructors/red_bull", "params": {}}

If the question cannot be answered with available data, return:
{"action": "respond", "message": "I don't have that information in the F1 database (1984-2024)."}

Return ONLY valid JSON, no other text."""
    
    def _query_ollama(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Query Ollama API.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Response text or None if failed
        """
        try:
            payload = {
                "model": self.ollama_model,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_endpoint}/api/chat",
                json=payload,
                timeout=self.ollama_timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"]
            
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama connection failed - service may not be running")
            return None
        except requests.exceptions.Timeout:
            logger.warning("Ollama request timed out")
            return None
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            return None
    
    def _query_azure_openai(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Query Azure OpenAI API.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Response text or None if failed
        """
        if not self.azure_client:
            return None
        
        try:
            response = self.azure_client.chat.completions.create(
                model=self.azure_deployment,
                messages=messages
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI query failed: {e}")
            return None
    
    def process_query(self, user_question: str) -> Dict[str, Any]:
        """
        Process a user's natural language question.
        
        Args:
            user_question: The user's question
            
        Returns:
            Dict with action and relevant data
        """
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_question}
        ]
        
        # Try Ollama first
        response = self._query_ollama(messages)
        llm_source = "ollama"
        
        # Fallback to Azure OpenAI if Ollama failed
        if response is None and self.azure_client:
            logger.info("Falling back to Azure OpenAI")
            response = self._query_azure_openai(messages)
            llm_source = "azure_openai"
        
        # If both failed
        if response is None:
            return {
                "action": "error",
                "message": "LLM service unavailable. Please ensure Ollama is running or configure Azure OpenAI.",
                "source": "none"
            }
        
        # Parse LLM response
        try:
            # Extract JSON from response (handle cases where LLM adds extra text)
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(response)
            parsed["source"] = llm_source
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}\nResponse: {response}")
            return {
                "action": "error",
                "message": "Failed to understand the question. Please try rephrasing.",
                "source": llm_source,
                "raw_response": response
            }
    
    def generate_summary(self, user_question: str, api_data: Any) -> str:
        """
        Generate a natural language summary of API data.
        
        Args:
            user_question: Original user question
            api_data: Data from API call
            
        Returns:
            Natural language summary
        """
        messages = [
            {"role": "system", "content": "You are an F1 expert. Provide clear, concise answers to F1 questions using the provided data. Format your response in a conversational way."},
            {"role": "user", "content": f"Question: {user_question}\n\nData: {json.dumps(api_data, indent=2)}\n\nProvide a natural language answer:"}
        ]
        
        # Try Ollama first
        response = self._query_ollama(messages)
        
        # Fallback to Azure OpenAI
        if response is None and self.azure_client:
            response = self._query_azure_openai(messages)
        
        return response or "Unable to generate summary."

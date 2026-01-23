"""LLM service wrapper for OpenAI API."""
import os
from typing import Optional, List, Dict, Any
import openai
from utils.config import config


# Set OpenAI API key
openai.api_key = config.OPENAI_API_KEY


class LLMService:
    """Wrapper for OpenAI API with streaming and caching."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.tokens_used = 0
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System message to prepend
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        
        Returns:
            Dict with 'response' and 'tokens_used'
        """
        try:
            # Prepare messages with system prompt
            all_messages = []
            if system_prompt:
                all_messages.append({"role": "system", "content": system_prompt})
            all_messages.extend(messages)
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=all_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract response
            answer = response['choices'][0]['message']['content']
            
            # Track tokens
            tokens_used = response.get('usage', {}).get('total_tokens', 0)
            self.tokens_used += tokens_used
            config.USAGE_STATS['total_tokens'] += tokens_used
            
            return {
                "response": answer,
                "tokens_used": tokens_used,
                "model": self.model,
            }
        
        except Exception as e:
            return {
                "response": f"Error generating response: {str(e)}",
                "tokens_used": 0,
                "error": str(e),
            }
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """
        Stream response tokens as they're generated.
        Yields token chunks for real-time display in frontend.
        """
        try:
            all_messages = []
            if system_prompt:
                all_messages.append({"role": "system", "content": system_prompt})
            all_messages.extend(messages)
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=all_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            
            async for chunk in response:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    yield delta['content']
        
        except Exception as e:
            yield f"\n\nError: {str(e)}"
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        return {
            "model": self.model,
            "tokens_used": self.tokens_used,
            "total_system_tokens": config.USAGE_STATS['total_tokens'],
        }


# Global LLM service instance
llm_service = LLMService()

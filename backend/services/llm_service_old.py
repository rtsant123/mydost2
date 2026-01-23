"""LLM service wrapper for Anthropic Claude AI API."""
import os
from typing import Optional, List, Dict, Any
from anthropic import AsyncAnthropic
from utils.config import config


# Initialize Anthropic client
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", config.ANTHROPIC_API_KEY))


class LLMService:
    """Wrapper for Anthropic Claude AI with streaming and caching."""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
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
            # Prepare messages (Claude doesn't use system in messages array)
            claude_messages = []
            for msg in messages:
                if msg["role"] != "system":
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Call Claude API
            response = await client.messages.create(
                model=self.model,
                system=system_prompt if system_prompt else None,
                messages=claude_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract response
            answer = response.content[0].text
            
            # Track tokens
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
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
            # Prepare messages
            claude_messages = []
            for msg in messages:
                if msg["role"] != "system":
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Stream from Claude
            async with client.messages.stream(
                model=self.model,
                system=system_prompt if system_prompt else None,
                messages=claude_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                
                # Get final message to track tokens
                final_message = await stream.get_final_message()
                tokens_used = final_message.usage.input_tokens + final_message.usage.output_tokens
                self.tokens_used += tokens_used
                config.USAGE_STATS['total_tokens'] += tokens_used
        
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

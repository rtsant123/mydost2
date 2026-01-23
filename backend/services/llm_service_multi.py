"""Multi-provider LLM service supporting Anthropic, OpenAI, and Google Gemini."""
import os
from typing import Optional, List, Dict, Any
from anthropic import AsyncAnthropic
from utils.config import config


class MultiLLMService:
    """Wrapper for multiple LLM providers with unified interface."""
    
    def __init__(self, provider: str = None, model: str = None):
        """
        Initialize LLM service with specified provider.
        
        Args:
            provider: LLM provider ('anthropic', 'openai', 'gemini')
            model: Model name (provider-specific)
        """
        self.provider = provider or config.LLM_PROVIDER
        self.tokens_used = 0
        
        # Default models per provider
        default_models = {
            "anthropic": "claude-3-5-sonnet-20241022",
            "openai": "gpt-4o",
            "gemini": "gemini-1.5-pro"
        }
        
        self.model = model or default_models.get(self.provider, default_models["anthropic"])
        
        # Initialize provider clients
        if self.provider == "anthropic":
            self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        elif self.provider == "openai":
            try:
                import openai
                openai.api_key = config.OPENAI_API_KEY
                self.client = openai
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.client = genai
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM (unified interface).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System message to prepend
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        
        Returns:
            Dict with 'response' and 'tokens_used'
        """
        try:
            if self.provider == "anthropic":
                return await self._generate_anthropic(messages, system_prompt, temperature, max_tokens)
            elif self.provider == "openai":
                return await self._generate_openai(messages, system_prompt, temperature, max_tokens)
            elif self.provider == "gemini":
                return await self._generate_gemini(messages, system_prompt, temperature, max_tokens)
        except Exception as e:
            return {
                "response": f"Error generating response: {str(e)}",
                "tokens_used": 0,
                "error": str(e),
            }
    
    async def _generate_anthropic(self, messages, system_prompt, temperature, max_tokens):
        """Generate response using Anthropic Claude."""
        claude_messages = []
        for msg in messages:
            if msg["role"] != "system":
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt if system_prompt else None,
            messages=claude_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        answer = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        self.tokens_used += tokens_used
        config.USAGE_STATS['total_tokens'] += tokens_used
        
        return {
            "response": answer,
            "tokens_used": tokens_used,
            "model": self.model,
            "provider": "anthropic"
        }
    
    async def _generate_openai(self, messages, system_prompt, temperature, max_tokens):
        """Generate response using OpenAI."""
        import openai
        
        # Prepare messages
        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        self.tokens_used += tokens_used
        config.USAGE_STATS['total_tokens'] += tokens_used
        
        return {
            "response": answer,
            "tokens_used": tokens_used,
            "model": self.model,
            "provider": "openai"
        }
    
    async def _generate_gemini(self, messages, system_prompt, temperature, max_tokens):
        """Generate response using Google Gemini."""
        import google.generativeai as genai
        
        # Prepare prompt
        full_prompt = ""
        if system_prompt:
            full_prompt += f"{system_prompt}\n\n"
        
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            full_prompt += f"{role}: {msg['content']}\n\n"
        
        full_prompt += "Assistant:"
        
        model = genai.GenerativeModel(self.model)
        response = await model.generate_content_async(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        
        answer = response.text
        tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else max_tokens
        self.tokens_used += tokens_used
        config.USAGE_STATS['total_tokens'] += tokens_used
        
        return {
            "response": answer,
            "tokens_used": tokens_used,
            "model": self.model,
            "provider": "gemini"
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
        Only Anthropic supports streaming currently.
        """
        try:
            if self.provider == "anthropic":
                claude_messages = []
                for msg in messages:
                    if msg["role"] != "system":
                        claude_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                async with self.client.messages.stream(
                    model=self.model,
                    system=system_prompt if system_prompt else None,
                    messages=claude_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
                    
                    final_message = await stream.get_final_message()
                    tokens_used = final_message.usage.input_tokens + final_message.usage.output_tokens
                    self.tokens_used += tokens_used
                    config.USAGE_STATS['total_tokens'] += tokens_used
            else:
                # Fallback: non-streaming for other providers
                result = await self.generate_response(messages, system_prompt, temperature, max_tokens)
                yield result["response"]
        
        except Exception as e:
            yield f"\n\nError: {str(e)}"
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text) // 4
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        return {
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "total_system_tokens": config.USAGE_STATS['total_tokens'],
        }


# Global LLM service instance (uses config.LLM_PROVIDER)
llm_service = MultiLLMService()

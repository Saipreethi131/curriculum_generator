"""
Groq Cloud Client - Ultra-fast LLM inference (FREE tier)
Groq runs LLMs on custom hardware at 500+ tokens/sec
Sign up: https://console.groq.com (free API key)

This replaces slow local Ollama for hackathon demos.
Ollama is kept as fallback if Groq is unavailable.
"""
import requests
import time
import json
import os
from typing import Dict, Any, Optional


class GroqClient:
    """Ultra-fast LLM client using Groq's free cloud API."""
    
    def __init__(self, api_key: str = None, model: str = "llama-3.1-8b-instant"):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (from https://console.groq.com)
                     Can also be set via GROQ_API_KEY env variable.
            model: Model to use. Best FREE options:
                   - "llama-3.1-8b-instant" (fastest, great quality)
                   - "gemma2-9b-it" (good alternative)
                   - "llama-3.3-70b-versatile" (best quality, still fast)
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model = model
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 30  # Groq is fast, 30s is generous
        
        # Generation settings
        self.default_options = {
            'temperature': 0.1,
            'max_tokens': 4096,
            'top_p': 0.8,
        }
    
    def is_available(self) -> bool:
        """Check if Groq API key is configured."""
        return bool(self.api_key)
    
    def generate(self, prompt: str, options: Optional[Dict] = None, json_mode: bool = True) -> Dict[str, Any]:
        """
        Generate response from Groq (OpenAI-compatible API).
        
        Args:
            prompt: Input prompt
            options: Override default options
            json_mode: If True, force JSON output. If False, allow free-form (Markdown).
            
        Returns:
            Dict with 'response', 'generation_time', 'model', 'success'
        """
        if not self.api_key:
            return {
                'response': '',
                'generation_time': 0,
                'model': self.model,
                'success': False,
                'error': 'GROQ_API_KEY not set. Get free key at https://console.groq.com'
            }
        
        start_time = time.time()
        
        # Merge options
        request_options = {**self.default_options}
        if options:
            request_options.update(options)
        
        try:
            payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a curriculum designer." + (" Always respond with valid JSON only, no markdown or explanation." if json_mode else " Respond with well-formatted Markdown.")
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": request_options.get('temperature', 0.1),
                    "max_tokens": request_options.get('max_tokens', 1024),
                    "top_p": request_options.get('top_p', 0.8),
            }
            
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            elapsed = time.time() - start_time
            
            content = result['choices'][0]['message']['content']
            
            return {
                'response': content,
                'generation_time': round(elapsed, 2),
                'model': self.model,
                'success': True
            }
            
        except requests.HTTPError as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            try:
                error_detail = e.response.json()
                error_msg = error_detail.get('error', {}).get('message', str(e))
            except:
                pass
            return {
                'response': '',
                'generation_time': round(elapsed, 2),
                'model': self.model,
                'success': False,
                'error': f'Groq API error: {error_msg}'
            }
            
        except requests.Timeout:
            elapsed = time.time() - start_time
            return {
                'response': '',
                'generation_time': round(elapsed, 2),
                'model': self.model,
                'success': False,
                'error': f'Request timeout after {self.timeout}s'
            }
            
        except requests.RequestException as e:
            elapsed = time.time() - start_time
            return {
                'response': '',
                'generation_time': round(elapsed, 2),
                'model': self.model,
                'success': False,
                'error': str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Groq API is accessible."""
        if not self.api_key:
            return {
                'connected': False,
                'model': self.model,
                'status': 'no_api_key',
                'message': 'Set GROQ_API_KEY env variable or pass api_key to constructor'
            }
        
        try:
            # Quick test with minimal tokens
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            response.raise_for_status()
            
            return {
                'connected': True,
                'model': self.model,
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'connected': False,
                'model': self.model,
                'status': 'error',
                'message': str(e)
            }

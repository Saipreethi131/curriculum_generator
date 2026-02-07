"""
Optimized Ollama Client for Fast Curriculum Generation
Target: <20s on Intel i5 11th Gen, 16GB RAM
"""
import requests
import time
import json
from typing import Dict, Any, Optional

class OllamaClient:
    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client with performance-optimized settings.
        
        Args:
            model: Recommended models for <20s latency:
                   - qwen2.5:3b (5-15s, BEST JSON + FAST)
                   - phi3:mini (8-12s, good balance)
                   - llama3.2:3b (5-10s, fast backup)
            base_url: Ollama API endpoint
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        # ULTRA-FAST settings for hackathon
        self.default_options = {
            'temperature': 0.1,      # Very low = deterministic + fastest
            'num_ctx': 4096,         # Context window for curriculum generation
            'num_predict': 3000,     # Enough tokens for flexible semester counts
            'top_p': 0.8,
            'top_k': 20,
            'repeat_penalty': 1.1,
            'num_thread': 8          # Use all P-cores of i5 13th gen
        }
        
        self.timeout = 45  # 45s is plenty for qwen2.5:3b
        
    def generate(self, prompt: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate response from Ollama with performance tracking.
        
        Args:
            prompt: Input prompt (keep under 200 words for speed)
            options: Override default options if needed
            
        Returns:
            Dict with 'response', 'generation_time', and 'model'
        """
        start_time = time.time()
        
        # Merge custom options with defaults
        request_options = {**self.default_options}
        if options:
            request_options.update(options)
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,  # Batch response is faster for this use case
                    'format': 'json',  # Force valid JSON output - faster + no truncation
                    'options': request_options
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            elapsed = time.time() - start_time
            
            return {
                'response': result.get('response', ''),
                'generation_time': round(elapsed, 2),
                'model': self.model,
                'success': True
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
    
    def warm_up(self) -> Dict[str, Any]:
        """
        Pre-load model into RAM so first real request is fast.
        Call this at app startup to eliminate cold-start latency.
        """
        print(f"🔥 Warming up model: {self.model}...")
        start = time.time()
        try:
            # Send a tiny request to force model loading
            response = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'prompt': 'Hi',
                    'stream': False,
                    'options': {'num_predict': 1}  # Generate just 1 token
                },
                timeout=120  # Model loading can take time first time
            )
            response.raise_for_status()
            elapsed = time.time() - start
            print(f"✅ Model warmed up in {elapsed:.1f}s - subsequent requests will be FAST")
            return {'success': True, 'warm_up_time': round(elapsed, 1)}
        except Exception as e:
            elapsed = time.time() - start
            print(f"⚠️ Warm-up failed ({elapsed:.1f}s): {e}")
            return {'success': False, 'error': str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            model_available = any(m.get('name', '').startswith(self.model) for m in models)
            
            return {
                'ollama_connected': True,
                'model': self.model,
                'model_available': model_available,
                'status': 'healthy' if model_available else 'model_not_found'
            }
        except:
            return {
                'ollama_connected': False,
                'model': self.model,
                'model_available': False,
                'status': 'unhealthy'
            }

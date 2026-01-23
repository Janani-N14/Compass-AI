"""LLM Service - Groq only"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from backend.app.config import config

# Try importing Groq directly
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class LLMService:
    """LLM service using Groq only"""
    
    def __init__(self):
        # Validate config
        config.validate()
        
        self.model = config.MODEL_NAME
        self.temperature = config.TEMPERATURE
        self.max_tokens = config.MAX_TOKENS
        
        # Initialize Groq
        if not GROQ_AVAILABLE:
            raise ImportError("Groq SDK not installed. Run: pip install groq")
        
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required in .env file")
        
        try:
            # Extract model name (remove provider prefix if present)
            model_name = self.model.replace("openai/", "").replace("groq/", "")
            # Use a valid Groq model if the extracted one doesn't work
            if model_name == "gpt-oss-20b" or "llama-3.1-70b" in model_name:
                model_name = "llama-3.3-70b-versatile"  # Fallback to current model
            self.groq_client = Groq(api_key=config.GROQ_API_KEY)
            self.model_name = model_name
        except Exception as e:
            raise ValueError(f"Failed to initialize Groq: {e}")
    
    def create_completion(self, prompt: str, temperature: float = None, stream: bool = False):
        """Create a chat completion using Groq SDK"""
        if not hasattr(self, 'groq_client'):
            raise ValueError("Groq client not initialized. Check API key.")
        
        temp = temperature if temperature is not None else self.temperature
        messages = [{"role": "user", "content": prompt}]
        
        if stream:
            return self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temp,
                max_tokens=self.max_tokens,
                stream=True
            )
        else:
            return self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temp,
                max_tokens=self.max_tokens
            )
    
    def get_response_text(self, completion, stream: bool = False):
        """Extract response text from completion"""
        if stream:
            # For streaming responses
            if hasattr(completion, '__iter__'):
                # It's a generator/iterator
                full_text = ""
                for chunk in completion:
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            full_text += delta.content
                return full_text
            else:
                return str(completion)
        else:
            # For non-streaming responses
            if hasattr(completion, 'choices') and len(completion.choices) > 0:
                return completion.choices[0].message.content
            elif hasattr(completion, 'content'):
                return completion.content
            elif isinstance(completion, str):
                return completion
            else:
                return str(completion)

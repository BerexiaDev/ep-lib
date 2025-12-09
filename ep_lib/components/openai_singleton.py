from flask import current_app
from openai import OpenAI
from typing import Optional, List, Dict, Any

class OpenAISingleton:
    _instance: Optional['OpenAISingleton'] = None
    _client: Optional[OpenAI] = None
    _embedding_model: str = "text-embedding-3-small"
    _chat_model: str = "gpt-4.1-nano"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAISingleton, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_client(cls) -> OpenAI:
        if cls._client is None:
            api_key = current_app.config.get("OPENAI_KEY")
            if not api_key:
                raise ValueError("OPENAI_KEY not found in Flask configuration")
            cls._client = OpenAI(api_key=api_key)
        return cls._client

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        client = cls.get_client()
        response = client.embeddings.create(
            input=[text],
            model=cls._embedding_model
        )
        return response.data[0].embedding

    @classmethod
    def get_embeddings(cls, texts: List[str]) -> List[List[float]]:
        client = cls.get_client()
        response = client.embeddings.create(
            input=texts,
            model=cls._embedding_model
        )
        return [item.embedding for item in response.data]

    @classmethod
    def chat_completion(cls, messages: List[Dict[str, str]], options: Dict[str, Any] = None) -> str:
        if options is None:
            options = {}
            
        chat_model = options.get("model", cls._chat_model)
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", None)
        response_format = options.get("response_format", None)
        
        client = cls.get_client()
        
        # Build completion parameters dynamically
        completion_params = {
            "model": chat_model,
            "messages": messages
        }
        
        # Only add temperature if it's not None (some models don't support it)
        if temperature is not None:
            completion_params["temperature"] = temperature
            
        # Only add max_tokens if it's specified
        if max_tokens is not None:
            completion_params["max_tokens"] = max_tokens
        
        # Only add response_format if it's specified
        if response_format is not None:
            completion_params["response_format"] = response_format
        
        completion = client.chat.completions.create(**completion_params)
        
        return completion.choices[0].message.content
    
    @classmethod
    def set_embedding_model(cls, model_name: str) -> None:
        cls._embedding_model = model_name 
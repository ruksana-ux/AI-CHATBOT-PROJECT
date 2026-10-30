"""LLM Engine for loading models via Ollama or Hugging Face Transformers.
No LangChain is used.
"""
import os
import json
import socket
import requests
from typing import List, Dict, Any, Optional


class OllamaModel:
    """Wrapper for models running through Ollama."""

    def __init__(self, model_name: str = "llama3.2", host: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.host = host

    def is_available(self) -> bool:
        """Fast socket check if local Ollama daemon port is listening."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            port = 11434
            host = "127.0.0.1"
            clean_host = self.host.replace("http://", "").replace("https://", "")
            if ":" in clean_host:
                parts = clean_host.split(":")
                host = parts[0]
                port = int(parts[1])
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            return False

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """Generate response using Ollama."""
        if not self.is_available():
            raise ConnectionError(f"Ollama daemon is not reachable at {self.host}.")

        # Try python package if available
        try:
            import ollama
            client = ollama.Client(host=self.host, timeout=30)
            response = client.chat(
                model=self.model_name,
                messages=messages,
                options={"temperature": temperature}
            )
            return response["message"]["content"]
        except Exception:
            pass

        # Direct HTTP API call
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]


class HuggingFaceTransformersModel:
    """Wrapper for Hugging Face Transformers models (local pipeline or HF Inference Client)."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.2-3B-Instruct",
        use_local_pipeline: bool = False,
        hf_token: Optional[str] = None
    ):
        self.model_name = model_name
        self.use_local_pipeline = use_local_pipeline
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.pipe = None

        if self.use_local_pipeline:
            try:
                from transformers import pipeline
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model_name,
                    max_new_tokens=512,
                    temperature=0.3
                )
            except Exception as e:
                print(f"[HuggingFaceEngine] Note: Local pipeline not loaded ({e})")
                self.pipe = None

    def is_available(self) -> bool:
        if self.use_local_pipeline:
            return self.pipe is not None
        return bool(self.hf_token)

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """Generate response using Hugging Face Transformers or InferenceClient."""
        # 1. Local Transformers Pipeline
        if self.use_local_pipeline and self.pipe is not None:
            prompt = self.pipe.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            outputs = self.pipe(
                prompt,
                max_new_tokens=512,
                do_sample=temperature > 0,
                temperature=temperature or 0.1
            )
            generated_text = outputs[0]["generated_text"]
            if prompt in generated_text:
                return generated_text.replace(prompt, "").strip()
            return generated_text.strip()

        # 2. Hugging Face InferenceClient
        if not self.hf_token:
            raise ValueError("HF_TOKEN is required to query Hugging Face models via InferenceClient.")

        from huggingface_hub import InferenceClient
        client = InferenceClient(token=self.hf_token)
        response = client.chat_completion(
            messages=messages,
            model=self.model_name,
            max_tokens=512,
            temperature=temperature or 0.1
        )
        return response.choices[0].message.content


def get_llm():
    """
    Factory function to instantiate the selected LLM based on environment variables:
    LLM_PROVIDER: 'ollama' (default) or 'huggingface'
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

    if provider == "huggingface":
        model_name = os.getenv("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
        use_local = os.getenv("HF_USE_LOCAL", "false").lower() == "true"
        return HuggingFaceTransformersModel(
            model_name=model_name,
            use_local_pipeline=use_local,
            hf_token=os.getenv("HF_TOKEN")
        )
    else:
        model_name = os.getenv("OLLAMA_MODEL", "llama3.2")
        host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        return OllamaModel(model_name=model_name, host=host)

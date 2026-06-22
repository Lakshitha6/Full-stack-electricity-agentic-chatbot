import os
import httpx
from typing import Optional , Dict, Any
from src.utils.config_loader import load_yaml, get_env


class LLMRouter:
    def __init__(self):
        self.config = load_yaml("llm.yaml")
        self.settings = self.config["settings"]


    async def chat_completion(self, prompt: str, system_prompt: str = "") -> str:
        """Try primary provider (gemini), fallback to groq if error."""

        primary = self.config["providers"]["primary"]
        fallback = self.config["providers"]["fallback"]

        try:
            return await self._call_provider(primary, prompt, system_prompt)

        except Exception as e:
            if self.settings["fallback_on_error"] and self._is_fallback_error(e):
                print(f"{primary['name']} failed ({type(e).__name__}), falling back to {fallback['name']}")
                return await self._call_provider(fallback, prompt, system_prompt)
            raise

    
    async def _call_provider(self, provider: Dict, prompt: str, system_prompt: str) -> str:
        
        provider_name = provider["name"]
        api_key = get_env(provider["api_key_env"])

        if not api_key:
            raise ValueError(f"API key not set: {provider['api_key_env']}")
        
        print(f" Calling {provider_name}...")

        if provider["name"] == "gemini":
            return await self._call_gemini(api_key, provider["model"], prompt, system_prompt, provider)
        elif provider["name"] == "groq":
            return await self._call_groq(api_key, provider["model"], prompt, system_prompt, provider)
        else:
            raise ValueError(f"Unknown provider: {provider['name']}")



    async def _call_gemini(self, api_key: str, model: str, prompt: str, system_prompt: str, config: Dict) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": self.settings["max_tokens"],
                "temperature": self.settings["temperature"]
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }


        async with httpx.AsyncClient(timeout=config["timeout"]) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    async def _call_groq(self, api_key: str, model: str, prompt: str, system_prompt: str, config: Dict) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.settings["max_tokens"],
            "temperature": self.settings["temperature"]
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=config["timeout"]) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    
    def _is_fallback_error(self, error: Exception) -> bool:
        fallback_codes = self.settings.get("fallback_errors", [429, 500, 503])
        if hasattr(error, "response") and hasattr(error.response, "status_code"):
            return error.response.status_code in fallback_codes
        return isinstance(error, (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException))


llm_router = LLMRouter()
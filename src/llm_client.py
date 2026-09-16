import json
import logging
import re
from typing import List, Dict, Any, Optional
from groq import Groq
from openai import OpenAI

from src.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    NVIDIA_API_KEY,
    NVIDIA_MODEL,
    NVIDIA_BASE_URL,
)

logger = logging.getLogger("growpido.llm_client")

class UnifiedLLMClient:
    """
    Unified LLM Client providing seamless, zero-latency failover from Groq to NVIDIA.
    - Primary: Groq (high-speed inference with guarded max_tokens to respect OTPM limits)
    - Fallback: NVIDIA Integrate API (nvidia/nemotron-3.5-lightning-30b-a3b)
    """

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None,
        nvidia_api_key: Optional[str] = None,
        nvidia_model: Optional[str] = None,
    ):
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.groq_model = groq_model or GROQ_MODEL
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None

        self.nvidia_api_key = nvidia_api_key or NVIDIA_API_KEY
        self.nvidia_model = nvidia_model or NVIDIA_MODEL
        self.nvidia_client = (
            OpenAI(base_url=NVIDIA_BASE_URL, api_key=self.nvidia_api_key, timeout=60.0)
            if self.nvidia_api_key
            else None
        )

        self.last_provider_used = "groq"

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 800,
        temperature: float = 0.1,
        json_mode: bool = False,
    ) -> str:
        """
        Executes chat completion with automatic Groq -> NVIDIA failover on any rate limit or API error.
        """
        # 1. Attempt Groq Primary
        if self.groq_client:
            try:
                kwargs: Dict[str, Any] = {
                    "model": self.groq_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self.groq_client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content or ""
                self.last_provider_used = "groq"
                return content.strip()

            except Exception as e:
                logger.warning(
                    f"[LLM Failover] Groq call failed with {type(e).__name__}: {e}. "
                    f"Failing over to NVIDIA ({self.nvidia_model})..."
                )

        # 2. Fallback to NVIDIA API (Lightning fast ~1.1s with enable_thinking=False)
        if self.nvidia_client:
            try:
                extra_body = {"chat_template_kwargs": {"enable_thinking": False}}
                nv_kwargs: Dict[str, Any] = {
                    "model": self.nvidia_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "extra_body": extra_body,
                }
                response = self.nvidia_client.chat.completions.create(**nv_kwargs)
                content = response.choices[0].message.content or ""
                self.last_provider_used = "nvidia"
                return content.strip()
            except Exception as nv_err:
                logger.error(f"[LLM Failover] NVIDIA fallback call also failed: {nv_err}")
                raise RuntimeError(
                    f"Both Groq and NVIDIA LLM providers failed. NVIDIA error: {nv_err}"
                )

        raise RuntimeError("No LLM client configured (neither Groq nor NVIDIA).")

    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 800,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Executes chat completion and parses response strictly as JSON with fallback and sanitization.
        """
        raw = self.chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True,
        )

        # Clean markdown code blocks if present (e.g. ```json ... ```)
        cleaned = raw
        if "```" in cleaned:
            # Extract content between code fences
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try finding first { and last }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise

# Global singleton client instance
llm_client = UnifiedLLMClient()

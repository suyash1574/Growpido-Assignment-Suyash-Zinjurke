import os
import json
import logging
import re
import time
import platform
from typing import List, Dict, Any, Optional

# Prevent Windows WMI query hang/leak (0x8007000e) during SDK client header generation
try:
    platform.platform = lambda *args, **kwargs: "Windows-10"
    platform.processor = lambda *args, **kwargs: "Intel64"
except Exception:
    pass

from groq import Groq
from openai import OpenAI

from src.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    NVIDIA_API_KEY,
    NVIDIA_MODEL,
    NVIDIA_BASE_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL_1,
    OPENROUTER_MODEL_2,
    OPENROUTER_MODEL_3,
    LOCAL_LLM_CONTEXT_WINDOW,
    LOCAL_LLM_GPU_LAYERS,
    LOCAL_LLM_MODEL_PATH,
)

logger = logging.getLogger("growpido.llm_client")

class UnifiedLLMClient:
    """
    Intelligent Latency- & Availability-Aware LLM Router.
    Priority Execution Order:
      1. Primary: Groq (Ultra-low latency, sub-second inference)
      2. Secondary: NVIDIA NIM (Dedicated enterprise inference)
      3. Tertiary Fallback: OpenRouter (Community / free models if primary engines are unavailable)
      4. Final Fallback: Local GGUF model through llama-cpp-python
    
    Features:
      - Automatic circuit breaking & cooldown on rate limit or timeout
      - Real-time latency monitoring
      - Dynamic speed & availability health check
    """

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None,
        nvidia_api_key: Optional[str] = None,
        nvidia_model: Optional[str] = None,
        local_model_path: Optional[str] = None,
    ):
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.groq_model = groq_model or GROQ_MODEL
        self.groq_client = (
            Groq(api_key=self.groq_api_key, max_retries=1, timeout=20.0)
            if self.groq_api_key
            else None
        )

        self.nvidia_api_key = nvidia_api_key or NVIDIA_API_KEY
        self.nvidia_model = nvidia_model or NVIDIA_MODEL
        self.nvidia_client = (
            OpenAI(base_url=NVIDIA_BASE_URL, api_key=self.nvidia_api_key, max_retries=1, timeout=25.0)
            if self.nvidia_api_key
            else None
        )

        self.openrouter_api_key = OPENROUTER_API_KEY
        self.openrouter_client = (
            OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.openrouter_api_key, max_retries=0, timeout=25.0)
            if self.openrouter_api_key
            else None
        )
        self.openrouter_models = [m for m in [OPENROUTER_MODEL_1, OPENROUTER_MODEL_2, OPENROUTER_MODEL_3] if m]

        # Explicit provider override from env (defaults to 'groq')
        self.preferred_provider = (os.getenv("LLM_PROVIDER", "groq") or "groq").lower()

        # Delay the GGUF load until it is needed so normal dashboard start-up
        # remains fast while offline analysis still has a real fallback.
        self.local_llm = None
        self.local_model_path = local_model_path or LOCAL_LLM_MODEL_PATH
        self.local_context_window = LOCAL_LLM_CONTEXT_WINDOW
        self.local_gpu_layers = LOCAL_LLM_GPU_LAYERS

        # Circuit breaker cooldown timestamps (unix epoch seconds)
        self._cooldowns: Dict[str, float] = {
            "groq": 0.0,
            "nvidia": 0.0,
            "openrouter": 0.0,
            "local_gguf": 0.0,
        }

        # Track last measured latency in milliseconds
        self.last_latency_ms: Dict[str, float] = {}
        self.last_provider_used: str = "none"

    def is_provider_available(self, provider: str) -> bool:
        """Checks if provider has credentials configured and is not currently on cooldown."""
        now = time.time()
        if now < self._cooldowns.get(provider, 0.0):
            return False

        if provider == "groq":
            return bool(self.groq_client)
        elif provider == "nvidia":
            return bool(self.nvidia_client)
        elif provider == "openrouter":
            return bool(self.openrouter_client and self.openrouter_models)
        elif provider == "local_gguf":
            return os.path.exists(self.local_model_path)
        return False

    def mark_cooldown(self, provider: str, duration_seconds: float = 60.0):
        """Places a failing or timed-out provider on temporary cooldown."""
        self._cooldowns[provider] = time.time() + duration_seconds
        logger.warning(f"[LLM Router] Marked {provider.upper()} on cooldown for {duration_seconds}s.")

    def clear_cooldown(self, provider: str):
        """Clears cooldown on success."""
        self._cooldowns[provider] = 0.0

    def ping_provider(self, provider: str) -> Dict[str, Any]:
        """Pings a specific provider with a tiny prompt to verify real-time status and latency."""
        messages = [{"role": "user", "content": "ping"}]
        t0 = time.time()
        try:
            if provider == "groq" and self.groq_client:
                self._call_groq(messages, max_tokens=10, temperature=0.1, json_mode=False)
            elif provider == "nvidia" and self.nvidia_client:
                self._call_nvidia(messages, max_tokens=10, temperature=0.1)
            elif provider == "openrouter" and self.openrouter_client:
                self._call_openrouter(messages, max_tokens=10, temperature=0.1)
            elif provider == "local_gguf" and self.is_provider_available(provider):
                self._call_local_gguf(messages, max_tokens=10, temperature=0.1, json_mode=False)
            else:
                return {"provider": provider, "status": "NOT_CONFIGURED", "latency_ms": None}
            
            latency = round((time.time() - t0) * 1000, 1)
            self.last_latency_ms[provider] = latency
            self.clear_cooldown(provider)
            return {"provider": provider, "status": "UP", "latency_ms": latency}
        except Exception as err:
            latency = round((time.time() - t0) * 1000, 1)
            return {"provider": provider, "status": "DOWN", "error": str(err), "latency_ms": latency}

    def check_all_providers_health(self) -> Dict[str, Any]:
        """Evaluates health and latency of all configured engines."""
        results = {}
        for p in ["groq", "nvidia", "openrouter", "local_gguf"]:
            results[p] = self.ping_provider(p)
            status = results[p]["status"]
            lat = results[p].get("latency_ms")
            logger.info(f"[LLM Health Check] {p.upper()}: {status} ({lat}ms)")
        return results

    def _call_groq(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float, json_mode: bool) -> str:
        models_to_try = [self.groq_model]
        for fallback_m in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        last_err = None
        for m in models_to_try:
            t0 = time.time()
            kwargs: Dict[str, Any] = {
                "model": m,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            try:
                response = self.groq_client.chat.completions.create(**kwargs)
                msg = response.choices[0].message
                content = (msg.content or "").strip()
                if not content:
                    reasoning = getattr(msg, "reasoning", None) or getattr(msg, "reasoning_content", None)
                    if reasoning and ("{" in reasoning or "[" in reasoning):
                        content = reasoning.strip()
                if not content:
                    continue
                elapsed = round((time.time() - t0) * 1000, 1)
                self.last_latency_ms["groq"] = elapsed
                self.last_provider_used = f"groq ({m}, {elapsed}ms)"
                self.clear_cooldown("groq")
                return content
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                if "rate limit" in err_str or "429" in err_str:
                    logger.warning(f"[Groq Model Failover] Model {m} hit rate limit. Trying alternate Groq model...")
                    continue
                raise e
        raise last_err or ValueError("Groq returned empty completion content.")

    def _call_nvidia(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        t0 = time.time()
        extra_body = {"chat_template_kwargs": {"enable_thinking": False}}
        nv_kwargs: Dict[str, Any] = {
            "model": self.nvidia_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "extra_body": extra_body,
        }
        response = self.nvidia_client.chat.completions.create(**nv_kwargs)
        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise ValueError("NVIDIA returned empty completion content.")
        elapsed = round((time.time() - t0) * 1000, 1)
        self.last_latency_ms["nvidia"] = elapsed
        self.last_provider_used = f"nvidia ({self.nvidia_model}, {elapsed}ms)"
        self.clear_cooldown("nvidia")
        return content

    def _call_openrouter(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        last_err = None
        for model in self.openrouter_models:
            if not model:
                continue
            t0 = time.time()
            or_kwargs: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            try:
                response = self.openrouter_client.chat.completions.create(**or_kwargs)
                content = (response.choices[0].message.content or "").strip()
                if not content:
                    raise ValueError(f"OpenRouter model {model} returned empty completion content.")
                elapsed = round((time.time() - t0) * 1000, 1)
                self.last_latency_ms["openrouter"] = elapsed
                self.last_provider_used = f"openrouter ({model}, {elapsed}ms)"
                self.clear_cooldown("openrouter")
                return content
            except Exception as e:
                logger.warning(f"[OpenRouter Retry] Model {model} failed: {e}")
                last_err = e

        raise last_err or RuntimeError("All OpenRouter fallback models failed.")

    def _call_local_gguf(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> str:
        """Run the configured GGUF model locally, loading it only on first use."""
        if not os.path.isfile(self.local_model_path):
            raise FileNotFoundError(f"Local GGUF model not found: {self.local_model_path}")

        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError(
                "Local GGUF fallback requires llama-cpp-python. Install it with "
                "`pip install llama-cpp-python`."
            ) from exc

        if self.local_llm is None:
            logger.info("[LLM Router] Loading local GGUF fallback from %s", self.local_model_path)
            self.local_llm = Llama(
                model_path=self.local_model_path,
                n_ctx=self.local_context_window,
                n_gpu_layers=self.local_gpu_layers,
                verbose=False,
            )

        t0 = time.time()
        kwargs: Dict[str, Any] = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.local_llm.create_chat_completion(**kwargs)
        content = (response["choices"][0]["message"].get("content") or "").strip()
        if not content:
            raise ValueError("Local GGUF model returned empty completion content.")

        elapsed = round((time.time() - t0) * 1000, 1)
        self.last_latency_ms["local_gguf"] = elapsed
        self.last_provider_used = f"local_gguf ({os.path.basename(self.local_model_path)}, {elapsed}ms)"
        self.clear_cooldown("local_gguf")
        return content

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 800,
        temperature: float = 0.1,
        json_mode: bool = False,
    ) -> str:
        """
        Executes chat completion adhering to strict speed & availability hierarchy:
          1. Groq (Fastest, ~200-800ms)
          2. NVIDIA NIM (Dedicated accelerator)
          3. OpenRouter (Tertiary fallback)
          4. Local GGUF (final offline fallback)
        """
        prepared_messages = list(messages)
        if json_mode:
            strict_json_prompt = (
                "You are a JSON-only API. You must strictly respond with a valid JSON object. "
                "Do NOT output any thinking process, reasoning, or preamble. Your output must start with '{' and end with '}'."
            )
            if not any(m.get("role") == "system" for m in prepared_messages):
                prepared_messages.insert(0, {"role": "system", "content": strict_json_prompt})
            elif not any("json" in m.get("content", "").lower() for m in prepared_messages if m.get("role") == "system"):
                orig_sys = prepared_messages[0]["content"]
                prepared_messages[0] = {"role": "system", "content": f"{orig_sys}\n{strict_json_prompt}"}

        # Build candidate provider order based on availability & preference
        # Default speed hierarchy: Groq -> NVIDIA -> OpenRouter -> local GGUF
        hierarchy = ["groq", "nvidia", "openrouter", "local_gguf"]
        if self.preferred_provider == "nvidia":
            hierarchy = ["nvidia", "groq", "openrouter", "local_gguf"]
        elif self.preferred_provider == "openrouter":
            # If user explicitly forced openrouter in env, still keep fast failover
            hierarchy = ["openrouter", "groq", "nvidia", "local_gguf"]
        elif self.preferred_provider in {"local", "local_gguf", "gguf"}:
            hierarchy = ["local_gguf", "groq", "nvidia", "openrouter"]

        errors = []

        for provider in hierarchy:
            # Check availability (credentials exist and not on cooldown)
            if not self.is_provider_available(provider):
                cooldown_left = max(0, int(self._cooldowns.get(provider, 0) - time.time()))
                if cooldown_left > 0:
                    logger.info(f"[LLM Router] Skipping {provider.upper()} (on cooldown for another {cooldown_left}s).")
                continue

            try:
                if provider == "groq":
                    try:
                        return self._call_groq(prepared_messages, max_tokens, temperature, json_mode)
                    except Exception as g_err:
                        err_str = str(g_err).lower()
                        # If Groq schema validation fails, instantly retry Groq once without json_mode
                        if "json_validate_failed" in err_str and json_mode:
                            logger.info("[LLM Router] Retrying Groq without strict json_mode...")
                            return self._call_groq(prepared_messages, max_tokens, temperature, json_mode=False)
                        # If Groq rate limit provides a short wait time, sleep and retry once
                        if "rate limit" in err_str or "429" in err_str:
                            match = re.search(r'try again in ([\d\.]+)s', str(g_err))
                            wait_s = float(match.group(1)) if match else 10.0
                            if wait_s <= 25.0:
                                logger.info(f"[LLM Router] Groq TPM limit hit. Waiting {wait_s + 0.5:.1f}s before retry...")
                                time.sleep(wait_s + 0.5)
                                return self._call_groq(prepared_messages, max_tokens, temperature, json_mode)
                        raise g_err

                elif provider == "nvidia":
                    return self._call_nvidia(prepared_messages, max_tokens, temperature)

                elif provider == "openrouter":
                    return self._call_openrouter(prepared_messages, max_tokens, temperature)

                elif provider == "local_gguf":
                    return self._call_local_gguf(prepared_messages, max_tokens, temperature, json_mode)

            except Exception as exc:
                err_msg = str(exc).lower()
                # If rate limit / quota or timeout hit, place on cooldown
                if "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg or "tokens per day" in err_msg or "timed out" in err_msg:
                    self.mark_cooldown(provider, duration_seconds=60.0)
                else:
                    self.mark_cooldown(provider, duration_seconds=15.0)

                errors.append(f"{provider}: {exc}")
                logger.warning(f"[LLM Failover] {provider.upper()} failed: {exc}. Failing over to next fastest engine...")

        raise RuntimeError(f"All LLM providers failed or timed out. Details: {'; '.join(errors)}")

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

        cleaned = raw
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    sub = cleaned[start : end + 1]
                    sub_fixed = re.sub(r',\s*([\]}])', r'\1', sub)
                    try:
                        return json.loads(sub_fixed)
                    except Exception:
                        pass

            if '"claims"' in cleaned:
                claim_matches = re.findall(r'\{\s*"claim_text":\s*"([^"]+)",\s*"category":\s*"([^"]+)"\s*\}', cleaned)
                if claim_matches:
                    return {"claims": [{"claim_text": m[0], "category": m[1]} for m in claim_matches]}
            logger.error(f"[LLM JSON Error] Could not decode JSON. Raw string: {repr(raw)}")
            return {}

# Global singleton client instance
llm_client = UnifiedLLMClient()

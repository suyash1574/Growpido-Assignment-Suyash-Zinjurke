from src.llm_client import UnifiedLLMClient


def test_uses_local_gguf_after_remote_failover(monkeypatch, tmp_path):
    """The GGUF fallback must be called after all remote providers fail."""
    model_path = tmp_path / "fallback.gguf"
    model_path.write_bytes(b"placeholder")
    client = UnifiedLLMClient(
        groq_api_key="test-key",
        nvidia_api_key="test-key",
        local_model_path=str(model_path),
    )
    client.openrouter_client = None

    def remote_failure(*args, **kwargs):
        raise RuntimeError("remote unavailable")

    monkeypatch.setattr(client, "_call_groq", remote_failure)
    monkeypatch.setattr(client, "_call_nvidia", remote_failure)
    monkeypatch.setattr(client, "_call_local_gguf", lambda *args, **kwargs: "local response")

    assert client.chat_completion([{"role": "user", "content": "hello"}]) == "local response"


def test_local_provider_can_be_preferred(monkeypatch, tmp_path):
    model_path = tmp_path / "fallback.gguf"
    model_path.write_bytes(b"placeholder")
    client = UnifiedLLMClient(local_model_path=str(model_path))
    client.preferred_provider = "local_gguf"
    monkeypatch.setattr(client, "_call_local_gguf", lambda *args, **kwargs: "offline response")

    assert client.chat_completion([{"role": "user", "content": "hello"}]) == "offline response"

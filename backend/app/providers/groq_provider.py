import time
from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class ProviderResult:
    text: str | None
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    error: str | None = None


def generate(prompt: str, model: str, temperature: float = 0.0, timeout: float = 30.0) -> ProviderResult:
    if not settings.groq_api_key:
        return ProviderResult(None, 0.0, error="GROQ_API_KEY is not configured")

    start = time.perf_counter()
    try:
        r = httpx.post(
            f"{settings.groq_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            },
            timeout=timeout,
        )
        latency = (time.perf_counter() - start) * 1000
        if r.status_code == 429:
            return ProviderResult(None, latency, error="rate_limited")
        if r.status_code in (401, 403):
            return ProviderResult(None, latency, error="authentication_failed")
        if r.status_code >= 400:
            return ProviderResult(None, latency, error=f"http_{r.status_code}: {r.text[:200]}")
        data = r.json()
        usage = data.get("usage", {})
        return ProviderResult(
            text=data["choices"][0]["message"]["content"].strip(),
            latency_ms=latency,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )
    except httpx.TimeoutException:
        return ProviderResult(None, (time.perf_counter() - start) * 1000, error="timeout")
    except Exception as e:  # malformed response, network error, etc.
        return ProviderResult(None, (time.perf_counter() - start) * 1000, error=f"provider_error: {type(e).__name__}")
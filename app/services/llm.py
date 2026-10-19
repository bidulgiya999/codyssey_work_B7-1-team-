"""Single server-side Groq Chat Completions request; no implicit retries."""

import httpx


class AITimeoutError(Exception):
    """The upstream service did not answer before the configured deadline."""


class AIServiceError(Exception):
    """The upstream service could not provide a usable answer."""


class AIRateLimitError(AIServiceError):
    """Groq returned HTTP 429; the caller should wait before retrying."""


AIError = AIServiceError


async def ask_llm(system: str, messages: list[dict]) -> str:
    """Send one request. Never expose the provider key to the browser."""
    from app.config import settings

    key = settings.GROQ_API_KEY.strip()
    if not key:
        raise AIServiceError("GROQ_API_KEY is not configured")

    model = settings.GROQ_MODEL.strip()
    base_url = settings.GROQ_BASE_URL.rstrip("/")
    try:
        timeout = float(settings.GROQ_TIMEOUT_SECONDS)
        if timeout <= 0:
            raise ValueError
    except ValueError as exc:
        raise AIServiceError("GROQ_TIMEOUT_SECONDS must be positive") from exc
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, *messages],
        "max_completion_tokens": settings.GROQ_MAX_COMPLETION_TOKENS,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json=payload,
            )
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise AITimeoutError from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise AIRateLimitError("Groq rate limit") from None
        raise AIServiceError("AI request failed") from None
    except httpx.HTTPError as exc:
        raise AIServiceError("AI request failed") from exc

    try:
        choice = response.json()["choices"][0]
        if choice.get("finish_reason") == "length":
            raise AIServiceError("AI response was truncated")
        answer = choice["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
        raise AIServiceError("AI response has an unexpected shape") from exc
    if not isinstance(answer, str) or not answer.strip():
        raise AIServiceError("AI response is empty")
    return answer.strip()

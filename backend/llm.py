import os
import json
from anthropic import Anthropic
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException

MODEL_DEFAULT = "claude-sonnet-4-6"
MODEL_AWARD = "claude-opus-4-8"
USE_OPUS_FOR_AWARD = False


def _client() -> Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured on server")
    return Anthropic(api_key=key)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:]
    return text.strip()


def call_claude(system: str, user: str, schema: type[BaseModel] | None = None,
                model: str = MODEL_DEFAULT, max_tokens: int = 2000):
    client = _client()
    sys_prompt = system
    if schema is not None:
        sys_prompt += ("\n\nReturn ONLY valid JSON matching this schema. "
                       "No markdown, no commentary:\n" + json.dumps(schema.model_json_schema()))

    def _send(messages):
        resp = client.messages.create(model=model, max_tokens=max_tokens,
                                      system=sys_prompt, messages=messages)
        return "".join(b.text for b in resp.content if b.type == "text")

    try:
        raw = _send([{"role": "user", "content": user}])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e}")

    if schema is None:
        return raw

    try:
        return schema.model_validate_json(_strip_fences(raw))
    except (ValidationError, ValueError):
        try:
            retry = _send([
                {"role": "user", "content": user},
                {"role": "assistant", "content": raw},
                {"role": "user", "content": "That was not valid JSON for the schema. Return ONLY the JSON object."},
            ])
            return schema.model_validate_json(_strip_fences(retry))
        except (ValidationError, ValueError) as e:
            raise HTTPException(status_code=422, detail=f"Could not parse structured response: {e}")

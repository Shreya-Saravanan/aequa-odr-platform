import os
import json
import anthropic
import streamlit as st
from pydantic import BaseModel, ValidationError

MODEL_DEFAULT = "claude-sonnet-4-6"
MODEL_AWARD = "claude-opus-4-8"
USE_OPUS_FOR_AWARD = False  # flip True only if you have credits to spare


def _client() -> anthropic.Anthropic:
    key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY"))
    if not key:
        st.error("No ANTHROPIC_API_KEY found in st.secrets or environment.")
        st.stop()
    return anthropic.Anthropic(api_key=key)


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
    """Returns str if schema is None, a validated schema instance if schema given, or None on failure."""
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
        st.error(f"Claude API error: {e}")
        return None

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
            st.error(f"Could not parse a valid structured response: {e}")
            return None

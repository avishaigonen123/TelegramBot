import logging
import time

import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
REQUEST_TIMEOUT = 30

# Ordered fallback chain of OpenRouter free-tier models. Free-model availability on
# OpenRouter shifts over time (verified live against GET /api/v1/models on 2026-08-10 --
# several previously-listed slugs, e.g. deepseek/deepseek-chat:free, had already been
# retired). Re-check https://openrouter.ai/models?max_price=0 periodically and update
# this list if a model gets deprecated or removed.
MODEL_FALLBACK_CHAIN = [
    "openai/gpt-oss-20b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-nano-9b-v2:free",
]

SYSTEM_PROMPT = (
    "You are a precise Arabic-to-Hebrew translator for a Telegram news channel. "
    "Translate the user's Arabic text into natural Hebrew. "
    "Preserve line breaks, emoji, and formatting exactly as in the original. "
    "Output ONLY the Hebrew translation -- no commentary, no notes, no quotation marks around it."
)

UNAVAILABLE_PREFIX = "⚠️ תרגום לא זמין:\n\n"


def _call_model(model, api_key, text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    }
    response = requests.post(API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    if response.status_code in (401, 403):
        raise PermissionError(f"key rejected ({response.status_code})")
    raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")


def translate_arabic_to_hebrew(text, api_keys):
    """
    Try each model in MODEL_FALLBACK_CHAIN, and for each model try each api key,
    with one bounded retry on transient errors. Returns (translated_text, model_used)
    on success, or (None, None) if every combination failed.
    """
    for model in MODEL_FALLBACK_CHAIN:
        for api_key in api_keys:
            for attempt in (1, 2):
                try:
                    result = _call_model(model, api_key, text)
                    if result:
                        return result, model
                    raise RuntimeError("empty response")
                except PermissionError as e:
                    logging.warning(f"[{model}] key rejected, skipping to next key: {e}")
                    break
                except Exception as e:
                    logging.warning(f"[{model}] attempt {attempt} failed: {e}")
                    if attempt == 1:
                        time.sleep(2)
                        continue
                    break
    logging.error("All models/keys exhausted; translation failed.")
    return None, None


def translate_or_fallback(text, api_keys):
    """
    Returns text ready to send: the Hebrew translation, or the original Arabic
    prefixed with an "unavailable" notice if every model/key failed.
    """
    translated, model = translate_arabic_to_hebrew(text, api_keys)
    if translated is not None:
        return translated
    return UNAVAILABLE_PREFIX + text

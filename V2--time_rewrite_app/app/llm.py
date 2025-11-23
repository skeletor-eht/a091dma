import json
import re
from typing import Optional

import httpx

from .config import settings
from .schemas import RewriteResponse

# ----------------- Drift config (tuned to be more forgiving) -----------------

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "by", "at", "from", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "into", "about",
    "regarding", "related", "re", "re:"
}

# Tokens we REALLY do not want silently dropped (crude safety guard)
MUST_PRESERVE_TOKENS = {"farts", "butt", "toilet", "poop", "nsfw"}

# How much overlap between original and rewritten content we require
# 0.30 = VERY forgiving (only huge semantic changes will trip it)
DRIFT_MIN_OVERLAP = 0.30


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"\b\w+\b", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _too_much_drift(original: str, rewritten: str) -> bool:
    """
    Returns True only if the rewrite looks *radically* different
    (very low overlap) OR if sensitive tokens were silently removed.

    This version is much more forgiving than the old one, so the
    model is trusted most of the time.
    """
    o_tokens = _tokenize(original)
    r_tokens = _tokenize(rewritten)

    o_set = set(o_tokens)
    r_set = set(r_tokens)

    if not o_set:
        # Nothing meaningful in the original, nothing to compare
        return False

    missing = o_set - r_set
    overlap_ratio = 1.0 - (len(missing) / len(o_set))

    # Only flag drift if overlap is extremely low
    if overlap_ratio < DRIFT_MIN_OVERLAP:
        return True

    # If we had any of our "must preserve" tokens originally and they vanished, be strict
    for t in o_set:
        if t in MUST_PRESERVE_TOKENS and t in missing:
            return True

    return False


# ----------------- System prompt -----------------

SYSTEM_PROMPT = """
You are an AI legal billing assistant for a law firm.

Your job is to REWRITE time entry narratives to:
- Improve clarity
- Match professional legal billing language
- Respect client billing guidelines

STRICT RULES:
- Do NOT change the number of hours.
- Do NOT add new tasks that were not clearly implied.
- Do NOT invent work or exaggerate.
- You may make the language more professional, but the substantive meaning must remain.

You MUST respond in JSON ONLY with this exact structure:

{
  "standard": "<cleaned version of the narrative>",
  "client_compliant": "<version tuned to client rules>",
  "audit_safe": "<version that is extra clear and defensible in audits>",
  "notes": "<brief explanation of what you changed and why>"
}

Do not include any explanation outside the JSON.
""".strip()


# ----------------- Fallback behavior -----------------

def _simple_fallback_rewrite(original: str) -> RewriteResponse:
    """
    Minimal "safe" rewrite used only when the LLM output is totally unusable.
    """
    text = original.strip() or "Performed legal services."
    text = text[0].upper() + text[1:]
    if not text.endswith("."):
        text += "."

    note = (
        "LLM rewrite was rejected due to potential semantic change or invalid output. "
        "Using a minimal cleaned version that preserves the original wording."
    )

    return RewriteResponse(
        standard=text,
        client_compliant=text,
        audit_safe=text,
        notes=note,
    )


def _extract_json(text: str) -> dict:
    """
    Try to parse the model output as JSON. If it wraps JSON in extra text,
    attempt to slice out the first {...} block.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        return json.loads(snippet)

    raise ValueError(f"Could not parse JSON from model output: {text!r}")


# ----------------- Main entrypoint -----------------

async def call_ollama(original: str, hours: float, rules: Optional[dict]) -> RewriteResponse:
    """
    Call Ollama (qwen2.5:7b by default) and return a validated RewriteResponse.

    - If LLM output is invalid JSON => fallback
    - If drift is *extreme* => fallback
    - Otherwise, trust the model's rewrite
    """
    rules = rules or {}
    user_prompt = f"""
Hours: {hours}
Original narrative: {original}

Client rules (JSON):
{json.dumps(rules, indent=2)}
""".strip()

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                settings.ollama_url,
                json={
                    "model": settings.model_name,
                    "prompt": SYSTEM_PROMPT + "\n\n" + user_prompt,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            raw_text = data.get("response", "")
    except Exception:
        # Network / Ollama error
        return _simple_fallback_rewrite(original)

    # Try to parse JSON from the model response
    try:
        parsed = _extract_json(raw_text)
    except Exception:
        return _simple_fallback_rewrite(original)

    # Validate the structure
    for key in ["standard", "client_compliant", "audit_safe"]:
        if key not in parsed or not isinstance(parsed[key], str):
            return _simple_fallback_rewrite(original)

    notes = parsed.get("notes", "")
    if not isinstance(notes, str):
        notes = str(notes)

    standard = parsed["standard"].strip()
    client_compliant = parsed["client_compliant"].strip()
    audit_safe = parsed["audit_safe"].strip()

    # Only reject when the change is extreme
    if _too_much_drift(original, standard):
        return _simple_fallback_rewrite(original)

    return RewriteResponse(
        standard=standard,
        client_compliant=client_compliant,
        audit_safe=audit_safe,
        notes=notes.strip(),
    )

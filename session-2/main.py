"""
Northstar Services — Support Assistant  (COURSE PROJECT)
========================================================

This is the course-long project. It GROWS across the whole course: each session adds a
capability the client asks for. Today (Session 2) is v0.

Run it:
    pip install google-genai python-dotenv pydantic pyyaml
    python main.py

Requires a `.env` file next to this file:
    GEMINI_API_KEY=...

Session 2 (v0): triage an incoming customer message, decide whether a human is needed, and
draft a first reply — using one LLM provider, *structured output*, well-built *system prompts*
(kept in prompt.yml), and *token-usage* tracking.
"""

# --- 1. Setup -----------------------------------------------------------------
# Purpose: load the API key from .env and create the LLM client.
# The client reads the key from the environment — never hard-code keys.
from dotenv import load_dotenv
load_dotenv()  # read .env into environment variables

from google import genai

client = genai.Client()              # reads GEMINI_API_KEY from the environment
MODEL = "gemini-3.1-flash-lite"      # one place to change the provider/model


# --- 2. The data shape --------------------------------------------------------
# Purpose: define the EXACT structured result of triaging a message.
# Every field is constrained or described so the output is predictable and easy to act on:
#   - Literal[...] limits a field to a fixed menu of values (like a dropdown).
#   - Field(description=...) tells the model exactly what belongs in that box.
#   - needs_human is the *escalation decision* as data — code can branch on it directly.
from typing import Literal
from pydantic import BaseModel, Field


class Triage(BaseModel):
    category: Literal["billing", "technical", "account", "general"] = Field(
        description="The main topic of the customer's message."
    )
    urgency: Literal["low", "medium", "high"] = Field(
        description="How quickly this needs a response."
    )
    sentiment: Literal["negative", "neutral", "positive"] = Field(
        description="The customer's mood in the message."
    )
    needs_human: bool = Field(
        description="True if this must be escalated to a human — refunds, billing disputes, "
                    "cancellations, legal/privacy issues, or an angry customer."
    )
    summary: str = Field(description="One-line summary of what the customer wants.")


# --- 3. System prompts --------------------------------------------------------
# Purpose: load both system prompts from prompt.yml instead of hard-coding them.
# Keeping prompts OUT of the code means we can reword them without editing Python —
# the system prompt carries the *behaviour*, the user message carries the *data*.
import yaml
from pathlib import Path

_PROMPTS = yaml.safe_load((Path(__file__).parent / "prompt.yml").read_text(encoding="utf-8"))
TRIAGE_SYSTEM = _PROMPTS["triage_system"]   # built from: role · task · guardrails · fallback
REPLY_SYSTEM = _PROMPTS["reply_system"]     # built from: role+tone · task+format · guardrails · fallback


# --- 4. Token & cost tracking -------------------------------------------------
# Purpose: every call reports how many tokens it used — the unit we pay for.
# We accumulate a running total so we can see the cost of one end-to-end run.
# Prices are per 1M tokens and are only an example — ALWAYS check the current pricing page.
IN_PRICE_PER_MTOK = 0.25     # Gemini Flash-Lite input (text/image/video; audio is $0.50)
OUT_PRICE_PER_MTOK = 1.50    # Gemini Flash-Lite output (includes thinking tokens)

_totals = {"input": 0, "output": 0}


def track(usage) -> None:
    """Add one response's token usage to the running totals.

    Gemini reports usage on `response.usage_metadata`: prompt_token_count is the
    input, candidates_token_count is the generated output. (A field can be None
    when nothing was counted, so we fall back to 0.)
    """
    _totals["input"] += usage.prompt_token_count or 0
    _totals["output"] += usage.candidates_token_count or 0


def usage_report() -> str:
    """Summarise tokens used and the estimated cost so far."""
    cost = (_totals["input"] / 1e6 * IN_PRICE_PER_MTOK
            + _totals["output"] / 1e6 * OUT_PRICE_PER_MTOK)
    return f"{_totals['input']} in + {_totals['output']} out tokens = ~${cost:.4f}"


# --- 5. Triage ----------------------------------------------------------------
# Purpose: turn a raw customer message into a validated `Triage` object (one LLM call).
# Returns a real Python object so later steps can branch on it (t.category, t.needs_human, ...).
def triage(message: str) -> Triage:
    resp = client.models.generate_content(
        model=MODEL,
        contents=message,
        config={
            "system_instruction": TRIAGE_SYSTEM,
            "response_mime_type": "application/json",  # ask for JSON, not prose
            "response_schema": Triage,                 # ...shaped EXACTLY like our schema
        },
    )
    track(resp.usage_metadata)      # record token usage for this call
    return resp.parsed              # already a validated Triage object


# --- 6. Draft reply -----------------------------------------------------------
# Purpose: write a short, human-editable first reply, guided by the triage result.
# We pass the triage in so the reply knows the category/urgency and whether to escalate.
def draft_reply(message: str, t: Triage) -> str:
    resp = client.models.generate_content(
        model=MODEL,
        contents=f"Customer message:\n{message}\n\nTriage: {t.model_dump()}",
        config={"system_instruction": REPLY_SYSTEM},
    )
    track(resp.usage_metadata)      # record token usage for this call
    return resp.text


# --- 7. Try it ----------------------------------------------------------------
# Purpose: run the assistant end-to-end on a few sample messages, then print the
# token/cost summary for the whole run.
def main() -> None:
    samples = [
        "I've been charged twice for May and nobody has replied. This is ridiculous.",
        "How do I change the email address on my account?",
        "Your app keeps crashing when I upload a file.",
    ]
    for s in samples:
        t = triage(s)
        print("-" * 70)
        print("MESSAGE :", s)
        print("TRIAGE  :", t.model_dump())
        print("ESCALATE:", "yes -> human" if t.needs_human else "no")
        print("DRAFT   :", draft_reply(s, t))

    print("=" * 70)
    print("TOKENS  :", usage_report())


if __name__ == "__main__":
    main()

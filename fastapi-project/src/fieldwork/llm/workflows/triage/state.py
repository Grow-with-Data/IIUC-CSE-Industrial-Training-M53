"""Simulation-chat graph state (owned by the outer StateGraph)."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class TriageChatState(TypedDict, total=False):
    """Conversation state persisted per session (thread) by the checkpointer.

    ``messages`` accumulates the running Human/AI turns (clean text only — the
    structured ``create_agent`` runs statelessly inside the node, so nothing but
    plain messages is checkpointed). ``system_prompt``, ``user_input`` and
    ``model`` are the per-turn inputs passed in as the graph input each request.

    ``model`` is the client-requested model ID as a plain string (never the
    ``ChatModel`` enum, so nothing enum-shaped reaches the checkpointer's
    serializer) and is ``None`` when the caller wants the default chain. The
    driver always writes the key, so a turn that omits it is not served by the
    previous turn's model.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    # system_prompt: str
    user_input: str
    # model: str | None

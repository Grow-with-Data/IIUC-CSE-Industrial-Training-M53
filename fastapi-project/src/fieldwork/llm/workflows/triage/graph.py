"""Simulation-chat outer workflow: a class-based StateGraph + module singleton.

LangGraph owns memory: the graph is compiled per request with the Postgres
checkpointer and persists only the clean Human/AI text produced by the node.
"""

from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from fieldwork.llm.workflows.triage.state import TriageChatState
from fieldwork.llm.workflows.triage.nodes import triageChat

class TraigeChatGraph(StateGraph):
    """The single-node simulation-chat StateGraph (nodes/edges wired in ``__init__``)."""

    def __init__(self) -> None:
        super().__init__(TriageChatState)
        self.add_node("triage", triageChat)
        self.add_edge(START, "triage")
        self.add_edge("triage", END)

    def compile_graph(self, checkpointer: BaseCheckpointSaver | None = None) -> CompiledStateGraph:
        """Compile the graph, wiring the per-session checkpointer for memory."""
        return self.compile()


triage_chat_graph = TraigeChatGraph()

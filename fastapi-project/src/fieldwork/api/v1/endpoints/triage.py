from fastapi import APIRouter

from fieldwork.api.v1.schemas import TriageInput, TriageOutput
from fieldwork.llm.workflows.triage.graph import triage_chat_graph

router = APIRouter()

@router.post("/triage/chatbot", response_model=TriageOutput)
async def triage_chatbot(
    triage_input: TriageInput
): 
    graph = triage_chat_graph.compile()
    state = {
        "user_input": triage_input.user_input
    }
    result = await graph.ainvoke(state)
    return {
        "response": result['messages'][-1].text
    }
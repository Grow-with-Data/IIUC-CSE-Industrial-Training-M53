
from langchain.agents import create_agent
from fieldwork.llm.workflows.triage.state import TriageChatState


async def triageChat(state: TriageChatState):
    # model = init_chat_model("gpt-5.5")

    agent = create_agent(
        model="google_genai:gemini-3.5-flash-lite",
        system_prompt="You are a helpful assistant",
    )
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": state["user_input"]}]}
    )
    return {
        "messages": result["messages"]
    }
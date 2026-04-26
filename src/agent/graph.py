import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from src.agent.llm_service import generate_response
from src.agent.voice_guard import build_system_prompt, filter_forbidden_phrases
from src.agent.tools import query_sales_leads, search_knowledge_base
from src.config.settings import get_settings

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    config_updates: dict

def call_model(state: AgentState):
    settings = get_settings()
    messages = state["messages"]
    
    # Check for config command (Dynamic Configuration)
    last_msg = messages[-1].content
    if last_msg.startswith("/set-model"):
        new_model = last_msg.split(" ")[1]
        # In a real app, we'd update settings.active_llm_provider in DB here
        return {"messages": [AIMessage(content=f"Configuration updated: Model set to {new_model}")], "config_updates": {"model": new_model}}
    
    # Very simple tool routing based on keywords (for MVP)
    last_msg_content = last_msg.lower()
    if "lead" in last_msg_content or "company" in last_msg_content:
        tool_res = query_sales_leads(last_msg)
        context = f"SQL Context: {tool_res}\n\nUser: {last_msg}"
    elif "product" in last_msg_content or "expertise" in last_msg_content:
        tool_res = search_knowledge_base(last_msg)
        context = f"RAG Context: {tool_res}\n\nUser: {last_msg}"
    else:
        context = last_msg

    sys_prompt = build_system_prompt()
    full_prompt = f"{sys_prompt}\n\n{context}"
    
    raw_response = generate_response(full_prompt, provider=settings.active_llm_provider)
    safe_response = filter_forbidden_phrases(raw_response)
    
    return {"messages": [AIMessage(content=safe_response)], "config_updates": {}}

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    return workflow.compile()

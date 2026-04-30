import operator
from typing import Annotated, Sequence, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.agent.tools import send_whatsapp_text, send_whatsapp_image, send_whatsapp_document, launch_whatsapp_campaign
from app.config import settings
from app.services.config_service import ConfigService
from loguru import logger

# Define State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender_phone: str

# All possible tools
all_tools = [send_whatsapp_text, send_whatsapp_image, send_whatsapp_document, launch_whatsapp_campaign]
tool_node = ToolNode(all_tools)

# Define Logic
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Define Logic
def call_model(state: AgentState):
    sender_phone = state["sender_phone"]
    messages = list(state["messages"])
    
    # 1. BREAK INFINITE LOOPS: Check if we just finished a terminal tool (sending a message)
    if messages and isinstance(messages[-1], ToolMessage):
        last_msg = messages[-1]
        # If the last thing that happened was a successful send, STOP.
        if "send_whatsapp" in last_msg.name and "Successfully sent" in last_msg.content:
            logger.info(f"Detected successful terminal tool '{last_msg.name}'. Terminating graph.")
            return {"messages": [AIMessage(content="Finalized.")]}

    # Load dynamic configuration
    config_service = ConfigService()
    config = config_service.get_config()
    
    # 2. Filter tools based on config
    tools_enabled = config.get("tools_enabled", {})
    available_tools = [t for t in all_tools if tools_enabled.get(t.name, True)]
    
    # 3. Get LLM providers from config
    providers = config.get("llm_providers", [])
    if not providers:
        # Fallback for old config format
        llm_config = config.get("llm", {})
        providers = [{
            "provider": llm_config.get("provider", "openrouter"),
            "model": llm_config.get("model", settings.llm_model),
            "temperature": llm_config.get("temperature", 0)
        }]

    # 4. Construct System Message from config
    base_prompt = config.get("system_prompt", "You are a professional WhatsApp AI Assistant.")
    system_msg_content = (
        f"{base_prompt}\n\n"
        f"You are talking to: {sender_phone}. "
        "\n\nOPERATIONAL RULES:\n"
        "1. To reply to the user, you MUST use the 'send_whatsapp_text' tool.\n"
        "2. If you have already used a tool to send your reply in this conversation turn, DO NOT use it again.\n"
        "3. Once you see a tool output confirming the message was sent, stop calling tools.\n"
        "4. The user only sees what you send via tools. Plain text responses from you are invisible to them.\n"
        "5. Be helpful, concise, and friendly.")
    
    system_msg = SystemMessage(content=system_msg_content)
    full_messages = [system_msg] + messages

    # 4. Try providers in order
    last_error = None
    for p_config in providers:
        provider_name = p_config.get("provider", "openrouter").lower()
        model_name = p_config.get("model")
        temperature = p_config.get("temperature", 0)
        
        # Determine API Key and Base URL
        if provider_name == "openrouter":
            api_key = settings.openrouter_api_key
            api_base = "https://openrouter.ai/api/v1"
        elif provider_name == "openai":
            api_key = settings.openai_api_key
            api_base = None
        elif provider_name == "groq":
            api_key = settings.groq_api_key
            api_base = "https://api.groq.com/openai/v1"
        else:
            # Default to openrouter if unknown provider
            api_key = settings.openrouter_api_key
            api_base = "https://openrouter.ai/api/v1"
        
        try:
            model = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=api_key,
                openai_api_base=api_base
            ).bind_tools(available_tools)

            logger.info(f"Invoking LLM ({model_name}) via {provider_name} for {sender_phone}...")
            response = model.invoke(full_messages)
            return {"messages": [response]}
        except Exception as e:
            logger.warning(f"Provider {provider_name} ({model_name}) failed: {e}")
            last_error = e
            continue
    
    # If all providers fail
    logger.error(f"All LLM providers failed for {sender_phone}. Last error: {last_error}")
    error_msg = AIMessage(content="I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment.")
    return {"messages": [error_msg]}

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

agent_app = workflow.compile()

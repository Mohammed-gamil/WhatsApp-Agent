from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from src.agent.tools import whatsapp_sender
from src.config.settings import get_settings
from loguru import logger
import os

def run_whatsapp_agent(sender_phone: str, user_message: str):
    settings = get_settings()
    
    # Configure OpenRouter
    # Base URL for OpenRouter is https://openrouter.ai/api/v1
    llm = ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=settings.openrouter_api_key,
        model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        temperature=0.1 # Low temperature for reasoning
    )

    system_prompt = (
        f"You are a helpful WhatsApp assistant. The user's phone number is {sender_phone}. "
        "When you have a response, ALWAYS use the 'whatsapp_sender' tool to send it to the user. "
        "Do not just state the answer, use the tool."
    )

    try:
        # create_agent returns a LangGraph CompiledStateGraph
        agent = create_agent(
            model=llm, # Pass the configured LLM object
            tools=[whatsapp_sender],
            system_prompt=system_prompt
        )
        
        # Invoke the agent with the user message
        agent.invoke({"messages": [("user", user_message)]})
        logger.info(f"Agent finished for {sender_phone}")
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")

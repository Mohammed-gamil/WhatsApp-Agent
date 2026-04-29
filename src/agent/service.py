from langchain.agents import create_agent
from src.agent.tools import whatsapp_sender
from src.config.settings import get_settings
from loguru import logger
import os

def run_whatsapp_agent(sender_phone: str, user_message: str):
    settings = get_settings()
    
    # Ensure API key is in environment for create_agent/init_chat_model
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    system_prompt = (
        f"You are a helpful WhatsApp assistant. The user's phone number is {sender_phone}. "
        "When you have a response, ALWAYS use the 'whatsapp_sender' tool to send it to the user. "
        "Do not just state the answer, use the tool."
    )

    try:
        # create_agent returns a LangGraph CompiledStateGraph
        agent = create_agent(
            model="gpt-4o",
            tools=[whatsapp_sender],
            system_prompt=system_prompt
        )
        
        # Invoke the agent with the user message
        agent.invoke({"messages": [("user", user_message)]})
        logger.info(f"Agent finished for {sender_phone}")
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")

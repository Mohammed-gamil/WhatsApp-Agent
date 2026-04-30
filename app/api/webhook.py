from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Set
from langchain_core.messages import HumanMessage
from app.agent.graph import agent_app
from loguru import logger
import time
import json
import traceback

router = APIRouter()

# In-memory set for deduplication (In production, use Redis)
processed_message_ids: Set[str] = set()

# In-memory history (In production, use a Database)
session_history: dict[str, list] = {}

async def process_whatsapp_message(event_data: dict):
    """
    Background task to process the message through LangGraph.
    """
    message_id = event_data.get("message_id")
    try:
        sender_phone = event_data.get("from")
        message_text = event_data.get("text")
        
        if not sender_phone or not message_text:
            logger.warning(f"Skipping message {message_id}: Missing 'from' or 'text' in data")
            return

        logger.info(f"--- AGENT START: Message {message_id} from {sender_phone} ---")
        logger.info(f"User Message: {message_text}")
        
        # 1. Get or create history
        if sender_phone not in session_history:
            session_history[sender_phone] = []
        
        # 2. Append new user message
        history = session_history[sender_phone]
        history.append(HumanMessage(content=message_text))
        
        # 3. Limit history to last 10 messages
        if len(history) > 10:
            history = history[-10:]
            session_history[sender_phone] = history

        inputs = {
            "messages": history,
            "sender_phone": sender_phone
        }
        
        # 4. Run the LangGraph agent
        result = await agent_app.ainvoke(inputs)
        
        # 5. Update history with the final messages from the agent
        # result["messages"] contains the full conversation from this turn
        session_history[sender_phone] = result.get("messages", history)
        
        # Log the AI's final state to see what it did
        final_messages = result.get("messages", [])
        if final_messages:
            last_ai_msg = final_messages[-1]
            logger.info(f"AI Final Response: {last_ai_msg.content}")
            if hasattr(last_ai_msg, 'tool_calls') and last_ai_msg.tool_calls:
                logger.info(f"AI used tools: {[tc['name'] for tc in last_ai_msg.tool_calls]}")
            else:
                logger.warning("AI did NOT use any tools for this response!")
        
        logger.info(f"--- AGENT END: Message {message_id} ---")
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in process_whatsapp_message: {str(e)}")
        logger.error(traceback.format_exc())
        # Remove from set so it can be retried
        if message_id in processed_message_ids:
            processed_message_ids.remove(message_id)

@router.get("/webhook/whats360")
async def verify_whats360_webhook():
    """
    Simple verification endpoint for Whats360.
    """
    logger.info("Webhook verification request received (GET)")
    return {"status": "success", "message": "Whats360 Webhook is active"}

@router.post("/webhook/whats360")
async def receive_whats360_webhook(payload: dict, background_tasks: BackgroundTasks):
    """
    Receives incoming WhatsApp messages from Whats360 v2.
    Handles both simulated (message.received) and real (message_incoming) events.
    """
    logger.info(f"RAW WEBHOOK RECEIVED: {json.dumps(payload)}")
    
    event_type = payload.get("event")
    
    # Initialize variables
    data = {}
    message_id = None
    sender_phone = None
    message_text = None

    # 1. Parse based on event type
    if event_type == "message.received":
        # Simulated format from UI
        data = payload.get("data", {})
        message_id = data.get("message_id")
        sender_phone = data.get("from")
        message_text = data.get("text")
    elif event_type == "message_incoming":
        # Real format from Whats360 Webhook
        msg_obj = payload.get("message", {})
        message_id = msg_obj.get("id")
        # Extract phone from chat_jid (e.g., "2010...@s.whatsapp.net")
        chat_jid = msg_obj.get("chat_jid", "")
        sender_phone = chat_jid.split("@")[0] if "@" in chat_jid else chat_jid
        message_text = msg_obj.get("content")
        # Wrap back into the 'data' format expected by process_whatsapp_message
        data = {
            "from": sender_phone,
            "text": message_text,
            "message_id": message_id
        }
    else:
        logger.info(f"Ignoring event: {event_type}")
        return {"status": "ignored", "event": event_type}

    if not message_id:
        logger.error("No message_id in payload")
        return {"status": "error", "reason": "Missing message_id"}

    # 2. Deduplication Check
    if message_id in processed_message_ids:
        logger.warning(f"Duplicate message: {message_id}")
        return {"status": "success", "message": "Duplicate ignored"}

    processed_message_ids.add(message_id)
    
    # 3. Cleanup old IDs
    if len(processed_message_ids) > 1000:
        processed_message_ids.clear() 

    # 4. Dispatch background task
    background_tasks.add_task(process_whatsapp_message, data)

    return {"status": "success"}

from fastapi import APIRouter, Query, Request, HTTPException, BackgroundTasks
from src.config.settings import get_settings
from src.agent.graph import build_graph
from langchain_core.messages import HumanMessage
from src.api.outbound import send_whatsapp_message
from src.database.session import SessionLocal
from src.database.models import ChatMessage
from src.agent.service import run_whatsapp_agent
from loguru import logger

router = APIRouter()
settings = get_settings()
agent_app = build_graph()

@router.post("/webhook/whats360")
async def handle_whats360_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        logger.info(f"Received Whats360 webhook: {data}")
        
        event_type = data.get("event")
        
        # We only care about incoming messages
        if event_type != "message.received":
            logger.info(f"Ignoring Whats360 event: {event_type}")
            return {"status": "ignored", "event": event_type}
            
        message_data = data.get("data", {})
        sender_phone = message_data.get("from")
        text_body = message_data.get("text")
        
        if sender_phone and text_body:
            logger.info(f"Triggering agent for {sender_phone}: {text_body[:50]}...")
            background_tasks.add_task(run_whatsapp_agent, sender_phone, text_body)
            return {"status": "success", "message": "Agent triggered in background"}
        
        return {"status": "ignored", "reason": "Missing from or text in message data"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == settings.meta_verify_token:
        try:
            return int(challenge)
        except (ValueError, TypeError):
            return challenge
    raise HTTPException(status_code=403, detail="Invalid verification token")

@router.post("/webhook")
async def handle_incoming_message(request: Request):
    data = await request.json()
    
    # Basic Meta WhatsApp webhook parsing
    try:
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    if messages:
                        msg = messages[0]
                        phone_number = msg["from"]
                        text = msg.get("text", {}).get("body", "")
                        
                        if text:
                            # 1. Save user message
                            db = SessionLocal()
                            try:
                                user_msg = ChatMessage(phone_number=phone_number, role="user", content=text)
                                db.add(user_msg)
                                db.commit()
                            except Exception as e:
                                logger.error(f"Error saving user chat: {e}")
                            finally:
                                db.close()

                            # 2. Process via LangGraph
                            state = {
                                "messages": [HumanMessage(content=text)], 
                                "config_updates": {},
                                "sender_number": phone_number
                            }
                            result = agent_app.invoke(state)
                            ai_response = result["messages"][-1].content
                            
                            # 3. Save AI message
                            db = SessionLocal()
                            try:
                                agent_msg = ChatMessage(phone_number=phone_number, role="agent", content=ai_response)
                                db.add(agent_msg)
                                db.commit()
                            except Exception as e:
                                logger.error(f"Error saving agent chat: {e}")
                            finally:
                                db.close()
                            
                            # 4. Send reply
                            await send_whatsapp_message(phone_number, ai_response)
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        
    return {"status": "ok"}

from fastapi import APIRouter, Query, Request, HTTPException
from src.config.settings import get_settings
from src.agent.graph import build_graph
from langchain_core.messages import HumanMessage
from src.api.outbound import send_whatsapp_message

router = APIRouter()
settings = get_settings()
agent_app = build_graph()

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
                            # Process via LangGraph
                            state = {"messages": [HumanMessage(content=text)], "config_updates": {}}
                            result = agent_app.invoke(state)
                            ai_response = result["messages"][-1].content
                            
                            # Send reply
                            await send_whatsapp_message(phone_number, ai_response)
            
    except Exception as e:
        # Log error in production
        print(f"Error processing webhook: {e}")
        
    return {"status": "ok"}

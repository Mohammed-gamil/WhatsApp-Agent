import requests
from src.config.settings import get_settings
from loguru import logger
import httpx

def send_whats360_message(to_number: str, message_text: str):
    settings = get_settings()
    url = f"{settings.whats360_api_url}/messages/send"
    headers = {
        "Authorization": f"Bearer {settings.whats360_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to_number,
        "text": message_text
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Message sent to {to_number}: {message_text}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send message to {to_number}: {e}")
        return {"success": False, "error": str(e)}

async def send_whatsapp_message(to_number: str, message_text: str):
    settings = get_settings()
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {
        "Authorization": f"Bearer {settings.meta_access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()

async def send_whatsapp_interactive_buttons(to_number: str, body_text: str, buttons: list[str]):
    """Send up to 3 interactive reply buttons."""
    settings = get_settings()
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {
        "Authorization": f"Bearer {settings.meta_access_token}",
        "Content-Type": "application/json"
    }
    
    # Format buttons (Max 3 allowed by Meta)
    formatted_buttons = []
    for i, btn_title in enumerate(buttons[:3]):
        formatted_buttons.append({
            "type": "reply",
            "reply": {
                "id": f"btn_{i}",
                "title": btn_title[:20] # Max 20 chars
            }
        })
        
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": formatted_buttons
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()

import httpx
from src.config.settings import get_settings

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

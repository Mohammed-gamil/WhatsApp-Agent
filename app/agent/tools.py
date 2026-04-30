from langchain_core.tools import tool
from app.services.whats360 import Whats360Client
from loguru import logger

# Initialize client
client = Whats360Client()

@tool
def send_whatsapp_text(phone: str, message: str) -> str:
    """
    Sends a plain text WhatsApp message to a specific phone number.
    Use this for direct replies or general notifications.
    'phone' should be in international format (e.g., '201097294152').
    """
    logger.info(f"Tool: send_whatsapp_text to {phone}")
    result = client.send_text(phone, message)
    if result.get("success") or "id" in str(result):
        return f"Successfully sent text message to {phone}."
    return f"Failed to send text message: {result.get('error', 'Unknown error')}"

@tool
def send_whatsapp_image(phone: str, image_url: str, caption: str = "") -> str:
    """
    Sends an image via WhatsApp using a public image URL.
    Use this when the user asks for a picture or visual proof.
    """
    logger.info(f"Tool: send_whatsapp_image to {phone}")
    result = client.send_image(phone, image_url, caption)
    if result.get("success") or "id" in str(result):
        return f"Successfully sent image to {phone}."
    return f"Failed to send image: {result.get('error', 'Unknown error')}"

@tool
def send_whatsapp_document(phone: str, doc_url: str, caption: str = "") -> str:
    """
    Sends a document (PDF, DOCX, etc.) via WhatsApp using a public document URL.
    Use this when the user asks for a report, invoice, or file.
    """
    logger.info(f"Tool: send_whatsapp_document to {phone}")
    result = client.send_document(phone, doc_url, caption)
    if result.get("success") or "id" in str(result):
        return f"Successfully sent document to {phone}."
    return f"Failed to send document: {result.get('error', 'Unknown error')}"

@tool
def launch_whatsapp_campaign(name: str, message: str, recipients: list[dict]) -> str:
    """
    Creates, adds recipients to, and starts a bulk WhatsApp marketing campaign.
    'recipients' must be a list of dicts like: [{"phone": "2010...", "name": "John"}]
    Use this for bulk marketing or mass notifications.
    """
    logger.info(f"Tool: launch_whatsapp_campaign '{name}'")
    
    # 1. Create
    create_res = client.create_campaign(name, message)
    campaign_id = create_res.get("response", {}).get("campaign_id")
    if not campaign_id:
        return f"Failed to create campaign: {create_res.get('error', 'No ID returned')}"
    
    # 2. Add recipients
    add_res = client.add_campaign_recipients(str(campaign_id), recipients)
    if not add_res.get("success") and "id" not in str(add_res):
        return f"Failed to add recipients to campaign {campaign_id}."
    
    # 3. Start
    start_res = client.start_campaign(str(campaign_id))
    if start_res.get("success") or "id" in str(start_res):
        return f"Campaign '{name}' (ID: {campaign_id}) launched successfully with {len(recipients)} recipients."
    
    return f"Campaign created but failed to start: {start_res.get('error')}"

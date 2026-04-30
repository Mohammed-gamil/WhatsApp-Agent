import requests
import urllib.parse
import json
from loguru import logger
from app.config import settings

class Whats360Client:
    """
    A client for interacting with the Whats360 v1 API.
    Based on working GET request architecture.
    """

    def __init__(self):
        # We use the base URL from settings (e.g., https://whats360.live)
        self.base_url = settings.whats360_base_url.rstrip('/')
        self.token = settings.whats360_token
        self.instance_id = settings.whats360_instance_id

    def _make_v1_get(self, endpoint: str, params: dict) -> dict:
        """Helper to make GET requests to V1 API."""
        # Always include token and instance_id
        params["token"] = self.token
        params["instance_id"] = self.instance_id
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"Making V1 GET request to {url}")
            # Use params=params to handle URL encoding properly
            response = requests.get(url, params=params, timeout=15)
            logger.info(f"Whats360 API Raw Response ({endpoint}): {response.status_code} - {response.text}")
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Whats360 V1 API Error ({endpoint}): {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    def _format_jid(self, phone: str) -> str:
        """Ensures phone is in JID format."""
        phone = str(phone).strip().replace("+", "")
        if "@s.whatsapp.net" not in phone:
            return f"{phone}@s.whatsapp.net"
        return phone

    def send_text(self, phone: str, message: str) -> dict:
        """Sends a text message using V1 /api/v1/send-text."""
        params = {
            "jid": self._format_jid(phone),
            "msg": message
        }
        return self._make_v1_get("/api/v1/send-text", params)

    def send_image(self, phone: str, image_url: str, caption: str = "") -> dict:
        """Sends an image using V1 /api/v1/send-media."""
        params = {
            "jid": self._format_jid(phone),
            "media_url": image_url,
            "msg": caption,
            "type": "image"
        }
        return self._make_v1_get("/api/v1/send-media", params)

    def send_document(self, phone: str, doc_url: str, caption: str = "") -> dict:
        """Sends a document using V1 /api/v1/send-media."""
        params = {
            "jid": self._format_jid(phone),
            "media_url": doc_url,
            "msg": caption,
            "type": "document"
        }
        return self._make_v1_get("/api/v1/send-media", params)

    def set_webhook(self, webhook_url: str) -> dict:
        """Sets the webhook URL using V1 /api/v1/set-webhook."""
        params = {
            "webhook_url": webhook_url
        }
        return self._make_v1_get("/api/v1/set-webhook", params)

    def create_campaign(self, name: str, message: str) -> dict:
        """Creates a new campaign."""
        params = {
            "name": name,
            "msg": message
        }
        return self._make_v1_get("/api/v1/create-campaign", params)

    def add_campaign_recipients(self, campaign_id: str, recipients: list) -> dict:
        """Adds recipients to a campaign."""
        params = {
            "id": campaign_id,
            "recipients": json.dumps(recipients)
        }
        return self._make_v1_get("/api/v1/add-campaign-recipients", params)

    def start_campaign(self, campaign_id: str) -> dict:
        """Starts a campaign."""
        params = {
            "id": campaign_id
        }
        return self._make_v1_get("/api/v1/start-campaign", params)

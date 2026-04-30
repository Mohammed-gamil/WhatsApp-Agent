import uvicorn
from fastapi import FastAPI, HTTPException
from app.api.webhook import router as webhook_router
from app.config import settings
from loguru import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Asynchronous WhatsApp AI Agent using Whats360 and LangGraph",
        version="1.0.0"
    )

    # Include Routes
    app.include_router(webhook_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {
            "app": settings.app_name,
            "status": "online",
            "docs": "/docs"
        }

    @app.get("/api/v1/config")
    async def get_agent_config():
        from app.services.config_service import ConfigService
        config_service = ConfigService()
        return config_service.get_config()

    @app.post("/api/v1/config")
    async def update_agent_config(config: dict):
        from app.services.config_service import ConfigService
        config_service = ConfigService()
        try:
            config_service.update_config(config)
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return {"status": "error", "message": str(e)}

    @app.post("/api/v1/config/webhook")
    async def update_webhook(payload: dict):
        """Updates the webhook URL in Whats360."""
        from app.services.whats360 import Whats360Client
        client = Whats360Client()
        url = payload.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        result = client.set_webhook(url)
        return result

    return app

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name}...")
    # Disabled reload to save memory (WinError 1455 fix)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=False)

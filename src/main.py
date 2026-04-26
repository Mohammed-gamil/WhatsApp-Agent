from fastapi import FastAPI
from src.api.whatsapp import router as whatsapp_router

app = FastAPI(title="WhatsApp Sales Agent")
app.include_router(whatsapp_router)

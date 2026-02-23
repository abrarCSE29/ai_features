from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config.app_config import AppConfig
from modules.ocr.router import router as ocr_router
from modules.chatbot.router import router as chatbot_router
from modules.object_detection.router import router as object_detection_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=AppConfig.origins,
    allow_credentials=AppConfig.allow_credentials,
    allow_methods=AppConfig.allow_methods,
    allow_headers=AppConfig.allow_headers,
)

# Include routers
app.include_router(ocr_router)
app.include_router(chatbot_router)
app.include_router(object_detection_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def startup():
    return {"status": "ai api running"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.app_config import AppConfig

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=AppConfig.origins,          
    allow_credentials=AppConfig.allow_credentials,
    allow_methods=AppConfig.allow_methods,            
    allow_headers=AppConfig.allow_headers,            # Authorization, Content-Type, etc
)


@app.get("/health")
def startup():
    return {"status":"ai api running"}
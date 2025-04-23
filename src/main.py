from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import tarot
from config.firebase_config import init_firebase

app = FastAPI(docs_url='/docs')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tarot.router, tags=["tarot"])

init_firebase(app)
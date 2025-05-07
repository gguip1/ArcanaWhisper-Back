from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import tarot
from config.firebase_config import lifespan

# app = FastAPI(docs_url='/docs')
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aitarot.site", "https://www.aitarot.site"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init_firebase(app)

app.include_router(tarot.router, tags=["tarot"])
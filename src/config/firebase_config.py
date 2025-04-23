import firebase_admin
from fastapi import FastAPI

from firebase_admin import credentials, firestore
from utils.api_key_loader import get_api_key

def init_firebase(app: FastAPI):
    @app.on_event("startup")
    async def startup_firebase_client():
        try:
            if not firebase_admin._apps:
                GOOGLE_APPLICATION_CREDENTIALS = get_api_key('GOOGLE_APPLICATION_CREDENTIALS')
                cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
                firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Firebase initialization error: {e}")
    
    @app.on_event("shutdown")
    async def shutdown_firebase_client():
        try:
            if firebase_admin._apps:
                firebase_admin.delete_app(firebase_admin.get_app())
        except Exception as e:
            print(f"Firebase shutdown error: {e}")
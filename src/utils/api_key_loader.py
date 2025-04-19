import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        return key
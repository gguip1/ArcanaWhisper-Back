import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(env_variable) -> str:
        key = os.getenv(env_variable)
        if not key:
            raise ValueError(f"{env_variable} 환경변수가 설정되어 있지 않습니다.")
        return key
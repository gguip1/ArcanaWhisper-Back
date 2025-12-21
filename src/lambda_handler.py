import json
import logging
import os
import base64

import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ============================================================
# Firebase 전역 초기화 (Cold start 시 1회만 실행)
# ============================================================
def _get_credentials_from_ssm(param_name: str) -> str:
    """AWS Systems Manager Parameter Store에서 credentials 로드"""
    import boto3
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def _init_firebase():
    if firebase_admin._apps:
        return

    # 방법 1: SSM Parameter Store에서 로드 (Lambda 배포용)
    param_name = os.environ.get("FIREBASE_CREDENTIALS_PARAM")
    if param_name:
        try:
            cred_base64 = _get_credentials_from_ssm(param_name)
            cred_json = base64.b64decode(cred_base64).decode("utf-8")
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase initialized from SSM Parameter: {param_name}")
            return
        except Exception as e:
            logger.warning(f"Failed to load from SSM: {e}, trying fallback...")

    # 방법 2: 파일 경로에서 로드 (로컬 테스트용)
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_PATH")
    if cred_path:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info(f"Firebase initialized from file: {cred_path}")
        return

    raise ValueError("Firebase credentials not found. Set FIREBASE_CREDENTIALS_PARAM or GOOGLE_APPLICATION_CREDENTIALS_PATH")

_init_firebase()

# ============================================================
# 서비스 임포트 (Firebase 초기화 후)
# ============================================================
from src.services.tarot_service import TarotService
from src.services.history_service import HistoryService
from src.repository.history_repository import HistoryRepository
from src.schema.tarot import TarotCards

# ============================================================
# 응답 헬퍼
# ============================================================
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}

def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, ensure_ascii=False),
    }

def error_response(status_code: int, message: str) -> dict:
    return response(status_code, {"error": message})

# ============================================================
# Lambda Handler
# ============================================================
def handler(event, _context):
    """메인 Lambda 핸들러 - API Gateway HTTP API 이벤트 처리"""
    logger.info(f"Event: {json.dumps(event)}")

    # OPTIONS 요청 처리 (CORS preflight)
    http_method = event.get("requestContext", {}).get("http", {}).get("method", "")
    if http_method == "OPTIONS":
        return response(200, {})

    # 라우팅 (스테이지 prefix 제거: /prod/tarot -> /tarot)
    raw_path = event.get("rawPath", "")
    # 스테이지명 제거 (/prod, /dev 등)
    path_parts = raw_path.split("/")
    if len(path_parts) > 2 and path_parts[1] in ["prod", "dev", "staging"]:
        path = "/" + "/".join(path_parts[2:])
    else:
        path = raw_path

    if path == "/tarot" and http_method == "POST":
        return handle_tarot_reading(event)
    elif path == "/tarot/history" and http_method == "GET":
        return handle_tarot_history(event)
    else:
        return error_response(404, f"Not Found: {http_method} {path}")


async def _async_tarot_reading(user_id, provider, question, cards, history_repository):
    """비동기 타로 리딩 처리"""
    tarot_service = TarotService(
        user_id=user_id,
        provider=provider,
        question=question,
        cards=cards,
        history_repository=history_repository
    )
    return await tarot_service.get_tarot_reading()


def handle_tarot_reading(event) -> dict:
    """POST /tarot - 타로 리딩 요청 처리"""
    import asyncio

    try:
        # Body 파싱
        body = event.get("body", "{}")
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")

        data = json.loads(body)

        # 필수 필드 검증
        question = data.get("question")
        cards_data = data.get("cards")

        if not question:
            return error_response(400, "question is required")
        if not cards_data:
            return error_response(400, "cards is required")

        # TarotCards 객체 생성
        cards = TarotCards(
            cards=cards_data.get("cards", []),
            reversed=cards_data.get("reversed", [False, False, False])
        )

        user_id = data.get("user_id")
        provider = data.get("provider")

        # 비동기 함수 실행
        history_repository = HistoryRepository()
        result = asyncio.run(_async_tarot_reading(
            user_id, provider, question, cards, history_repository
        ))

        return response(200, {
            "cards": {
                "cards": result.cards.cards,
                "reversed": result.cards.reversed
            },
            "result": result.result
        })

    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")
    except Exception as e:
        logger.error(f"Error in handle_tarot_reading: {e}", exc_info=True)
        return error_response(500, "Internal Server Error")


def handle_tarot_history(event) -> dict:
    """GET /tarot/history - 타로 히스토리 조회"""
    try:
        # Query parameters 파싱
        params = event.get("queryStringParameters") or {}

        user_id = params.get("user_id")
        provider = params.get("provider")
        cursor_doc_id = params.get("cursor_doc_id")

        if not user_id:
            return error_response(400, "user_id is required")
        if not provider:
            return error_response(400, "provider is required")

        # 히스토리 조회
        history_repository = HistoryRepository()
        history_service = HistoryService(
            user_id=user_id,
            provider=provider,
            cursor_doc_id=cursor_doc_id,
            history_repository=history_repository
        )

        result = history_service.get_history()

        # 응답 직렬화
        history_items = [
            {
                "question": item.question,
                "cards": {
                    "cards": item.cards.cards,
                    "reversed": item.cards.reversed
                },
                "result": item.result,
                "created_at": item.created_at
            }
            for item in result.history
        ]

        return response(200, {
            "history": history_items,
            "next_cursor_doc_id": result.next_cursor_doc_id
        })

    except ValueError as e:
        return error_response(400, str(e))
    except Exception as e:
        logger.error(f"Error in handle_tarot_history: {e}", exc_info=True)
        return error_response(500, "Internal Server Error")

import json
import logging
import os
import base64

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

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


def verify_firebase_token(authorization: str) -> dict:
    """
    Firebase ID Token 검증

    Args:
        authorization: "Bearer <token>" 형식의 헤더 값

    Returns:
        dict: { uid, email, provider }

    Raises:
        ValueError: 토큰이 없거나 유효하지 않은 경우
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise ValueError("Authorization header missing")

    token = authorization.split("Bearer ")[1]

    try:
        decoded = firebase_auth.verify_id_token(token)
        return {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
            "provider": decoded.get("firebase", {}).get("sign_in_provider", "unknown")
        }
    except firebase_auth.InvalidIdTokenError:
        raise ValueError("Invalid token")
    except firebase_auth.ExpiredIdTokenError:
        raise ValueError("Token expired")

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

    if path == "/health" and http_method == "GET":
        return response(200, {"status": "ok"})
    elif path == "/tarot" and http_method == "POST":
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


def _run_async(coro):
    """
    Lambda 환경에서 안전하게 비동기 함수 실행.

    asyncio.run()은 매 호출마다 event loop를 생성하고 닫는데,
    Lambda warm start 시 이전 요청에서 캐시된 httpx 클라이언트가
    닫힌 event loop를 참조하여 RuntimeError 발생.

    해결: 명시적으로 새 event loop를 생성하고 설정.
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def handle_tarot_reading(event) -> dict:
    """POST /tarot - 타로 리딩 요청 처리"""

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

        # Authorization 헤더에서 사용자 정보 추출 (비로그인 허용)
        headers = event.get("headers", {})
        authorization = headers.get("authorization")

        user_id = None
        provider = None

        if authorization:
            try:
                user = verify_firebase_token(authorization)
                user_id = user["uid"]
                provider = user["provider"]
            except ValueError:
                pass  # 토큰 실패해도 비로그인으로 처리

        # 비동기 함수 실행
        history_repository = HistoryRepository()
        result = _run_async(_async_tarot_reading(
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
        # Authorization 헤더에서 토큰 검증
        headers = event.get("headers", {})
        authorization = headers.get("authorization")  # API Gateway HTTP API는 소문자

        try:
            user = verify_firebase_token(authorization)
        except ValueError as e:
            return error_response(401, str(e))

        user_id = user["uid"]
        provider = user["provider"]

        # Query parameters에서 커서만 파싱
        params = event.get("queryStringParameters") or {}
        cursor_doc_id = params.get("cursor_doc_id")

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

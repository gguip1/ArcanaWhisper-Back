"""
Rate Limit 서비스

- Guest: 1회/일
- 로그인 사용자: 10회/일
- 리셋: KST 00:00
"""
import logging
from datetime import datetime, timezone, timedelta
from firebase_admin import firestore

logger = logging.getLogger(__name__)

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))

# 일일 사용량 제한
GUEST_DAILY_LIMIT = 1
USER_DAILY_LIMIT = 10


def _get_kst_today() -> str:
    """KST 기준 오늘 날짜 문자열 반환 (YYYY-MM-DD)"""
    return datetime.now(KST).strftime("%Y-%m-%d")


def _get_kst_reset_time() -> str:
    """다음 리셋 시간 (KST 00:00) ISO 8601 형식"""
    now = datetime.now(KST)
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return tomorrow.isoformat()


class UsageService:
    def __init__(self):
        db = firestore.client()
        self.guest_collection = db.collection("guest_usage")
        self.user_collection = db.collection("user_usage")

    def get_guest_usage(self, guest_token: str) -> dict:
        """Guest 사용량 조회"""
        doc = self.guest_collection.document(guest_token).get()
        today = _get_kst_today()

        if not doc.exists:
            return {"used": 0, "limit": GUEST_DAILY_LIMIT, "remaining": GUEST_DAILY_LIMIT}

        data = doc.to_dict()
        # 날짜가 다르면 리셋
        if data.get("date") != today:
            return {"used": 0, "limit": GUEST_DAILY_LIMIT, "remaining": GUEST_DAILY_LIMIT}

        used = data.get("count", 0)
        return {
            "used": used,
            "limit": GUEST_DAILY_LIMIT,
            "remaining": max(0, GUEST_DAILY_LIMIT - used)
        }

    def get_user_usage(self, user_id: str) -> dict:
        """로그인 사용자 사용량 조회"""
        doc = self.user_collection.document(user_id).get()
        today = _get_kst_today()

        if not doc.exists:
            return {"used": 0, "limit": USER_DAILY_LIMIT, "remaining": USER_DAILY_LIMIT}

        data = doc.to_dict()
        # 날짜가 다르면 리셋
        if data.get("date") != today:
            return {"used": 0, "limit": USER_DAILY_LIMIT, "remaining": USER_DAILY_LIMIT}

        used = data.get("count", 0)
        return {
            "used": used,
            "limit": USER_DAILY_LIMIT,
            "remaining": max(0, USER_DAILY_LIMIT - used)
        }

    def check_and_increment_guest(self, guest_token: str) -> tuple[bool, dict]:
        """
        Guest 사용량 체크 및 증가

        Returns:
            (allowed, usage_info)
            - allowed: True면 요청 허용, False면 제한 초과
            - usage_info: 현재 사용량 정보
        """
        today = _get_kst_today()
        doc_ref = self.guest_collection.document(guest_token)
        doc = doc_ref.get()

        current_count = 0
        if doc.exists:
            data = doc.to_dict()
            if data.get("date") == today:
                current_count = data.get("count", 0)

        # 제한 초과 체크
        if current_count >= GUEST_DAILY_LIMIT:
            return False, {
                "used": current_count,
                "limit": GUEST_DAILY_LIMIT,
                "remaining": 0,
                "reset_at": _get_kst_reset_time()
            }

        # 사용량 증가
        new_count = current_count + 1
        doc_ref.set({
            "count": new_count,
            "date": today,
            "updated_at": datetime.now(KST).isoformat()
        })

        return True, {
            "used": new_count,
            "limit": GUEST_DAILY_LIMIT,
            "remaining": max(0, GUEST_DAILY_LIMIT - new_count),
            "reset_at": _get_kst_reset_time()
        }

    def check_and_increment_user(self, user_id: str) -> tuple[bool, dict]:
        """
        로그인 사용자 사용량 체크 및 증가

        Returns:
            (allowed, usage_info)
        """
        today = _get_kst_today()
        doc_ref = self.user_collection.document(user_id)
        doc = doc_ref.get()

        current_count = 0
        if doc.exists:
            data = doc.to_dict()
            if data.get("date") == today:
                current_count = data.get("count", 0)

        # 제한 초과 체크
        if current_count >= USER_DAILY_LIMIT:
            return False, {
                "used": current_count,
                "limit": USER_DAILY_LIMIT,
                "remaining": 0,
                "reset_at": _get_kst_reset_time()
            }

        # 사용량 증가
        new_count = current_count + 1
        doc_ref.set({
            "count": new_count,
            "date": today,
            "updated_at": datetime.now(KST).isoformat()
        })

        return True, {
            "used": new_count,
            "limit": USER_DAILY_LIMIT,
            "remaining": max(0, USER_DAILY_LIMIT - new_count),
            "reset_at": _get_kst_reset_time()
        }

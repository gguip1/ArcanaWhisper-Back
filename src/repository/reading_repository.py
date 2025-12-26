"""
공유 리딩 Repository

readings 컬렉션: tarot_history를 참조하는 공유 링크 관리
- share_id (UUID)로 공개 접근
- history_id로 원본 데이터 참조
- 30일 후 만료
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from firebase_admin import firestore

SHARE_EXPIRY_DAYS = 30


class ReadingRepository:
    def __init__(self):
        db = firestore.client()
        self.readings_collection = db.collection("readings")
        self.history_collection = db.collection("tarot_history")

    def create_share(self, history_id: str) -> str:
        """
        공유 링크 생성

        Args:
            history_id: tarot_history document ID

        Returns:
            share_id: UUID 형식의 공유 ID
        """
        share_id = str(uuid.uuid4())
        # UTC datetime 사용 (Firestore가 자동으로 Timestamp로 변환)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=SHARE_EXPIRY_DAYS)

        self.readings_collection.document(share_id).set({
            "history_id": history_id,
            "created_at": now,
            "expires_at": expires_at
        })

        # tarot_history에 공유 상태 업데이트
        self.history_collection.document(history_id).update({
            "is_shared": True
        })

        return share_id

    def get_reading_by_share_id(self, share_id: str) -> Optional[dict]:
        """
        share_id로 리딩 데이터 조회 (공개)

        Returns:
            dict: { question, cards, result, created_at } 또는 None (만료/없음)
        """
        # 1. readings에서 share_id로 문서 조회
        share_doc = self.readings_collection.document(share_id).get()
        if not share_doc.exists:
            return None

        share_data = share_doc.to_dict()

        # 2. 만료 체크 (Firestore Timestamp는 UTC datetime으로 변환됨)
        expires_at = share_data["expires_at"]
        if datetime.now(timezone.utc) > expires_at:
            return None

        # 3. history_id로 원본 데이터 조회
        history_id = share_data["history_id"]
        history_doc = self.history_collection.document(history_id).get()
        if not history_doc.exists:
            return None

        history_data = history_doc.to_dict()

        return {
            "question": history_data.get("question"),
            "cards": history_data.get("cards"),
            "result": history_data.get("result"),
            "created_at": history_data.get("created_at")
        }

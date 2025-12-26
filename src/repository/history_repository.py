from typing import Optional
from firebase_admin import firestore
from google.cloud.firestore import FieldFilter

from src.model.history_model import HistoryModel
from src.utils.normalize import normalize_history_data

class HistoryRepository:
    def __init__(self):
        self.collection = firestore.client().collection("tarot_history")

    def save_tarot_reading(self, history: HistoryModel) -> str:
        """타로 리딩 결과 저장 후 document ID 반환"""
        _, doc_ref = self.collection.add(history.model_dump(exclude_none=True))
        return doc_ref.id
    
    def get_history(
        self,
        user_id: str,
        provider: str,
        limit: int = 5,
        cursor_doc_id: Optional[str] = None,
        ) -> tuple[list[tuple[str, bool, HistoryModel]], Optional[str]]:
        """
        히스토리 조회

        Returns:
            tuple: ([(doc_id, is_shared, HistoryModel), ...], next_cursor_doc_id)
        """
        query = (
            self.collection
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("provider", "==", provider))
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        if cursor_doc_id:
            doc_snapshot = self.collection.document(cursor_doc_id).get()
            if not doc_snapshot.exists:
                raise ValueError("Invalid cursor document ID.")
            query = query.start_after(doc_snapshot)

        docs = query.get()
        history_items = []
        for doc in docs:
            data = doc.to_dict()
            is_shared = data.get("is_shared", False)
            normalized_data = normalize_history_data(data)
            history_items.append((doc.id, is_shared, HistoryModel(**normalized_data)))

        return history_items, docs[-1].id if docs else None
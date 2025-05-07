from datetime import datetime
from typing import Optional
from firebase_admin import firestore
from google.cloud.firestore import FieldFilter

from model.history_model import HistoryModel
from utils.normalize import normalize_history_data

class HistoryRepository:
    def __init__(self):
        self.collection = firestore.client().collection("tarot_history")

    def save_tarot_reading(self, history: HistoryModel) -> None:
        self.collection.add(history.model_dump(exclude_none=True))
    
    def get_history(
        self, 
        user_id: str, 
        provider: str,
        limit: int = 5,
        cursor_doc_id: Optional[str] = None,
        ) -> list[HistoryModel]:
        
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
        history_models = []
        for doc in docs:
            data = normalize_history_data(doc.to_dict())
            history_models.append(HistoryModel(**data))

        return history_models, docs[-1].id if docs else None
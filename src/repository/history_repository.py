from datetime import datetime
from typing import Optional
from firebase_admin import firestore
from google.cloud.firestore import FieldFilter

from model.history_model import HistoryModel

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
        start_after_created_at: Optional[str] = None
        ) -> list[HistoryModel]:
        
        query = (
            self.collection
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("provider", "==", provider))
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        if start_after_created_at:
            try:
                dt = datetime.strptime(start_after_created_at, "%Y-%m-%d %H:%M:%S")
                query = query.start_after({"created_at": dt})
            except ValueError:
                raise ValueError("Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'.")
        
        docs = query.get()
        return [HistoryModel(**doc.to_dict()) for doc in docs]
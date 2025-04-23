from firebase_admin import firestore
from datetime import datetime
from model.history_model import HistoryModel
from typing import Optional

class HistoryRepository:
    def __init__(self):
        self.collection = firestore.client().collection("tarot_history")

    def save_tarot_reading(self, history: HistoryModel) -> None:
        self.collection.add(history.model_dump(exclude_none=True))
from src.repository.history_repository import HistoryRepository
from src.schema.tarot import HistoryItem, TarotCards
from src.schema.tarot import HistoryResponse


class HistoryService:
    def __init__(self, user_id:str, provider:str, cursor_doc_id:str, history_repository: HistoryRepository):
        self.user_id = user_id
        self.provider = provider
        self.cursor_doc_id = cursor_doc_id
        self.history_repository = history_repository

    def get_history(self):
        models, next_cursor_doc_id = self.history_repository.get_history(
            user_id=self.user_id, 
            provider=self.provider,
            limit=5,
            cursor_doc_id=self.cursor_doc_id,
        )
        
        items = [
            HistoryItem(
                question=history.question,
                cards=history.cards,
                result=history.result,
                created_at=history.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ) for history in models
        ]
        
        return HistoryResponse(
            history=items,
            next_cursor_doc_id=next_cursor_doc_id
        )
from repository.history_repository import HistoryRepository
from schema.tarot import HistoryItem


class HistoryService:
    def __init__(self, user_id:str, provider:str, history_repository: HistoryRepository):
        self.user_id = user_id
        self.provider = provider
        self.history_repository = history_repository

    def get_history(self):
        raw_history = self.history_repository.get_history(
            self.user_id, 
            self.provider
        )
        
        return [
            HistoryItem(
                question=history.question,
                cards=history.cards,
                result=history.result,
                created_at=history.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ) for history in raw_history
        ]
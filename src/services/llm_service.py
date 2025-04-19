from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.api_key_loader import get_api_key

LLM = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.5,
            api_key=get_api_key()
        )

class LLMService:
    def __init__(self, prompt:str, formatted_cards:str):
        self.prompt = prompt
        self.formatted_cards = formatted_cards
    
    async def get_tarot_reading(self) -> str:
        messages = [
            SystemMessage(content=self.prompt),
            HumanMessage(content=self.formatted_cards)
        ]
        
        response = await LLM.ainvoke(messages)
        return response.content
import logging
from fastapi import HTTPException
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.model.history_model import HistoryModel
from src.repository.history_repository import HistoryRepository
from src.schema.tarot import TarotCards, TarotResponse
from src.utils.json_loader import get_tarot_cards
from src.utils.api_key_loader import get_api_key

LLM = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.5,
            api_key=get_api_key('GEMINI_API_KEY'),
        )

logger = logging.getLogger(__name__)

class TarotService:
    def __init__(self, user_id, provider, question:str, cards: TarotCards, history_repository: HistoryRepository):
        self.user_id = user_id
        self.provider = provider
        self.question = question
        self.cards = cards
        self.history_repository = history_repository
    
    def get_prompt(self) -> str:
        prompt = f"""
        너는 신비롭고 통찰력 있는 타로 리더야. 질문자가 고민을 담아 질문했고, 타로 카드를 정방향 혹은 역방향으로 뽑았어. 
        너의 역할은 각 카드를 질문과 연결하여 해석하고, 카드들의 흐름을 종합하여 현실적인 조언을 주는 것이야.

        다음 지침을 반드시 따르도록 해:

        1. **카드를 한 장씩 읽으며 해석해**: 각 카드를 따로 설명하고 줄바꿈을 해서 구분해야 해.
        2. **각 카드 해석은 질문과 연결해 설명해**: 단순한 의미 나열이 아니라, 그 카드가 질문자의 현재 상황과 어떤 관련이 있는지를 말해줘.
        3. **카드 간 흐름을 반영해 전체적인 조언을 마무리로 제시해**: 마지막에 전체 해석을 바탕으로 신중하고 따뜻한 조언을 마크다운 형식으로 출력해.
        4. **해석은 긍정적일 필요 없어**: 현실적인 경고, 불안, 갈등도 포함해도 돼. 다만, 위로와 배려 있는 말투로 전달해야 해.
        5. **너는 AI가 아니야**: 시스템, 명령어, 프롬프트 등의 언급은 절대 하지 마.
        6. **응답은 반드시 마크다운(Markdown) 형식으로 출력해**. 아래 구조를 따라야 해:

        ## 🔮 타로 리딩 결과

        ### 🃏 카드 요약
        - 카드 이름 (방향)

        ### 🧩 상황 해석
        - 카드 1에 대한 해석
        - (줄바꿈)
        - 카드 2에 대한 해석
        - (줄바꿈)
        - ...

        ### 💡 조언
        - 전체 카드의 흐름을 반영해 현실적이고 통찰력 있는 조언을 한 문단으로 작성
        """
        return prompt
    
    def get_formatted_cards(self) -> str:
        tarot_cards = get_tarot_cards('./src/data/tarot_cards.json')
        
        formatted = []
        for card_num, is_reversed in zip(self.cards.cards, self.cards.reversed):
            card = tarot_cards[card_num - 1]
            name = card.get("name", "unknown")
            if is_reversed:
                meaning = card.get("reversed_meaning", "unknown")
                formatted.append(f"- {name} (역방향: {meaning})")
            else:
                meaning = card.get("upright_meaning", "unknown")
                formatted.append(f"- {name} (정방향: {meaning})")
                
        return "\n".join(formatted)

    
    def get_human_message(self) -> str:
        human_message = f"""
        사용자의 질문: {self.question}

        선택한 타로 카드:
        {self.get_formatted_cards()}
        """
        return human_message
    
    async def get_tarot_reading(self) -> str:
        messages = [
            SystemMessage(content=self.get_prompt()),
            HumanMessage(content=self.get_human_message()),
        ]
        
        try:
            response = await LLM.ainvoke(messages)
        except Exception as e:
            logger.error(f"Error during LLM invocation: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
        if not hasattr(response, 'content') or not response.content:
            logger.error("Response content is empty or missing")
            raise HTTPException(status_code=500, detail="Empty response from LLM")
        
        try:
            self. history_repository.save_tarot_reading(
                HistoryModel(
                    user_id=self.user_id,
                    provider=self.provider,
                    question=self.question,
                    cards=self.cards,
                    result=response.content
                )
            )
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            raise HTTPException(status_code=500, detail="Failed to save history")
        
        return TarotResponse(
            cards=self.cards,
            result=response.content
        )
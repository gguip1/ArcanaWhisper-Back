from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.llm_service import LLMService
from services.tarot_service import TarotPromptService
from schema.tarot import TarotRequest, TarotResponse

app = FastAPI(docs_url='/docs')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/tarot", response_model=TarotResponse)
async def get_tarot_reading(request: TarotRequest):
    tarotPromptService = TarotPromptService(selected_cards=request.cards)
    prompt = tarotPromptService.get_prompt()
    formatted_cards = tarotPromptService.get_formatted_cards()
    
    llmService = LLMService(prompt=prompt, formatted_cards=formatted_cards)
    result = await llmService.get_tarot_reading()
    
    return {
        "message": "타로 리딩 결과입니다.",
        "cards": request.cards,
        "result": result
    }
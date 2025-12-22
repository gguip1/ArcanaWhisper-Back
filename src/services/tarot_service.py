import logging
import os
import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.model.history_model import HistoryModel
from src.repository.history_repository import HistoryRepository
from src.schema.tarot import TarotCards, TarotResponse
from src.utils.json_loader import get_tarot_cards
from src.utils.api_key_loader import get_api_key

logger = logging.getLogger(__name__)

# Lambda 호환 경로 설정
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(SRC_DIR, "data")
PROMPTS_DIR = os.path.join(SRC_DIR, "prompts")
TAROT_CARDS_PATH = os.path.join(DATA_DIR, "tarot_cards.json")

# 프롬프트 SSM 경로 또는 로컬 파일 경로
SYSTEM_PROMPT_SSM_PARAM = os.environ.get("TAROT_SYSTEM_PROMPT_PARAM")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "tarot_system.txt")

# 프롬프트 인젝션 방어 패턴
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions?",
    r"disregard\s+(previous|above|all)\s+instructions?",
    r"forget\s+(previous|above|all)\s+instructions?",
    r"you\s+are\s+now\s+(?:a|an)\s+",
    r"new\s+instructions?:",
    r"system\s*prompt",
    r"act\s+as\s+(?:a|an)\s+",
    r"pretend\s+(?:to\s+be|you\s+are)",
    r"reveal\s+(?:your|the)\s+(?:instructions?|prompt|system)",
    r"무시\s*(?:해|하고|하세요)",
    r"새로운\s*지시",
    r"시스템\s*프롬프트",
    r"너는\s*이제\s*",
]

def _get_from_ssm(param_name: str) -> str:
    """AWS Systems Manager Parameter Store에서 값 로드"""
    import boto3
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def _load_system_prompt() -> str:
    """시스템 프롬프트를 SSM 또는 파일에서 로드합니다."""
    # 1. SSM Parameter Store에서 로드 (Lambda 환경)
    if SYSTEM_PROMPT_SSM_PARAM:
        try:
            prompt = _get_from_ssm(SYSTEM_PROMPT_SSM_PARAM)
            logger.info(f"Loaded system prompt from SSM: {SYSTEM_PROMPT_SSM_PARAM}")
            return prompt
        except Exception as e:
            logger.warning(f"Failed to load prompt from SSM: {e}, trying file...")

    # 2. 파일에서 로드 (로컬 테스트용)
    try:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            logger.info(f"Loaded system prompt from file: {SYSTEM_PROMPT_PATH}")
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"System prompt not found in SSM or file: {SYSTEM_PROMPT_PATH}")
    except Exception as e:
        raise RuntimeError(f"Failed to load system prompt: {e}")

# 프롬프트 캐싱 (Cold start 최적화)
_CACHED_SYSTEM_PROMPT = None

def get_system_prompt() -> str:
    """캐싱된 시스템 프롬프트를 반환합니다."""
    global _CACHED_SYSTEM_PROMPT
    if _CACHED_SYSTEM_PROMPT is None:
        _CACHED_SYSTEM_PROMPT = _load_system_prompt()
    return _CACHED_SYSTEM_PROMPT

def sanitize_user_input(text: str) -> str:
    """사용자 입력에서 프롬프트 인젝션 시도를 제거합니다."""
    sanitized = text
    for pattern in INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)
    return sanitized

def detect_injection_attempt(text: str) -> bool:
    """프롬프트 인젝션 시도를 감지합니다."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False

LLM = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.5,
            api_key=get_api_key('GEMINI_API_KEY'),
        )


class TarotService:
    def __init__(self, user_id, provider, question:str, cards: TarotCards, history_repository: HistoryRepository):
        self.user_id = user_id
        self.provider = provider
        self.question = question
        self.cards = cards
        self.history_repository = history_repository
    
    def get_prompt(self) -> str:
        """캐싱된 시스템 프롬프트를 반환합니다."""
        return get_system_prompt()
    
    def get_formatted_cards(self) -> str:
        tarot_cards = get_tarot_cards(TAROT_CARDS_PATH)
        
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
        """사용자 메시지를 생성합니다. 프롬프트 인젝션 방어가 적용됩니다."""
        # 프롬프트 인젝션 감지 및 sanitize
        safe_question = sanitize_user_input(self.question)

        if detect_injection_attempt(self.question):
            logger.warning(f"Potential prompt injection detected: {self.question[:100]}...")

        human_message = f"""[TAROT READING REQUEST]

Question: {safe_question}

Selected Cards:
{self.get_formatted_cards()}

[END OF REQUEST]"""
        return human_message
    
    async def get_tarot_reading(self) -> str:
        messages = [
            SystemMessage(content=self.get_prompt()),
            HumanMessage(content=self.get_human_message()),
        ]

        try:
            # 동기 API 사용 (Lambda event loop 재사용 문제 해결)
            response = LLM.invoke(messages)
        except Exception as e:
            logger.error(f"Error during LLM invocation: {e}")
            raise RuntimeError("LLM invocation failed") from e

        if not hasattr(response, 'content') or not response.content:
            logger.error("Response content is empty or missing")
            raise RuntimeError("Empty response from LLM")

        try:
            self.history_repository.save_tarot_reading(
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
            raise RuntimeError("Failed to save history") from e
        
        return TarotResponse(
            cards=self.cards,
            result=response.content
        )
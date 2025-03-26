import streamlit as st
import json

# Lottie JSON 로드
def load_lottie_json(path):
    with open(path, "r") as f:
        return json.load(f)

st.set_page_config(
    page_title='Arcana Whisper',
    page_icon='🔮',
    layout='centered',
)

if 'selected_card' not in st.session_state:
    st.switch_page('app.py')
if len(st.session_state.selected_card[1:]) < 3:
    st.switch_page('app.py')

# LangChain 관련
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

# 환경변수 로드
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("Gemini_API_KEY")

def get_llm(provider: str):
    if provider == "gemma3:1b":
        return ChatOllama(model = "gemma3:1b")
    elif provider == "gemma3:4b":
        return ChatOllama(model = "gemma3:4b")
    elif provider == "gemini-2.0-flash-lite":
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.5,
            api_key=GEMINI_API_KEY
        )

def format_cards(selected_cards: list[dict]) -> str:
    formatted = []
    for card in selected_cards:
        name = card['name']
        meaning = card['meaning']
        formatted.append(f"- {name} ({meaning})")
    return "\n".join(formatted)

def getPrompt(formatted_cards: str) -> str:
    prompt = f"""
        (서론 없이 바로 카드 해석 시작 (출력 X))
        (필요시 자연스럽게 반말 섞어서 친근감 UP (출력x))
        
        ## 🧭 핵심 포인트 요약 (3줄)

        1. **[현재 에너지]**: 5단어 내외로 진단  
        2. **[당장 필요한 것]**: 7단어 내외 조언  
        3. **[경고 사항]**: 7단어 내외 주의점

        ---

        ## 🪄 각 카드의 숨겨진 메시지

        [카드 이름]  
        - **좋은 신호**: 친구처럼 편하게 말하는 긍정 요소  
        - **살짝 주의**: 속삭이듯 전하는 경고 메시지  
        - **활용법**: "~하면 금방 효과 볼 수 있어요" 형식

        ---

        ## 🕰️ 흐름 읽기 (시간선)

        **▶️ 과거 → 현재 → 가까운 미래**

        - **어제의 너**: 과거의 영향력  
        - **오늘의 너**: 현재의 결정적 요인 
        - **내일의 너**: 예측 가능한 미래

        ---

        ## 🔀 카드들의 조합 케미

        - **최강 콜라보**: 시너지 카드 2장 → *"이 두 개가 같이 나오면…"*  
        - **살짝 충돌**: 상충되는 카드 → *"여기서 고민이 생길 수 있어요."*

        ---

        ## 🎯 실전 행동 매뉴얼

        ✅ **당장 할 일**  
        - **3일 안에**: 구체적인 행동 1가지 → *"이거 하나만 먼저 해보세요."*  
        - **1주일 내**: 두 번째 행동 → *"효과를 보려면 이렇게 해보세요."*

        ⛔ **절대 금지**  
        - *"[특정 행동]은 정말 안 돼요!"*  
        - *"이런 사람은 피하시고…"*

        ---

        (마지막 객관적인 평가 또는 조언으로 마무리 (출력x))
        """
    return prompt
    
def run_tarot_reading(selected_cards: list[dict], provider="gemma3:1b"):
    llm = get_llm(provider)
    
    formatted_cards = format_cards(selected_cards)
    
    # prompt = ChatPromptTemplate.from_messages([
    #     ('system', getPrompt(formatted_cards)),
    # ])
    # chain = prompt | llm | StrOutputParser()
    
    messages = [SystemMessage(content=getPrompt(formatted_cards)),
                HumanMessage(content=f"{formatted_cards}")]
    response = llm.invoke(messages)
    
    return response.content

# 스타일
from ui.common_style import common_style
common_style()

st.markdown("<h1 class='centered'>🔮 Arcana Whisper</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='centered'>🃏 당신이 뽑은 카드</h3>", unsafe_allow_html=True)

cols = st.columns([1, 1, 1], vertical_alignment='center')

with cols[0]:
    st.markdown(f'''<h3 class='centered'>{st.session_state.selected_card[1]['name']}</h3>''', unsafe_allow_html=True)
    st.image(st.session_state.selected_card[1]['img'])
with cols[1]:
    st.markdown(f'''<h3 class='centered'>{st.session_state.selected_card[2]['name']}</h3>''', unsafe_allow_html=True)
    st.image(st.session_state.selected_card[2]['img'])
with cols[2]:
    st.markdown(f'''<h3 class='centered'>{st.session_state.selected_card[3]['name']}</h3>''', unsafe_allow_html=True)
    st.image(st.session_state.selected_card[3]['img'])

cols = st.columns([1, 1, 1])

with cols[1]:
    with st.spinner("", show_time=True):
        print('Info | Run tarot reading...')
        print('Info | Selected cards:')
        for card in st.session_state.selected_card[1:]:
            print(f'Info | - {card["name"]} ({card["meaning"]})')
        result = run_tarot_reading(st.session_state.selected_card[1:], provider="gemini-2.0-flash-lite")

st.markdown(f'''{result}''')

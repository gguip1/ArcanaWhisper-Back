import streamlit as st
import json

from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def load_lottie_json(path):
    with open(path, "r") as f:
        return json.load(f)

def get_llm(provider: str = "ollama"):
    if provider == "ollama":
        return Ollama(model = "gemma3:1b")

def format_cards_for_prompt(cards: list[dict]) -> str:
    return "\n".join([f"- {card['name']} ({card['meaning']})" for card in cards])

def run_tarot_reading(selected_cards: list[dict], provider="ollama"):
    llm = get_llm(provider)
    tarot_prompt = PromptTemplate.from_template("""
        당신은 신비롭고 지혜로운 타로 마스터입니다.

        아래는 사용자가 뽑은 타로 카드 목록입니다:

        {cards}

        각 카드의 의미를 분석하고, 카드들 간의 흐름과 조화를 바탕으로 사용자의 현재 상황, 내면의 흐름, 가까운 미래를 예측해 주세요.

        **출력 형식은 아래와 같이 Markdown 스타일로 작성해주세요:**

        ## 🃏 선택한 카드 소개
        - 카드 1: 의미 요약
        - 카드 2: 의미 요약
        - 카드 3: 의미 요약

        ## 🔍 해석과 통찰
        ### 현재 상황
        - 카드들과 연관된 사용자의 현재 상태를 설명

        ### 내면의 흐름
        - 감정적/정신적인 흐름에 대한 통찰

        ### 가까운 미래
        - 예측 가능한 변화나 흐름

        ## ✨ 한 줄 조언
        - 핵심 메시지를 명확하고 인상 깊게 전달 (짧고 강렬하게)
    """)
    chain = LLMChain(llm=llm, prompt=tarot_prompt)

    formatted = format_cards_for_prompt(selected_cards)
    response = chain.run(cards=formatted)

    return response

def render(setPage):
    st.markdown(
        """
        <style>
            body {
                background-color: #1e1e2f;
                color: #f0e6f6;
            }
            .centered {
                text-align: center;
            }
            .stButton>button {
                background-color: #6a0dad;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-weight: bold;
            }
            .stButton {
                display: flex;
                justify-content: center;
            }
            .stAlert {
                display: flex;
                justify-content: center;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    cards = st.session_state.selected_card[1:]  # 첫 카드는 특수 처리 중이라면 제외
    
    placeholder = st.empty()

    # 로딩 메시지 정중앙에 표시
    placeholder.markdown(
        """
        <div style='
            height: 80vh;
            display: flex;
            align-items: center;
            justify-content: center;
        '>
            <p style='
                font-size: 20px;
                color: #AAAAAA;
                text-align: center;
            '>
                잠시 숨을 고르며,<br>당신을 위한 운명의 메시지를 준비하고 있어요...
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 로딩 중 처리
    with st.spinner("", show_time=True):
        result = run_tarot_reading(cards)

    # 로딩 메시지 제거
    placeholder.empty()
    
    st.markdown(f'''{result}''')

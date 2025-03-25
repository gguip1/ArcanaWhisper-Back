import streamlit as st
import random
import json

@st.cache_data
def loadCards():
    with open('data/tarot_cards.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_lottie_json(path):
    with open(path, "r") as f:
        return json.load(f)

from streamlit_image_select import image_select
from streamlit_lottie import st_lottie

BACK_IMAGE = './data/images/tarot_back/tarot_back.webp'
CARD_DATA = loadCards()

def initialize_state():
    if "card_order" not in st.session_state:
        st.session_state.card_order = list(range(22))
        random.shuffle(st.session_state.card_order)
    
    if "card_pool" not in st.session_state:
        st.session_state.card_pool = [
            {"img": BACK_IMAGE, "id": card_id} for card_id in st.session_state.card_order
        ]

    if "selected_card" not in st.session_state:
        st.session_state.selected_card = []
    
def render(setPage):
    initialize_state()

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
    
    if st.session_state.card_pool and len(st.session_state.selected_card) < 4:
        
        st.markdown(
            f'''
            ## 🃏 세 장의 카드를 고르세요.  
            <br>

            **남은 카드: {3 - len(st.session_state.selected_card)}장**
            ''',
            unsafe_allow_html=True
        )
        
        selected = image_select(
            label="",
            images=[card["img"] for card in st.session_state.card_pool],
        )
        
        if selected and len(st.session_state.selected_card) < 4:
            for i, card in enumerate(st.session_state.card_pool):
                if card["img"] == selected:
                    selected_card_data = CARD_DATA[card["id"]]
                    st.session_state.selected_card.append(selected_card_data)
                    st.session_state.card_pool.pop(i)
                    break
        
        if len(st.session_state.selected_card) == 4:
            st.rerun()
    
    if len(st.session_state.selected_card) == 4:
        # cols = st.columns([1, 1, 1])
        
        # for i, card in enumerate(st.session_state.selected_card[1:]):
        #     with cols[i]:
        #         st.image(card["img"], width=200)
        #         st.write(card["name"])
        
        st.markdown("<h1 class='centered'>🔮 Arcana Whisper</h1>", unsafe_allow_html=True)
        
        lottie_animation = load_lottie_json('./data/lottie/Animation - 1742911210963.json')
        st_lottie(lottie_animation, height=300, loop=True)
        
        # st.markdown(
        #     "<p style='text-align:center; font-size:18px; color:#AAAAAA;'>"
        #     "잠시 숨을 고르며, 당신을 위한 운명의 메시지를 준비하고 있어요..."
        #     "</p>",
        #     unsafe_allow_html=True
        # )
        
        cols = st.columns([1, 1, 1, 1])
        
        with cols[1]:
            if st.button("✨ 운명의 메시지 확인하기 ✨"):
                setPage('result')
                # st.rerun()
        
        with cols[2]:
            if st.button("🔄 다시 뽑기"):
                setPage('tarot')
                st.session_state.card_order = list(range(22))
                random.shuffle(st.session_state.card_order)
            
                st.session_state.card_pool = [
                    {"img": BACK_IMAGE, "id": card_id} for card_id in st.session_state.card_order
                ]

                st.session_state.selected_card = []
import streamlit as st
import json
import random

# Card Json 로드
@st.cache_data
def loadCards():
    with open('data/tarot_cards.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Lottie JSON 로드
def load_lottie_json(path):
    with open(path, "r") as f:
        return json.load(f)

from streamlit_image_select import image_select
from streamlit_lottie import st_lottie

BACK_IMAGE = './data/images/tarot_back/tarot_back.webp'
CARD_DATA = loadCards()

st.set_page_config(
    page_title='Arcana Whisper',
    page_icon='🔮',
    layout='wide'
)

from ui.common_style import common_style

# 스타일
common_style()

# Session State 초기화
if "card_order" not in st.session_state:
    st.session_state.card_order = list(range(22))
    random.shuffle(st.session_state.card_order)

if "card_pool" not in st.session_state:
    st.session_state.card_pool = [
        {"img": BACK_IMAGE, "id": card_id} for card_id in st.session_state.card_order
    ]

if "selected_card" not in st.session_state:
    st.session_state.selected_card = []

# 카드 선택
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

# 카드 선택 완료
if len(st.session_state.selected_card) == 4:
    st.markdown("<h1 class='centered'>🔮 Arcana Whisper</h1>", unsafe_allow_html=True)
        
    lottie_animation = load_lottie_json('./data/lottie/Animation - 1742911210963.json')
    st_lottie(lottie_animation, height=300, loop=True)
    
    cols = st.columns([1, 1, 1, 1])
        
    with cols[1]:
        if st.button("✨ 운명의 메시지 확인하기 ✨"):
            st.switch_page('pages/result.py')
    
    with cols[2]:
        if st.button("🔄 다시 뽑기"):
            st.session_state.selected_card = []
            
            st.session_state.card_order = list(range(22))
            random.shuffle(st.session_state.card_order)
        
            st.session_state.card_pool = [
                {"img": BACK_IMAGE, "id": card_id} for card_id in st.session_state.card_order
            ]
            
            st.switch_page('pages/tarot.py')
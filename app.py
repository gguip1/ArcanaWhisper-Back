import streamlit as st
from st_clickable_images import clickable_images
import os
from random import shuffle
import tarot_with_llm

# 페이지 설정
st.set_page_config(
    page_title='Daily ARCANA', 
    page_icon='👋', 
    layout='wide',
)

# CSS
st.markdown("""
    <style>
        div > img{
            border-radius: 6px
        }
    </style>
""", unsafe_allow_html=True)

imgs_path = os.getcwd() +  '/resource/images/tarot_/'
imgs_list = os.listdir(imgs_path)

#중복 체크
def dup_check(list, checking_value):
    for content in list:
        if checking_value == content:
            return True
    return False

if "card" not in st.session_state:
    shuffle(imgs_list)
    st.session_state.card = imgs_list

if "selected_card" not in st.session_state:
    st.session_state.selected_card = []

st.title('타로')

with st.container(border=True):
    st.markdown('<h3 class="center-title">카드를 선택해주세요.</h3>', unsafe_allow_html=True)
    clicked = clickable_images(
        [
            "https://i.pinimg.com/564x/c0/77/76/c0777662cc623d7203c995e10c213090.jpg"
        ] * len(imgs_list),
        div_style={
            "display": "flex",
            "flex-wrap": "nowrap",
            "justify-content": "center",
            "align-items": "center",
            "padding": "20px",
            "width": "100%",
            "position": "relative"
        },
        img_style={
            "height": "200px",
            "position": "relative",
            "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
            "transition": "transform 0.2s",
        },
    )

if clicked != -1 and len(st.session_state.selected_card) < 3:
    if not dup_check(st.session_state.selected_card, st.session_state.card[clicked]):
        st.session_state.selected_card.append(st.session_state.card[clicked])
    else:
        st.toast('중복 카드입니다.')

if len(st.session_state.selected_card) == 3:
    st.toast('더이상 선택할 수 없습니다.')

if st.session_state.selected_card:
    imgs_cols = st.columns(3)
    
    if len(st.session_state.selected_card) > 0:
        with imgs_cols[0]:
            with st.container(border=True):
                st.markdown('<h3 class="center-title">첫번째 카드</h3>', unsafe_allow_html=True)
                st.image(imgs_path + st.session_state.selected_card[0], use_column_width=True)
    
    if len(st.session_state.selected_card) > 1:
        with imgs_cols[1]:
            with st.container(border=True):
                st.markdown('<h3 class="center-title">두번째 카드</h3>', unsafe_allow_html=True)
                st.image(imgs_path + st.session_state.selected_card[1], use_column_width=True)
    
    if len(st.session_state.selected_card) > 2:
        with imgs_cols[2]:
            with st.container(border=True):
                st.markdown('<h3 class="center-title">세번째 카드</h3>', unsafe_allow_html=True)
                st.image(imgs_path + st.session_state.selected_card[2], use_column_width=True)

if st.button('운명 확인하기'):
    with st.spinner('운명 확인중...'):
        if 'selected_card' in st.session_state:
            response = tarot_with_llm.sonnet_respone('오늘의 운세', st.session_state.selected_card)
            st.write(response)
        else:
            st.write("카드를 선택하지 않았습니다.")

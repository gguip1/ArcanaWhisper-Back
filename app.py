import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title='타로 서비스(가제)', 
    page_icon='👋', 
    layout='wide',
    initial_sidebar_state="collapsed"
)

from st_clickable_images import clickable_images

import uuid
from streamlit_cookies_manager import EncryptedCookieManager

import os
from random import shuffle

import tarot_with_llm
import db_logics

# 쿠키 관리
cookies = EncryptedCookieManager(password="7554")

if not cookies.ready():
    st.stop()

# 유저 식별을 위한 쿠키 생성 및 저장
if "identifier" not in cookies:
    identifier = str(uuid.uuid4())
    cookies["identifier"] = identifier
    cookies.save()  # 쿠키를 저장

print(f"식별자 : {cookies['identifier']}")

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

with st.container(border=True):
    st.header('Step 1. 타로를 보기 위해 정보를 입력해주세요.')
    st.divider()
    input_cols = st.columns(2)
    with input_cols[0]:
        tarot_reader = st.selectbox(label="선생 고르기",
                    options=['llama3.1:8b', 'cluade sonnet 3.5'],
                    index=None)
    with input_cols[1]:
        tarot_type = st.selectbox(label="종목",
                    options=['오늘의 운세', '신년'],
                    index=None)
    
    if tarot_reader and tarot_type:
        st.markdown('<h3 class="center-title">카드를 선택해주세요.</h3>', unsafe_allow_html=True)
        clicked = clickable_images(
            [
                "https://i.pinimg.com/564x/c0/77/76/c0777662cc623d7203c995e10c213090.jpg"
            ] * len(imgs_list),
            # titles=[f"Image #{str(i)}" for i in range(22)],
            div_style={
                # "border": "1px solid black",
                "border-radius" 
                "box-shadow": "3px 3px 3px 3px",
                "display": "flex",
                "flex-wrap": "nowrap",
                # "overflow-x": "auto",  # 가로로 스크롤 가능하게 설정
                "justify-content": "center",
                "align-items": "center",
                "padding": "20px",
                "width": "100%",
                "position": "relative"
            },
            img_style={
                "display": "flex",
                "height": "200px",
                # "z-index": "1",
                # "position": "relative",
                "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                "transition": "transform 0.2s",  # 호버 시 애니메이션 추가
            },
        )
        # st.markdown(f"Image #{clicked} clicked" if clicked > -1 else "No image clicked")
        if clicked != -1 and len(st.session_state.selected_card) < 3:
            if not dup_check(st.session_state.selected_card, st.session_state.card[clicked]): # 카드 중복 체크
                st.session_state.selected_card.append(st.session_state.card[clicked])
            else:
                st.toast('중복 카드입니다.')
    # if len(st.session_state.selected_card) == 3:
#     st.toast('더이상 선택할 수 없습니다.')

    if st.session_state.selected_card:
        st.divider()
        imgs_cols = st.columns(3)
        
        # 첫 번째 카드가 있는지 확인하고 이미지 출력
        if len(st.session_state.selected_card) > 0:
            with imgs_cols[0]:
                st.markdown('<h3 class="center-title">첫번째 카드</h3>', unsafe_allow_html=True)
                st.image(imgs_path + st.session_state.selected_card[0], use_column_width=True)
        
        # 두 번째 카드가 있는지 확인하고 이미지 출력
        if len(st.session_state.selected_card) > 1:
            with imgs_cols[1]:
                st.markdown('<h3 class="center-title">두번째 카드</h3>', unsafe_allow_html=True)
                st.image(imgs_path + st.session_state.selected_card[1], use_column_width=True)
        
        # 세 번째 카드가 있는지 확인하고 이미지 출력
        if len(st.session_state.selected_card) > 2:
            with imgs_cols[2]:
                st.markdown('<h3 class="center-title">세번째 카드</h3>', unsafe_allow_html=True)
                st.image(imgs_path + st.session_state.selected_card[2], use_column_width=True)
    if len(st.session_state.selected_card) == 3:
        button_cols = st.columns(4,vertical_alignment="center",gap="large")
        with button_cols[1]:
            if st.button('운명 확인하기', use_container_width=True):
                with st.spinner('운명 확인중...'):
                    # st.session_state에 selected_card가 있는지 확인 필요
                    if 'selected_card' in st.session_state:
                        response = tarot_with_llm.tarot_response(tarot_reader, tarot_type, st.session_state.selected_card) 
                        # response = tarot_with_llm.ollama_response('오늘의 운세', st.session_state.selected_card) # 자체 ollama 서버
                        # response = tarot_with_llm.sonnet_respone('오늘의 운세', st.session_state.selected_card) # 클라우드
                        
                        if response:
                            st.write(response)
                            db_logics.insert_tarot_result(cookies['identifier'], tarot_reader, tarot_type, response)
                        else:
                            st.write('서버 상태를 확인해 보세요')
                            
                    else:
                        st.write("카드를 선택하지 않았습니다.")
        with button_cols[2]:
            st.button('초기화', use_container_width=True)

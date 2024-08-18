import streamlit as st
import os

# 페이지 설정
st.set_page_config(
    page_title='타로 서비스(가제)', 
    page_icon='👋', 
    layout='wide',
)

if "content" not in st.session_state:
    st.session_state.content = None

if "selected_card" not in st.session_state:
    st.session_state.selected_card = []

imgs_path = os.getcwd() +  '/resource/images/tarot_/'

st.markdown(
    """
<style>
.stButton > button {
    display: absolute;
    background-color: red;
    height: 120px;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

def select_content():
    st.session_state.content = st.session_state['content']

with st.container():
    options = ['오늘의 운세', '1년 운세']
    content = st.selectbox(
        '어떤 고민이 있으신가요?', 
        options=options,
        index=None,
        on_change=select_content,
        key='content'
        )
    if content:
        imgs_list = os.listdir(imgs_path)
        cols = st.columns(len(imgs_list))
        for i, col in enumerate(cols):
            if col.button('', key=f'{imgs_list[i]}', use_container_width=True):
                if len(st.session_state.selected_card) < 3:
                    st.session_state.selected_card.append(imgs_list[i].replace('.jpg', ''))
                else:
                    st.toast('최대 갯수 초과')

def initialize():
    st.write(st.session_state.content)
    st.write(st.session_state.selected_card)
    st.session_state.selected_card = []

st.button('초기화', on_click=initialize)

with st.container():
    if st.session_state.selected_card:
        cols = st.columns(len(st.session_state.selected_card))
        for i, col in enumerate(cols):
            col.image(imgs_path + st.session_state.selected_card[i] + '.jpg')

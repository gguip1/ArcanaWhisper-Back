import os
import streamlit as st
from streamlit_image_select import image_select
from random import shuffle

# 페이지 설정
st.set_page_config(
    page_title='타로 서비스(가제)', 
    page_icon='👋', 
    layout='wide',
)

# 페이지 제목 설정
st.title('타로 서비스(가제)')

# 타로 이미지 리소스 경로 설정
imgs_path = 'resource/images/tarot_/'
tarot_back_img_path = 'resource/images/tarot_back/tarot_back.jpg'

# 타로 이미지 파일 목록 가져오기
imgs_list = os.listdir(imgs_path)

# 타로 카드 뒷면 이미지 생성
tarot_back_imgs = [tarot_back_img_path] * len(imgs_list)

# 세션 초기화 및 관리
if "selected_imgs" not in st.session_state:
    st.session_state.selected_imgs = []

if "imgs" not in st.session_state:
    st.session_state.imgs = []
    shuffle(imgs_list)
    st.session_state.imgs = [os.path.join(imgs_path, img) for img in imgs_list]

if "run_button" not in st.session_state:
    st.session_state.run_button = True
if "run_button_clicked" not in st.session_state:
    st.session_state.run_button_clicked = False

# 이미지 선택 영역
with st.container(border=True):
    selected_img_index = image_select(
        label="",
        images=tarot_back_imgs,
        return_value="index",
        use_container_width=False,
    )

# 선택한 이미지 추가
session_imgs = st.session_state.imgs
session_selected_imgs = st.session_state.selected_imgs

if selected_img_index is not None:  # 이미지 선택 시에만 추가
    session_selected_imgs.append(session_imgs[selected_img_index])

# 선택된 이미지 표시 영역
selected_imgs_cols = st.columns(6)
for idx, img_path in enumerate(session_selected_imgs[1:4], start=0):  # 선택된 이미지 3장 표시
    with selected_imgs_cols[idx * 2]:  # 1열씩 띄워서 표시
        with st.container(border=True):
            st.image(img_path, use_column_width=True)

# 버튼 클릭 핸들러
def run_button_clicked():
    st.session_state.run_button = True
    with st.spinner('확인하는 중...'):
        st.write(session_selected_imgs[1:4])
    

# 선택된 이미지가 4장일 경우 버튼 활성화
if len(session_selected_imgs) == 4:
    st.session_state.run_button = False

# 운명 확인하기 버튼
st.button('운명 확인하기', on_click=run_button_clicked, disabled=st.session_state.run_button)

# LLM 통합 (주석처리된 부분)
# if st.session_state.run_button_clicked:
#     with st.spinner('In progress..'):
#         st.markdown(llama_LLM.response(st.session_selected_imgs[1], st.session_selected_imgs[2], st.session_selected_imgs[3]))

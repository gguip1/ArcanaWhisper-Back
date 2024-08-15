import os
import streamlit as st
from streamlit_image_select import image_select
from random import shuffle

st.set_page_config(layout='wide') # Wide 모드 설정

st.title('타로 서비스(가제)') # 제목
st.write('\n') # 간격

imgs_label = ''
imgs_path = 'resource\images\\tarot_\\' ## 타로 이미지 리소스 다운로드 필요
imgs_list = os.listdir(imgs_path)

tarot_back_img_path = 'resource\images\\tarot_back\\tarot_back.jpg' ## 타로 뒷면 이미지 다운로드 필요

if "selected_imgs_paths" not in st.session_state:
    st.session_state.selected_imgs_paths = []

if "imgs_paths" not in st.session_state:
    st.session_state.imgs_paths = []
    shuffle(imgs_list)
    for img in imgs_list:
        st.session_state.imgs_paths.append(os.path.join(imgs_path, img))


tarot_back_imgs = [tarot_back_img_path]
tarot_back_imgs = tarot_back_imgs * len(imgs_list)
    
session_imgs = st.session_state.imgs_paths
session_selected_imgs = st.session_state.selected_imgs_paths

imgs = image_select(
    label="",
    images=tarot_back_imgs,
    # captions=session_imgs,
    return_value="index",
    use_container_width=False,
)

index = int(str(imgs)[:100])

if len(st.session_state.selected_imgs_paths) < 4:
    session_selected_imgs.append(session_imgs[index])
    # session_imgs.remove(str(imgs)[:100])    

if "selected_imgs_paths" in st.session_state:
    st.title('선택된 카드')

cols = st.columns(3)
if len(session_selected_imgs) > 1:
    with cols[0]:
        st.image(session_selected_imgs[1], use_column_width=True)
    if len(session_selected_imgs) > 2:
        with cols[1]:
            st.image(session_selected_imgs[2], use_column_width=True)
        if len(session_selected_imgs) > 3:
            with cols[2]:
                st.image(session_selected_imgs[3], use_column_width=True)

# st.write("Comment")
# """
#     streamlit_image_select 라이브러리를 이용
#     이미지와 선택된 이미지 session을 설정함.
#     이미지를 클릭하게 되면 이미지 session에서는 지워지고 선택된 이미지 session에 추가되는 형태
#     하지만 현재 이미지 session을 지우게 되면 새로고침이 이루어지게 되고 이미지는 지워지지만 선택된 이미지가 가장 처음 이미지로만 선택되는 이슈
# """
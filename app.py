import os
import streamlit as st
# from streamlit_image_select import image_select
from random import shuffle

st.set_page_config(layout='wide') # Wide 모드 설정

st.title('타로 서비스(가제)') # 제목
st.write('\n') # 간격

imgs_label = ''
imgs_path = 'resource\images\\tarot_\\'
imgs_list = os.listdir(imgs_path)

imgs_paths = [os.path.join(imgs_path, img) for img in imgs_list]

# imgs_paths 랜덤 shuffle
shuffle(imgs_paths) 

# 한 줄에 표시할 이미지 수
num_per_row = 11

# 이미지들을 두 줄로 나누기
rows = [imgs_paths[i:i + num_per_row] for i in range(0, len(imgs_paths), num_per_row)]

for row in rows:
    cols = st.columns(len(row))
    for i, img_path in enumerate(row):
        with cols[i]:
            st.image(img_path, use_column_width=True)
'''
    현재는 카드 이미지가 보이고 있지만 카드 뒷면이 보이도록 수정 예정
    타로 진행 중 session으로 imgs_paths 저장 필요
    타로 진행이 종료되거나 중간에 취소시 session 초기화
'''

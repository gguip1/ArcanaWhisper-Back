import os
import ast
import streamlit as st

st.set_page_config('안뇽', layout='wide') # Wide 모드 설정

from streamlit_image_select import image_select
from streamlit_cookies_controller import CookieController
from random import shuffle

# 쿠키 컨트롤러
controller = CookieController()

st.title('타로 서비스(가제)') # 제목
st.write('\n') # 간격

imgs_label = ''
imgs_path = 'resource\images\\tarot_\\'
imgs_list = os.listdir(imgs_path)

cookies = controller.getAll()

# imgs_paths 초기화
if "imgs_paths" not in cookies:
    imgs_paths = [os.path.join(imgs_path, img) for img in imgs_list]
    shuffle(imgs_paths)
    controller.set('imgs_paths', imgs_paths)

st.write(cookies.get("imgs_paths"))

# selected_img_paths 초기화
if "selected_img_paths" not in cookies:
    controller.set('selected_imgs_paths', [])

imgs_paths = controller.get('imgs_paths')
selected_img_paths = controller.get('selected_imgs_paths')

imgs = image_select(
    label="",
    images=imgs_paths,
    # captions=imgs_paths,
    use_container_width=False,
)

selected_img = str(imgs)[:100]
print(selected_img)
selected_img_paths.append(str(imgs)[:100])

imgs_paths.remove(str(imgs)[:100])

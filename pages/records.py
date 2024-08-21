import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(
    page_title='타로 서비스(가제)', 
    page_icon='👋', 
    layout='wide',
    initial_sidebar_state="collapsed"
)

import db_logics

st.session_state.selected_card = []

# 쿠키 관리
cookies = EncryptedCookieManager(password="7554")

if not cookies.ready():
    st.stop()

print(f"식별자 : {cookies['identifier']}")

st.write(db_logics.select_tarot_result(cookies['identifier']))
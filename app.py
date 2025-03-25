import streamlit as st

st.set_page_config(
    page_title='Arcana Whisper',
    page_icon='🔮',
    layout='wide',
)

from page import index, tarot, result

# params = st.query_params
# page = params.get('page', 'index')

# def setPage(pageName):
#     st.query_params['page'] = pageName

if 'page' not in st.session_state:
    st.session_state.page = 'index'

def setPage(pageName):
    st.session_state.page = pageName
    st.rerun()

if st.session_state.page == 'index':
    index.render(setPage)
    st.stop()
elif st.session_state.page == 'tarot':
    tarot.render(setPage)
    st.stop()
elif st.session_state.page == 'result':
    result.render(setPage)
    st.stop()
else:
    index.render(setPage)
    st.stop()
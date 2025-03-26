import streamlit as st

from ui.common_style import common_style

st.set_page_config(
    page_title='Arcana Whisper',
    page_icon='🔮',
    layout='centered',
    initial_sidebar_state="collapsed"
)

# 스타일
common_style()

# 타이틀, 소개
st.markdown("<h1 class='centered'>🔮 Arcana Whisper</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='centered'>타로 카드와 LLM이 속삭이는 운명의 메시지</h3>", unsafe_allow_html=True)

# 설명
st.markdown(
    """
    <div class='centered'>
        <p><strong>Arcana Whisper</strong>는 인공지능을 통해 타로 카드 리딩을 경험할 수 있는 타로 서비스입니다.<br>
        신비로운 타로의 세계와 인공지능의 힘이 만나, 지금 이 순간 당신에게 필요한 메시지를 전해드립니다.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.warning(
    "Arcana Whisper는 오락 및 자기 성찰용으로 제공됩니다.\n\n"
    "- 실제 인생 결정은 전문가 상담 및 자신의 판단을 기반으로 하길 권장합니다.\n"
    "- 이 앱은 사용자의 심리 상태를 분석하거나 예언하지 않습니다."
)

if st.button("오늘의 타로 보기 ✨"):
    st.switch_page('pages/tarot.py')
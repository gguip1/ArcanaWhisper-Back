import streamlit as st

def common_style():
    # 스타일
    st.markdown(
        """
        <style>
            body {
                background-color: #1e1e2f;
                color: #f0e6f6;
            }
            .centered {
                text-align: center;
            }
            .stButton>button {
                background-color: #6a0dad;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-weight: bold;
            }
            .stButton {
                display: flex;
                justify-content: center;
            }
            .stAlert {
                display: flex;
                justify-content: center;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
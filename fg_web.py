import streamlit as st
from streamlit_option_menu import option_menu

from fg_pages import chat, setting

st.set_page_config(page_title='FG')

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

pages = {
    "问答": {
        "icon": "chat",
        "func": chat.chat_ui,
    },
    "知识库设置": {
        "icon": "building-gear",
        "func": setting.setting_ui,
    },
    "模型设置": {
        "icon": "database-gear",
        "func": setting.model_setting_ui,
    },
}

with st.sidebar:
    options = list(pages)
    icons = [x["icon"] for x in pages.values()]

    default_index = 0
    selected_page = option_menu(
        "",
        options=options,
        icons=icons,
        default_index=default_index,
    )

if selected_page in pages:
    pages[selected_page]["func"]()

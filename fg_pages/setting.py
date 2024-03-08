import os

import streamlit as st

from fg_apis.apis import doc_to_vdb

uploads_dir = 'uploads'
models_dir = 'models'


def not_exist_to_create(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def del_files(files):
    for file in files:
        os.remove(os.path.join(uploads_dir, file))


def mod_files(uploaded_files):
    paths = os.listdir(uploads_dir)
    for uploaded_file in uploaded_files:
        if uploaded_file.name in paths:
            continue
        else:
            uploaded_filepath = os.path.join(uploads_dir, uploaded_file.name)
            with open(uploaded_filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.toast(doc_to_vdb(uploaded_filepath))


def show_files(files, uploaded_files):
    st.divider()
    st.write('知识库中的文件', files)
    st.divider()
    st.write('当前添加的文件', uploaded_files)
    st.divider()


def setting_ui():
    with st.container():
        not_exist_to_create(uploads_dir)
        uploaded_files = st.file_uploader('Choose some files', accept_multiple_files=True)
        mod_files(uploaded_files)
        files = os.listdir(uploads_dir)
        show_files(files, uploaded_files)
        if len(files) == 0:
            return
        options = st.multiselect("选择需要删除的知识库文件", options=files, placeholder="请选择文件")
        st.write(options)
        if st.button("删除", use_container_width=True):
            del_files(options)
            st.experimental_rerun()


def model_setting_ui():
    with st.container():
        model_path = st.text_input("请输入模型位置", "models/m3e-base", disabled=True)
        st.divider()
        option = st.selectbox(
            '选择内容向量化使用的模型',
            ('m3e-small', 'm3e-base', 'm3e-large'), index=1)
        st.divider()
        st.write('知识库使用模型')
        st.text('m3e-base')
        st.divider()
        st.write('当前选择模型')
        st.text(option)

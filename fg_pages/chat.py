import time

import streamlit as st
from langchain import OpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
)

from fg_apis.apis import chat_with_vdb


@st.cache_resource
def load_llm():
    llm = OpenAI(temperature=0,
                 model_name="gpt-3.5-turbo",
                 openai_api_key='sk-**********************************',
                 openai_proxy='http://127.0.0.1:10809')
    return llm


def get_prompt(question, context):
    return f"""【指令】根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，不允许在答案中添加编造成分，答案请使用中文。 

            【已知信息】{context} 

            【问题】{question}"""


def get_answer(question, context):
    llm = load_llm()
    answer = llm(get_prompt(question, context))
    return answer


def chat_ui():
    with st.container():
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []
        for message in st.session_state['messages']:
            if isinstance(message, HumanMessage):
                with st.chat_message('user'):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message('assistant'):
                    st.markdown(message.content)
                    if 'source' in message.additional_kwargs:
                        with st.expander(f"知识库匹配结果{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"):
                            st.write(message.additional_kwargs['source'])
                            st.write(message.additional_kwargs['filepath'])
        prompt = st.chat_input("请提问...")
        if prompt:
            st.session_state['messages'].append(HumanMessage(content=prompt))
            with st.chat_message('user'):
                st.markdown(prompt)
            vdb_message = chat_with_vdb(prompt)
            if not vdb_message['source']:
                not_found = '未在知识库中找到匹配内容'
                st.session_state['messages'].append(AIMessage(content=not_found))
                with st.chat_message('assistant'):
                    st.write(not_found)
                return
            ai_answer = get_answer(prompt, vdb_message['content'])
            st.session_state['messages'].append(AIMessage(content=ai_answer, additional_kwargs={
                'source': vdb_message['content'],
                'filepath': vdb_message['source']
            }))
            with st.chat_message('assistant'):
                st.markdown(ai_answer)
                with st.expander("知识库匹配结果"):
                    st.write(vdb_message['content'])
                    st.write(vdb_message['source'])

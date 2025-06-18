import asyncio
import random
import time

import streamlit as st

from modules.answer.schemas import AnswerCreate
from modules.answer.service import create as create_answer
from modules.llm.llm_infos import Model
from pages.page_utils import show_regulations_widget, header, menu, page_config

page_config()


def initial_response_generator():
    response = random.choice(
        [
            "Hi! Is there any question about this regulation I can help you with?",
            "Do you have any question about this regulation?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def chatbot_page():
    st.divider()
    st.subheader("Chatbot 🤖")
    chat_not_empty = "messages" in st.session_state and st.session_state.messages
    clear_btn = st.button(
        "Clear chat",
        type="primary",
        disabled=not chat_not_empty
    )
    if clear_btn:
        initial_message = random.choice(
            [
                "Hi! Is there any question about this regulation I can help you with?",
                "Do you have any question about this regulation?",
            ]
        )
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        st.rerun()
    show_regulations_widget("Select a regulation to ask questions about:")
    st.divider()
    if "messages" not in st.session_state:
        st.session_state.messages = []
        with st.chat_message("assistant"):
            initial_response = initial_response_generator()
            initial_message = st.write_stream(initial_response)
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if question := st.chat_input("Ask your question about regulations here."):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            request = AnswerCreate(
                question=question,
                model=Model.AZURE_GPT4,
                prompt="You are a legal expert in ESG regulation, "
                       "first cite the relevant text from the contexts that can be used to answer the question. "
                       "Then answer the question based on the given contexts"
                       "Important: Make sure your answer is as complete as possible both in citing the relevant text and in answering the question. "
                # prompt="""You are a legal expert in ESG regulation,
                # Answer the question by copying exactly a portion of the context shown after the delimiter ####.
                # The portion you copy can directly answer the question or be evidence that supports the answer.
                # The portion you copy can be any substring of the context, the whole context, or even a single word. But favor short and concise answers.
                # *Mandatory*: your answer is always an exact excerpt of the the context shown after the delimiter ####, never respond with text not contained in the contexts.
                # Begin!
                # ####
                # """
            )
            answer_tuple = asyncio.run(create_answer(request, title=st.session_state["explored_regulation"]))
            response = st.write_stream(answer_tuple[2])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


header()
chatbot_page()
menu()


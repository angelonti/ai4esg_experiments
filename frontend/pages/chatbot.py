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
                prompt="""You are a legal expert in ESG regulation, please give thorough and professional answer to
                the question based on the given context. The answer must be an exact
                excerpt extracted from the given context that answers the question. Make
                sure to not add any additional or irrelevant information to the answer.
                Make sure the answer is as complete and correct as possible given the information in the context.
                Add quotes around every exact excerpt you use in the answer.
                If the answer consist of multiple excerpts from the context, add them as a bulleted list."""
            )
            answer_tuple = asyncio.run(create_answer(request, title=st.session_state["explored_regulation"]))
            response = st.write_stream(answer_tuple[2])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


header()
chatbot_page()
menu()


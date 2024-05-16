import streamlit as st
import sys

sys.path.append("../backend")

from modules.document.service import get_all_titles


def show_regulations_widget(message):
    message = message if message else "Select a regulation:"
    st.write(f"**{message}**")
    regulation_titles = get_regulation_titles()
    st.selectbox(
        label="Regulation",
        options=regulation_titles,
        key="explored_regulation"
    )


@st.cache_data
def get_regulation_titles():
    return get_all_titles()


def page_config():
    st.set_page_config(
        page_title="ESG IT-Tool", page_icon=":earth_americas:", layout="wide", initial_sidebar_state="auto",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )


def header():
    st.title("ESG IT-Tool ⚖️🌍")


def menu():
    st.sidebar.info("Select one of the options below.")
    st.sidebar.page_link("app.py", label="Home")
    st.sidebar.page_link("pages/run_evaluation.py", label="Run an evaluation")
    st.sidebar.page_link("pages/explore_regulations.py", label="Explore regulations")
    st.sidebar.page_link("pages/saved_evaluations.py", label="Saved evaluations")
    st.sidebar.page_link("pages/chatbot.py", label="Chatbot")
    st.sidebar.page_link("pages/annotation_page.py", label="Data annotation")

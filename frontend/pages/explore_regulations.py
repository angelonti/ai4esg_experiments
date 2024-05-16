import streamlit as st

from modules.document.service import get_by_title
from modules.penalty.service import get_summary_by_document_id as get_penalty_summary_by_document_id, \
    get_by_document_id as get_penalties_by_document_id
from modules.requirement.service import get_summary_by_document_id as get_requirement_summary_by_document_id, \
    get_by_document_id as get_requirements_by_document_id
from pages.page_utils import show_regulations_widget, header, menu, page_config

page_config()


@st.cache_data
def get_regulation_by_title(title):
    return get_by_title(title)


@st.cache_data
def get_regulation_requirements_summary(title):
    regulation = get_regulation_by_title(title)
    return get_requirement_summary_by_document_id(regulation.id).summary


@st.cache_data
def get_regulation_penalties_summary(title):
    regulation = get_regulation_by_title(title)
    return get_penalty_summary_by_document_id(regulation.id).summary


@st.cache_data
def get_all_requirements(title):
    regulation = get_regulation_by_title(title)
    requirements = get_requirements_by_document_id(regulation.id)
    return [requirement.text for requirement in requirements]


@st.cache_data
def get_all_penalties(title):
    regulation = get_regulation_by_title(title)
    penalties = get_penalties_by_document_id(regulation.id)
    return [penalty.text for penalty in penalties]


def regulations_page():
    st.divider()
    st.subheader("Explore regulations 📜")
    show_regulations_widget("Select a regulation to explore its requirements and penalties:")
    st.divider()
    col1, col2 = st.columns(2)
    col1.button("Show requirements summary", key="show_requirements_summary")
    col2.button("Show penalties summary", key="show_penalties_summary")
    if st.session_state["show_requirements_summary"]:
        requirements_summary = get_regulation_requirements_summary(st.session_state["explored_regulation"])
        st.write("**Requirements summary:**")
        st.write(requirements_summary)
        with st.expander("Requirements details", expanded=False):
            st.write(get_all_requirements(st.session_state["explored_regulation"]))

    if st.session_state["show_penalties_summary"]:
        penalties_summary = get_regulation_penalties_summary(st.session_state["explored_regulation"])
        st.write("**Penalties summary:**")
        st.write(penalties_summary)
        with st.expander("Penalties details", expanded=False):
            st.write(get_all_penalties(st.session_state["explored_regulation"]))


header()
regulations_page()
menu()


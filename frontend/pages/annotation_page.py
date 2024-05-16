import time
from itertools import count

import streamlit as st
import sys

sys.path.append("../backend")

from modules.evaluation_result.service import get_all as get_all_evaluation_results
from modules.annotations.service import get_annotator_by_password, set_annotation_task_finished, \
    update_annotation_task_data
from modules.annotations.schemas import Annotator, AnnotationTask
from pages.page_utils import menu, page_config

page_config()

st.title("ESG IT-Tool ⚖️🌍 | Data Annotation")


def load_data(annotator):
    tasks = annotator.tasks
    return tasks


@st.cache_data
def applicability_question_label_map(key_parameter: str, key_parameter_value: str) -> str:
    match key_parameter:
        case "Capital market oriented companies":
            return f"Given that the company **{key_parameter_value}** capital market oriented, and the above law text, does this law apply to the company?"
        case "Number of employees":
            return f"Given that the company has **{key_parameter_value}** employees, and the above law text, does this law apply to the company?"
        case "Assets":
            return f"Given that the company has **{key_parameter_value}€** in assets, and the above law text, does this law apply to the company?"
        case "Revenue":
            return f"Given that the company has **{key_parameter_value}€** in yearly revenue, and the above law text, does this law apply to the company?"
        case "Offering of financial products":
            return f"Given that the company **{key_parameter_value}** offering financial products, and the above law text, does this law apply to the company?"
        case "Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)":
            return f"Given that the company **{key_parameter_value}** in the scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH), and the above law text, does this law apply to the company?"
        case "Manufacturers or distributors of batteries":
            return f"Given that the company **{key_parameter_value}** a manufacturer or distributor of batteries, and the above law text, does this law apply to the company?"
        case "Jurisdiction":
            return f"Given that the company operates in the following jurisdictions: **{key_parameter_value}**, and the above law text, does this law apply to the company?"
        case "Markets (countries)":
            return f"Given that the company operates in the following markets: **{key_parameter_value}**, and the above law text, does this law apply to the company?"
        case "Sourcing (countries)":
            return f"Given that the company is sourcing from the following countries: **{key_parameter_value}**, and the above law text, does this law apply to the company?"
        case "Production (Countries)":
            return f"Given that the company is producing in the following countries: **{key_parameter_value}**, and the above law text, does this law apply to the company?"
        case "Products and Services offered":
            return f"Given that the company offers the following products and services: **{key_parameter_value}**, and the above law text, does this law apply to the company?"


def set_initial_page(my_data: dict):
    remaining_data = list(filter(lambda x: not x.finished, my_data))
    if len(remaining_data) == 0:
        st.session_state.completed = True
        return
    st.session_state.iterator = iter(remaining_data)
    st.session_state.item = next(st.session_state.iterator)
    st.session_state.first_submit = False


def set_task_data_for_update(task_data: dict):
    task_data["annotation"] = {}
    task_data["annotation"]["relevant_1"] = st.session_state.get(f"{task_data['key_parameter']}_relevant_1")
    task_data["annotation"]["relevant_2"] = st.session_state.get(f"{task_data['key_parameter']}_relevant_2")
    task_data["annotation"]["relevant_3"] = st.session_state.get(f"{task_data['key_parameter']}_relevant_3")
    task_data["annotation"]["applicable"] = st.session_state.get(f"{task_data['key_parameter']}_applicable")
    task_data["annotation"]["rating"] = st.session_state.get(f"{task_data['key_parameter']}_rating")
    return task_data


def move_next_page(task_data: dict):
    try:
        task_data = set_task_data_for_update(task_data)
        update_annotation_task_data(st.session_state.item.id, task_data)
        set_annotation_task_finished(st.session_state.item.id)
        st.session_state.item = next(st.session_state.iterator)
        js = '''
        <script>
            var body = window.parent.document.querySelector(".main");
            body.scrollTop = 0;
        </script>
        '''
        st.components.v1.html(js)
        time.sleep(0.1)
        st.session_state.num_completed += 1
        st.rerun()
    except StopIteration:
        st.session_state.completed = True
        print("reached end of data")
        st.rerun()


def all_fields_filled(key_parameter: str) -> bool:
    return all([st.session_state.get(f"{key_parameter}_relevant_1"),
                st.session_state.get(f"{key_parameter}_relevant_2"),
                st.session_state.get(f"{key_parameter}_relevant_3"),
                st.session_state.get(f"{key_parameter}_applicable")])


def data_annotation_page():
    st.write("""
    This is a data annotation app for the ESG IT-Tool.
    Please follow the instructions below to annotate the data. When you are done with the current page, please click the **submit button** to save the data, and move to the next page.
    """)

    st.write("## Instructions")
    st.expander("Show Instructions").markdown("""
    You will be presented with company parameters and text extracted from ESG law. For each company parameter, you will be asked to do the following tasks:
    1. Read the text extracted from ESG law, and decide if the text is relevant to determine the applicability of the law for the given company parameter.
    2. Given the law text, and the company parameter value, decide if this law applies to the company.
    3. In some cases, you will be presented a reasoning for whether the law applies to the company or not. Your task is to rate this reasoning on a scale of 1 to 5, where 1 is the lowest and 5 is the highest.
    """)

    st.write("## Data Annotation")
    progress = (st.session_state.num_completed / st.session_state.total) * 100
    st.progress(int(progress),
                text=f"You have completed {st.session_state.num_completed} annotations out of {st.session_state.total}.")

    task_data = st.session_state.item.data.copy()
    with st.container(border=True):
        st.markdown(f"Company Parameter: **{task_data['key_parameter']}**")
        st.markdown(f"Law title: **{task_data['title']}**")
        st.write(
            f"_Select whether the following texts are relevant or not to determine the applicability of the law with respect to the company parameter **\"{task_data['key_parameter']}\"**:_")
        st.write(f"{task_data['relevant_embeddings'][0]['text']}")
        st.radio("Is this text relevant?", ("Yes", "No"), key=f"{task_data['key_parameter']}_relevant_1", index=None)
        st.divider()
        st.write(f"{task_data['relevant_embeddings'][1]['text']}")
        st.radio("Is this text relevant?", ("Yes", "No"), key=f"{task_data['key_parameter']}_relevant_2", index=None)
        st.divider()
        st.write(f"{task_data['relevant_embeddings'][2]['text']}")
        st.radio("Is this text relevant?", ("Yes", "No"), key=f"{task_data['key_parameter']}_relevant_3", index=None)
        st.divider()
        st.write(applicability_question_label_map(task_data["key_parameter"], task_data["key_parameter_value"]))
        applicable = st.radio("does this law apply to the company?", ("Yes", "No", "Unclear"),
                              key=f"{task_data['key_parameter']}_applicable", index=None)
        st.divider()
        if not st.session_state.get("first_submit") and all_fields_filled(task_data["key_parameter"]):
            submit_button = st.button("Submit", key=f"{task_data['key_parameter']}_submit")
        else:
            submit_button = st.button("Submit", key=f"{task_data['key_parameter']}_submit", disabled=True)

        response_match = applicable and applicable.lower() == task_data["response"]["answer"].lower()
        if st.session_state.get(f"{task_data['key_parameter']}_rating_submit"):
            st.session_state.first_submit = False
            move_next_page(task_data)
        elif (submit_button and response_match) or st.session_state.first_submit:
            st.session_state.first_submit = True
            st.write("*Give a rating from 1 to 5 to the reasoning that explains the answer to the previous question.*")
            st.write("**Reasoning**: ", task_data["response"]["reasoning"])
            st.slider(f"Rating", 1, 5, key=f"{task_data['key_parameter']}_rating", value=None)
            st.button("Submit Rating", key=f"{task_data['key_parameter']}_rating_submit")
        elif submit_button and not response_match:
            st.session_state.first_submit = False
            move_next_page(task_data)


def completed_page():
    st.balloons()
    st.markdown("## Data annotation completed. Thank you for your time! 🎉")


def find_annotator_data(password: str):
    annotator = get_annotator_by_password(password)
    return annotator


if st.session_state.get("authenticated"):
    # initialize data
    if st.session_state.get("iterator") is None:
        # data = [parameter_data for item in load_data(st.session_state.annotator) for parameter_data in item]
        # data = [data[0]]  # for testing purposes
        data = load_data(st.session_state.annotator)
        st.session_state.num_completed = len(list(filter(lambda x: x.finished, data)))
        st.session_state.total = len(data)
        set_initial_page(data)

    if st.session_state.get("completed"):
        completed_page()
    else:
        data_annotation_page()
else:
    st.write(
        "Only authorized annotators may access this module. To access please input the password you received via e-mail.")
    password = st.text_input("Password", type="password")
    password_submit = st.button("Submit")
    if password_submit and (annotator := find_annotator_data(password)) is not None:
        st.session_state.authenticated = True
        st.session_state.annotator = annotator
        st.rerun()
    elif password_submit:
        st.error("Wrong password. Please try again.")
menu()

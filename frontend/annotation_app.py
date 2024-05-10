import json
import time
import sys
import streamlit as st

sys.path.append("../backend")

from modules.evaluation_result.service import get_all as get_all_evaluation_results

st.set_page_config(
    page_title="ESG IT-Tool|annotation", page_icon=":white_check_mark:", layout="wide", initial_sidebar_state="auto",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.title("ESG IT-Tool ⚖️🌍 | Data Annotation App")

st.write("""
This is a data annotation app for the ESG IT-Tool.
Please follow the instructions below to annotate the data. When you are done with the current page, please click the **submit button** to save the data, and move to the next page.
""")


@st.cache_data
def load_data():
    evaluation_results = get_all_evaluation_results()
    print(evaluation_results)
    json_data = [item.evaluation["data"] for item in evaluation_results]
    # json_data = json.load(open("./testEval1_results.json", "r", encoding="utf-8"))
    return json_data


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
    st.session_state.iterator = iter(my_data)
    st.session_state.item = next(st.session_state.iterator)
    st.session_state.first_submit = False


def move_next_page():
    try:
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


st.write("## Instructions")
st.expander("Show Instructions").markdown("""
You will be presented with company parameters and text extracted from ESG law. For each company parameter, you will be asked to do the following tasks:
1. Read the text extracted from ESG law, and decide if the text is relevant to determine the applicability of the law for the given company parameter.
2. Given the law text, and the company parameter value, decide if this law applies to the company.
3. In some cases, you will be presented a reasoning for whether the law applies to the company or not. Your task is to rate this reasoning on a scale of 1 to 5, where 1 is the lowest and 5 is the highest.
""")


def data_annotation_page():
    st.write("## Data Annotation")
    progress = (st.session_state.num_completed / st.session_state.total) * 100
    st.progress(int(progress), text=f"You have completed {st.session_state.num_completed} annotations out of {st.session_state.total}.")

    item = st.session_state.item
    with st.container(border=True):
        st.markdown(f"Company Parameter: **{item['key_parameter']}**")
        st.markdown(f"Law title: **{item['title']}**")
        st.write(f"_Select whether the following texts are relevant or not to determine the applicability of the law with respect to the company parameter **\"{item['key_parameter']}\"**:_")
        st.write(f"{item['relevant_embeddings'][0]['text']}")
        st.radio("Is this text relevant?", ("Yes", "No"), key=f"{item['key_parameter']}_relevant_1", index=None)
        st.divider()
        st.write(f"{item['relevant_embeddings'][1]['text']}")
        st.radio("Is this text relevant?", ("Yes", "No"), key=f"{item['key_parameter']}_relevant_2", index=None)
        st.divider()
        st.write(f"{item['relevant_embeddings'][2]['text']}")
        st.radio("Is this text relevant?", ("Yes", "No"), key=f"{item['key_parameter']}_relevant_3", index=None)
        st.divider()
        st.write(applicability_question_label_map(item["key_parameter"], item["key_parameter_value"]))
        applicable = st.radio("does this law apply to the company?", ("Yes", "No", "Unclear"), key=f"{item['key_parameter']}_applicable", index=None)
        st.divider()
        if not st.session_state.get("first_submit") and all_fields_filled(item["key_parameter"]):
            submit_button = st.button("Submit", key=f"{item['key_parameter']}_submit")
        else:
            submit_button = st.button("Submit", key=f"{item['key_parameter']}_submit", disabled=True)

        response_match = applicable and applicable.lower() == item["response"]["answer"].lower()
        if st.session_state.get(f"{item['key_parameter']}_rating_submit"):
            st.session_state.first_submit = False
            move_next_page()
        elif (submit_button and response_match) or st.session_state.first_submit:
            st.session_state.first_submit = True
            st.write("*Give a rating from 1 to 5 to the reasoning that explains the answer to the previous question.*")
            st.write("**Reasoning**: ", item["response"]["reasoning"])
            st.slider(f"Rating", 1, 5, key=f"{item['key_parameter']}_rating", value=None)
            st.button("Submit Rating", key=f"{item['key_parameter']}_rating_submit")
        elif submit_button and not response_match:
            st.session_state.first_submit = False
            move_next_page()


def completed_page():
    st.markdown("## Data annotation completed. Thank you for your time! 🎉")
    st.balloons()


# initialize data
if st.session_state.get("iterator") is None:
    #data = load_data()[0]
    data = [parameter_data for item in load_data() for parameter_data in item]
    set_initial_page(data)
    st.session_state.num_completed = 0
    st.session_state.total = len(data)

if st.session_state.get("completed"):
    completed_page()
else:
    data_annotation_page()

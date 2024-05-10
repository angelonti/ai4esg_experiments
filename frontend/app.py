import sys
from typing import Union

sys.path.append("../backend")

import streamlit as st
from modules.llm.llm_infos import Model
from modules.document.service import get_all_titles
from modules.document.service import get_by_title, get as get_document_by_id
from modules.requirement.service import get_summary_by_document_id as get_requirement_summary_by_document_id
from modules.penalty.service import get_summary_by_document_id as get_penalty_summary_by_document_id
from modules.requirement.service import get_by_document_id as get_requirements_by_document_id
from modules.penalty.service import get_by_document_id as get_penalties_by_document_id
from modules.answer.schemas import AnswerCreate
from modules.answer.service import create as create_answer
from modules.evaluation_result.service import get_all as get_all_evaluations, get as get_evaluation_by_id
from modules.esg.applicability.service import determine_applicability_single
from data import all_countries, all_regions
import random
import time
import asyncio
import pandas as pd

st.set_page_config(
    page_title="ESG IT-Tool", page_icon=":earth_americas:", layout="wide", initial_sidebar_state="auto",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.title("ESG IT-Tool ⚖️🌍")

st.sidebar.selectbox(
    label="Select an option:",
    options=["Main page", "Run an evaluation", "Explore regulations", "Saved evaluations", "Chatbot"],
    key="context"
)

st.sidebar.success("Select one of the options above.")


def home_page():
    st.markdown(
        """
        This tool is designed to help you determine what regulations apply to your company based on your company's parameters.\n
        It also helps you understand the requirements for compliance and penalties for non-compliance for each regulation.
        
        Here you can:
        * Run an evaluation of applicability regulations to your company based on your company's parameters.
        * Explore regulations, with their requirements for compliance and penalties for non-compliance.
        * View saved evaluation results.
        * Use our chatbot to ask questions about the regulations.
        
        **👈 Select an item on the left** to see what this tool can do!"""
    )


def run_evaluation_page():
    st.divider()
    st.subheader("Run an evaluation ✔️")
    show_regulations_widget("Select a regulation to evaluate:")
    st.divider()
    show_evaluation_form()


def show_evaluation_form():
    all_regions_and_countries = all_regions + all_countries
    with st.form(key="evaluation_form", border=True, clear_on_submit=False):
        st.write("**Give this evaluation a name**:")
        st.text_input("Evaluation name", key="evaluation_name", placeholder="Enter a name for this evaluation",
                      help="Evaluation name must be an alphanumeric string with no spaces. Underscores '_' are allowed.")
        st.write("**Enter your company's parameters**:")
        st.text_input("Company name", key="company_name")
        st.radio("Is the company capital market oriented?", ["is", "is not"], format_func=map_yes_no_radios,
                 key="is_capital_market_oriented")
        st.number_input("Number of employees", min_value=0, step=1, key="num_employees")
        st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "CNY"], key="currency", index=1)
        st.number_input("Total assets", min_value=0.00, step=0.01,
                        format="%.2f", key="assets")
        st.number_input("Yearly revenue", min_value=0.00, step=0.01,
                        format="%.2f", key="revenue")
        st.radio("Is the company offering financial products?", ["is", "is not"], format_func=map_yes_no_radios,
                 key="is_offering_financial_products")
        st.radio(
            "Is the company subject the Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)?",
            ["Yes", "No"], key="is_REACH")
        st.radio("Is the company a manufacturer or distributor of batteries?", ["is", "is not"],
                 format_func=map_yes_no_radios, key="is_battery")
        with st.container(border=True):
            st.write("**Jurisdiction**:")
            st.multiselect("Include", options=all_regions_and_countries, key="jurisdiction_include")
            st.multiselect("Exclude", options=all_regions_and_countries, key="jurisdiction_exclude")
        with st.container(border=True):
            st.write("**Markets**:")
            st.multiselect("Include", options=all_regions_and_countries, key="markets_include")
            st.multiselect("Exclude", options=all_regions_and_countries, key="markets_exclude")
        with st.container(border=True):
            st.write("**Sourcing countries/regions**:")
            st.multiselect("Include", options=all_regions_and_countries, key="sourcing_include")
            st.multiselect("Exclude", options=all_regions_and_countries, key="sourcing_exclude")
        with st.container(border=True):
            st.write("**Production countries/regions**:")
            st.multiselect("Include", options=all_regions_and_countries, key="production_include")
            st.multiselect("Exclude", options=all_regions_and_countries, key="production_exclude")
        st.text_input(label="Products and services offered", key="products_and_services_offered",
                      help="Enter the products and services offered by the company separated by commas",
                      placeholder="comma separated list of products and services")
        st.write("**Begin the evaluation**:")
        st.form_submit_button("Run evaluation", on_click=run_evaluation)


def map_yes_no_radios(value):
    if value == "is":
        return "Yes"
    else:
        return "No"


def validate_evaluation_name(name: str):
    if not (name.replace("_", "").isalnum() or len(name) == 0) or (" " in name):
        return False
    return True


def validate_input_data(input_data: dict):
    st.session_state["evaluation_form_error"] = False
    for key, value in input_data.items():
        if key == "evaluation_name" and not (validate_evaluation_name(value)):
            st.session_state[
                "error_message"] = "Evaluation name must be an alphanumeric string with no spaces. Underscores '_' are allowed."
            st.session_state["evaluation_form_error"] = True
        if not value:
            st.session_state["error_message"] = f"Please provide a value for {key}"
            st.session_state["evaluation_form_error"] = True


def process_form_data() -> tuple[dict, str]:
    jurisdiction = get_include_exclude_list(st.session_state["jurisdiction_include"],
                                            st.session_state["jurisdiction_exclude"])
    markets = get_include_exclude_list(st.session_state["markets_include"], st.session_state["markets_exclude"])
    sourcing = get_include_exclude_list(st.session_state["sourcing_include"], st.session_state["sourcing_exclude"])
    production = get_include_exclude_list(st.session_state["production_include"],
                                          st.session_state["production_exclude"])

    evaluation_input = {
        "evaluation_name": st.session_state["evaluation_name"],
        "company_name": st.session_state["company_name"],
        "is_capital_market_oriented": st.session_state["is_capital_market_oriented"],
        "num_employees": st.session_state["num_employees"],
        "currency": st.session_state["currency"],
        "assets": st.session_state['assets'],
        "revenue": st.session_state['revenue'],
        "is_offering_financial_products": st.session_state["is_offering_financial_products"],
        "is_REACH": st.session_state["is_REACH"],
        "is_battery": st.session_state["is_battery"],
        "jurisdiction": jurisdiction,
        "markets": markets,
        "sourcing": sourcing,
        "production": production,
        "products_and_services_offered": st.session_state["products_and_services_offered"]
    }

    validate_input_data(evaluation_input)

    title = st.session_state["explored_regulation"]

    return evaluation_input, title


def run_evaluation():
    evaluation_input, title = process_form_data()
    if st.session_state["evaluation_form_error"]:
        st.sidebar.error(st.session_state["error_message"], icon="🚨")
        st.session_state["evaluation_form_error"] = False
        st.session_state["error_message"] = None
        return

    st.write("Evaluation started...")
    st.write(f"evaluating for title: {title}")
    st.write(evaluation_input)
    result = asyncio.run(determine_applicability_single(input_params=evaluation_input, title=title,
                                                        evaluation_name=evaluation_input["evaluation_name"]))
    st.write(result)


def get_include_exclude_list(include: list, exclude: list) -> list:
    return list(set(include) - set(exclude))


@st.cache_data
def get_regulation_by_title(title):
    return get_by_title(title)


@st.cache_data
def get_regulation_titles():
    return get_all_titles()


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


def show_regulations_widget(message):
    #st.checkbox("Show only applicable regulations", key="show_applicable_regulations", value=True)
    message = message if message else "Select a regulation:"
    st.write(f"**{message}**")
    #if st.session_state["show_applicable_regulations"]:
    #    regulation_titles = [
    #        "DIRECTIVES DIRECTIVE (EU) 2022/2464 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL",
    #        "Union REGULATION (EU) 2020/852 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 18 June 2020",
    #        "REGULATION (EU) 2023/1542 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 12 July 2023 concerning batteries and waste batteries, amending Directive 2008/98/EC and Regulation (EU) 2019/1020 and repealing Directive 2006/66/EC (Text with EEA relevance)",
    #        "Act on Corporate Due Diligence Obligations for the Prevention of Human Rights Violations in Supply Chains (Lieferkettensorgfaltspflichtengesetz – LkSG)",
    #        "REGULATION (EU) 2019/2088 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 27 November 2019 on sustainability‐related disclosures in the financial services sector (Text with EEA relevance)",
    #        "DIRECTIVE 2008/98/EC OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 19 November 2008 on waste and repealing certain Directives (Text with EEA relevance)"
    #    ]
    #else:
    #    regulation_titles = get_regulation_titles()
    regulation_titles = get_regulation_titles()
    st.selectbox(
        label="Regulation",
        options=regulation_titles,
        key="explored_regulation"
    )


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


def show_evaluations_table(df):
    data_with_details = df.copy()
    data_with_details['show_details'] = [False for _ in range(len(df))]
    column_config = {
        "id": None,
        "show_details": "Show details",
        "evaluation_name": "Evaluation name",
        "title": st.column_config.TextColumn(
            label="Regulation title",
            disabled=True
        )
    }
    st.session_state.data_editor = st.data_editor(
        data_with_details,
        use_container_width=True,
        disabled=("evaluation_name", "title"),
        column_config=column_config, hide_index=True,
        column_order=("show_details", "evaluation_name", "title")
    )


@st.cache_data
def get_evaluation_by_id_cached(id):
    return get_evaluation_by_id(id)


def map_yes_no_parameter_value(parameter_value: str):
    match parameter_value:
        case "is":
            return "Yes"
        case "is not":
            return "No"
        case _:
            return parameter_value


def map_parameter_value(parameter_value: Union[str, list]):
    if isinstance(parameter_value, list):
        return ", ".join(parameter_value)
    else:
        return map_yes_no_parameter_value(parameter_value)


def show_detail(id):
    evaluation = get_evaluation_by_id_cached(id)
    evaluation.document = ""
    evaluation_data = evaluation.evaluation["data"]
    with st.container(border=True):
        st.write(f"Evaluation details for **{evaluation.evaluation_name}**")
        st.write(f"**Regulation title:** {evaluation_data[0]['title']}")
        for item in evaluation_data:
            with st.container(border=True):
                st.write(f"**Parameter:** {item['key_parameter']}")
                st.write(f"**Value:** {map_parameter_value(item['key_parameter_value'])}")
                st.write(f"**Applicable:** {str(item['response']['answer']).capitalize()}")
                st.write(f"**Reasoning:** {item['response']['reasoning']}")
                with st.expander("**Relevant excerpts**", expanded=False):
                    for i, context in enumerate(item["relevant_embeddings"]):
                        st.write(f"**Excerpt ({i + 1}):**")
                        st.write(context["text"])
                        st.divider()


def results_page():
    st.divider()
    st.subheader("View saved results 🗄️")
    evaluations_data = get_all_evaluations()
    for evaluation in evaluations_data:
        evaluation.document_id = str(evaluation.document_id)
        evaluation.id = str(evaluation.id)
        evaluation.evaluation = str(evaluation.evaluation)
        evaluation.document = ""
    evaluations_df = pd.DataFrame([{
        "id": evaluation.id,
        "evaluation_name": evaluation.evaluation_name,
        "title": get_document_by_id(evaluation.document_id).title,
    } for evaluation in evaluations_data])

    show_evaluations_table(evaluations_df)

    st.session_state["selected_evaluation"] = st.session_state.data_editor.loc[
        st.session_state.data_editor['show_details']]
    st.session_state["clicked_indexes"] = st.session_state["selected_evaluation"].index if not st.session_state[
        "selected_evaluation"].empty else []

    if len(st.session_state["clicked_indexes"]) > 0:
        for index in st.session_state["clicked_indexes"]:
            show_detail(st.session_state.data_editor.iloc[index].id)
    st.session_state.data_editor["show_details"] = False


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
                #prompt="""You are a legal expert in ESG regulation,
                #Answer the question by copying exactly a portion of the context shown after the delimiter ####.
                #The portion you copy can directly answer the question or be evidence that supports the answer.
                #The portion you copy can be any substring of the context, the whole context, or even a single word. But favor short and concise answers.
                #*Mandatory*: your answer is always an exact excerpt of the the context shown after the delimiter ####, never respond with text not contained in the contexts.
                #Begin!
                #####
                #"""
            )
            answer_tuple = asyncio.run(create_answer(request, title=st.session_state["explored_regulation"]))
            response = st.write_stream(answer_tuple[2])
        st.session_state.messages.append({"role": "assistant", "content": response})


if st.session_state["context"] in ["Main page", None]:
    home_page()
if st.session_state["context"] == "Run an evaluation":
    run_evaluation_page()
elif st.session_state["context"] == "Explore regulations":
    regulations_page()
elif st.session_state["context"] == "Saved evaluations":
    results_page()
elif st.session_state["context"] == "Chatbot":
    chatbot_page()

import sys

sys.path.append("../backend")

import streamlit as st
from modules.llm.llm_infos import Model
from modules.document.service import get_all_titles
from modules.document.service import get_by_title
from modules.requirement.service import get_summary_by_document_id as get_requirement_summary_by_document_id
from modules.penalty.service import get_summary_by_document_id as get_penalty_summary_by_document_id
from modules.requirement.service import get_by_document_id as get_requirements_by_document_id
from modules.penalty.service import get_by_document_id as get_penalties_by_document_id
from modules.answer.schemas import AnswerCreate
from modules.answer.service import create as create_answer
from modules.esg.applicability.service import determine_applicability_single
from data import all_countries, all_regions
import random
import time
import asyncio

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
        st.text_input("Evaluation name", key="evaluation_name", placeholder="Enter a name for this evaluation")
        st.write("**Enter your company's parameters**:")
        st.text_input("Company name", key="company_name")
        st.radio("Is the company capital market oriented?", ["is", "is not"], format_func=map_yes_no_radios,
                 key="is_capital_market_oriented")
        st.number_input("Number of employees", min_value=0, step=1, key="num_employees")
        st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "CNY"], key="currency", index=1)
        st.number_input("Total Assets", min_value=0.00, step=0.01, key="assets")
        st.number_input("Yearly Revenue", min_value=0.00, step=0.01, key="revenue")
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


def validate_input_data(input_data: dict):
    st.session_state["evaluation_form_error"] = False
    for key, value in input_data.items():
        if key == "evaluation_name" and not (value.isalnum() and len(value) > 0):
            st.session_state[
                "error_message"] = "Evaluation name must be an alphanumeric string. No special characters allowed."
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
        "assets": st.session_state["assets"],
        "revenue": st.session_state["revenue"],
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
    st.checkbox("Show only applicable regulations", key="show_applicable_regulations", value=True)
    message = message if message else "Select a regulation:"
    st.write(f"**{message}**")
    if st.session_state["show_applicable_regulations"]:
        regulation_titles = [
            "DIRECTIVES DIRECTIVE (EU) 2022/2464 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL",
            "Union REGULATION (EU) 2020/852 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 18 June 2020",
            "REGULATION (EU) 2023/1542 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 12 July 2023 concerning batteries and waste batteries, amending Directive 2008/98/EC and Regulation (EU) 2019/1020 and repealing Directive 2006/66/EC (Text with EEA relevance)",
            "Act on Corporate Due Diligence Obligations for the Prevention of Human Rights Violations in Supply Chains (Lieferkettensorgfaltspflichtengesetz – LkSG)",
            "REGULATION (EU) 2019/2088 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 27 November 2019 on sustainability‐related disclosures in the financial services sector (Text with EEA relevance)",
            "DIRECTIVE 2008/98/EC OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 19 November 2008 on waste and repealing certain Directives (Text with EEA relevance)"
        ]
    else:
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


def results_page():
    st.divider()
    st.subheader("View saved results 🗄️")


def test_response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
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
                       "Then answer the question based of the given contexts"
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

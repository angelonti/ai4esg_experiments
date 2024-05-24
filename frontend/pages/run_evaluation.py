import asyncio

import streamlit as st
import streamlit.components.v1 as st_components

from pages.page_utils import show_regulations_widget, header, menu, page_config
from pages.location_data import all_regions, all_countries
from modules.esg.applicability.service import determine_applicability_single

page_config()


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
            ["is", "is not"],
            format_func=map_yes_no_radios, key="is_REACH")
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
                      placeholder="Comma separated list of products and services")
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


def scroll_to_top():
    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        body.scrollTop = 0;
    </script>
    '''
    st_components.html(js)


def run_evaluation():
    evaluation_input, title = process_form_data()
    if st.session_state["evaluation_form_error"]:
        st.sidebar.error(st.session_state["error_message"], icon="🚨")
        st.session_state["evaluation_form_error"] = False
        st.session_state["error_message"] = None
        return

    scroll_to_top()

    asyncio.run(run_evaluation_internal(evaluation_input, title))


async def run_evaluation_internal(evaluation_input, title):
    st.write(f"Evaluating for regulation: **{title}**")
    recorder = []
    evaluation_task = asyncio.create_task(
        determine_applicability_single(
            input_params=evaluation_input,
            title=title,
            evaluation_name=evaluation_input["evaluation_name"],
            recorder=recorder
        )
    )
    # st.write(evaluation_input)
    with st.status("Running evaluation...", expanded=True) as status:
        st.write("Evaluation started...")
        while not evaluation_task.done():
            await asyncio.sleep(2)
            if len(recorder) > 0:
                for _ in range(len(recorder)):
                    message = recorder.pop(0)
                    st.write(message)
                    st.toast(message)
        for _ in range(len(recorder)):
            message = recorder.pop(0)
            st.write(message)
            st.toast(message)
        status.update(label="Evaluation complete!", state="complete", expanded=False)

    app_path = 'http://localhost:8501'
    page_file_path = 'pages/saved_evaluations.py'
    page = page_file_path.split('/')[1][0:-3]
    st.success("Evaluation completed! You can view the result under:")
    st.markdown(f'<a href="{app_path}/{page}" target="_self">Saved evaluations</a>.', unsafe_allow_html=True)


def get_include_exclude_list(include: list, exclude: list) -> list:
    return list(set(include) - set(exclude))


header()
run_evaluation_page()
menu()


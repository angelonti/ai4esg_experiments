from typing import Union

import pandas as pd
import streamlit as st

from modules.document.service import get as get_document_by_id
from modules.evaluation_result.service import get as get_evaluation_by_id, get_all as get_all_evaluations
from pages.page_utils import header, menu, page_config

page_config()


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


header()
results_page()
menu()


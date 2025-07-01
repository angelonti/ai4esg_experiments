import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent)+'/backend')

import streamlit as st
from pages.page_utils import header
from pages.page_utils import menu, page_config

page_config()


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


header()
home_page()
menu()

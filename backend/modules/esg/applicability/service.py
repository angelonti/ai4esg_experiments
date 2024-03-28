import json
import logging
import os.path
import sys

from modules.embedding.utils import to_relevant_embeddings
from modules.prompts.applicability_evaluation_prompts import (
    KEY_PARAMETERS,
    APPLICABILITY_PROMPT_MAP,
)
from dotenv import load_dotenv, find_dotenv
from modules.document.ingest.esg_document_ingest import EsgRegulationIngestor
import warnings
from config import config
import openai
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import SimpleJsonOutputParser
from modules.document.pydantic.models import KeyParameterEvaluation
from modules.llm.utils import get_text_embedding
from modules.llm.clients.base import LLMClient

logging.basicConfig(level=logging.DEBUG, filename="ai4esg.log", format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)

warnings.filterwarnings("ignore")

_ = load_dotenv(find_dotenv(filename="local.env"))

openai.api_key = config.azure_openai_key
openai.api_base = config.api_endpoint
openai.api_version = "2023-05-15"

warnings.filterwarnings("ignore")

# esg_regulation_ingestor = EsgRegulationIngestor(documents=[], batch_size=2, init_docs=False)

chatOpenAI = AzureChatOpenAI(
    temperature=config.temperature,
    deployment_name=config.azure_gpt4_deployment_name,
    openai_api_base=openai.api_base,
    openai_api_version=openai.api_version,
    openai_api_key=openai.api_key,
)

EXTRACTED_FILE = "C:/Users/onan/IdeaProjects/ai4esg_experiments_new/experiments/key_parameters/DIRECTIVES_DIRECTIVE_(EU)_2022_2464_OF_THE_EUROPEAN_PARLIAMENT_AND_OF_THE_COUNCIL_key_parameters.json"
RESULTS_FILE = "./company_x_applicability_evaluation_results.json"


def load_saved_results(RESULTS_FILE):
    with open(RESULTS_FILE, "r") as f:
        json_data = json.load(f)
    return json_data


# add regulation title
'''
def determine_applicability_single_from_extracted(input_params: dict) -> dict:
    """
    Determine if a regulation applies to a company based on the company's key parameters.

    Args:
    extracted_file (str): The extracted text from the legal document.
    regulation_title (str): The title of the regulation.
    input (dict): The input data.

    Returns:
    dict: The output data.
    """
    results = {"data": []}

    remaining_key_parameters = KEY_PARAMETERS

    if os.path.isfile(RESULTS_FILE):  # check if there are saved results and load them
        saved_results = load_saved_results(RESULTS_FILE)
    else:
        saved_results = {}
    if "data" in saved_results:
        results = saved_results
        processed_key_parameters = [d["key_parameter"] for d in results["data"]]
        remaining_key_parameters = list(set(remaining_key_parameters) - set(processed_key_parameters))

    # load datafile with relevant key parameter texts
    extracted_data = esg_regulation_ingestor.load_saved_data(EXTRACTED_FILE)  # add regulation title
    if not extracted_data:
        raise ValueError("No extracted data found for the regulation title")
    key_parameter_data = extracted_data["data"]  # load data
    metadata = extracted_data["metadata"]  # load metadata

    for key_parameter in remaining_key_parameters:
        current_data = [d for d in key_parameter_data if
                        d["key_parameter"] == key_parameter]  # data for current key parameter
        eval_prompt = APPLICABILITY_PROMPT_MAP[key_parameter]
        prompt = PromptTemplate.from_template(eval_prompt)
        doc = "".join(
            [excerpt["text"] + "\n\n" for element in current_data for excerpt in
             element["excerpts"]])  # merge all excerpts for context
        output_parser = SimpleJsonOutputParser(pydantic_object=KeyParameterEvaluation)
        chain = LLMChain(llm=chatOpenAI, verbose=True, prompt=prompt, output_parser=output_parser,
                         output_key="response")
        invoke_params = get_invoke_params(input_params, key_parameter, doc, output_parser)
        response = chain.invoke(invoke_params)
        results["data"].append({
            "key_parameter": key_parameter,
            "response": response["response"],
            "title": metadata["title"],
        })
        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=4)
            print(f"saved results to results/{RESULTS_FILE} for key parameter {key_parameter}")
'''


def load_saved_evaluations(RESULTS_FILE):
    if os.path.isfile(RESULTS_FILE):  # check if there are saved results and load them
        saved_results = load_saved_results(RESULTS_FILE)
        return saved_results
    return {}


def get_remaining_key_parameters(remaining_key_parameters, saved_results, title):
    if "data" in saved_results:
        processed_key_parameters = [d["key_parameter"] for d in saved_results["data"] if d["title"] == title]
        remaining_key_parameters = list(set(remaining_key_parameters) - set(processed_key_parameters))
    return remaining_key_parameters


async def determine_applicability_single(input_params: dict, title: str) -> dict:
    """
    Determine if a regulation applies to a company based on the company's key parameters.

    Args:
    extracted_file (str): The extracted text from the legal document.
    regulation_title (str): The title of the regulation.
    input (dict): The input data.

    Returns:
    dict: The output data.
    """
    logger.info(f"Starting applicability evaluation for {title}")
    results = {"data": []}

    remaining_key_parameters = KEY_PARAMETERS

    saved_results = load_saved_evaluations(RESULTS_FILE)
    if "data" in saved_results:
        results = saved_results
        remaining_key_parameters = get_remaining_key_parameters(remaining_key_parameters, results, title)

    logger.info(f"Remaining key parameters: {remaining_key_parameters}")
    for key_parameter in remaining_key_parameters:
        eval_prompt = APPLICABILITY_PROMPT_MAP[key_parameter]
        embedding_response = await get_text_embedding(eval_prompt)
        question_embedding = embedding_response.data[0].embedding
        embeddings = LLMClient.get_relevant_embeddings(question_embedding, config.max_content, title=title)
        relevant_embeddings = to_relevant_embeddings(question_embedding, embeddings)
        prompt = PromptTemplate.from_template(eval_prompt)
        doc = "".join([embedding.text + "\n\n" for embedding in embeddings])
        doc_title = embeddings[0].document.title
        output_parser = SimpleJsonOutputParser(pydantic_object=KeyParameterEvaluation)
        chain = LLMChain(llm=chatOpenAI, verbose=True, prompt=prompt, output_parser=output_parser, output_key="response")
        invoke_params = get_invoke_params(input_params, key_parameter, doc, output_parser)
        response = chain.invoke(invoke_params)
        results["data"].append({
            "key_parameter": key_parameter,
            "response": response["response"],
            "relevant_embeddings": relevant_embeddings,
            "title": doc_title,
        })
        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=4)
            print(f"saved results to results/{RESULTS_FILE} for key parameter {key_parameter}")


def get_invoke_params(input_params, key_parameter, doc, output_parser):
    invoke_params_map = {
        "Capital market oriented companies": get_invoke_params_capital_market_oriented(input_params, doc, output_parser),
        "Number of employees": get_invoke_params_number_of_employees(input_params, doc, output_parser),
        "Assets": get_invoke_params_assets(input_params, doc, output_parser),
        "Revenue": get_invoke_params_revenue(input_params, doc, output_parser),
        "Offering of financial products": get_invoke_params_offering_of_financial_products(input_params, doc, output_parser),
        "Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)":
            get_invoke_params_REACH(input_params, doc, output_parser),
        "Manufacturers or distributors of batteries": get_invoke_params_battery(input_params, doc, output_parser),
        #    "Date of applicability": "",
        "Jurisdiction": get_invoke_params_jurisdiction(input_params, doc, output_parser),
        "Markets (countries)": get_invoke_params_markets(input_params, doc, output_parser),
        "Sourcing (countries)": get_invoke_params_sourcing(input_params, doc, output_parser),
        "Production (Countries)": get_invoke_params_production(input_params, doc, output_parser),
        "Products and Services offered": get_invoke_params_products_and_services_offered(input_params, doc, output_parser)
    }

    return invoke_params_map[key_parameter]


def get_invoke_params_capital_market_oriented(input_params, doc, output_parser):
    return {
        "is_capital_market_oriented": input_params["is_capital_market_oriented"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_number_of_employees(input_params, doc, output_parser):
    return {
        "num_employees": input_params["num_employees"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_assets(input_params, doc, output_parser):
    return {
        "assets": input_params["assets"],
        "currency": input_params["currency"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_revenue(input_params, doc, output_parser):
    return {
        "revenue": input_params["revenue"],
        "currency": input_params["currency"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_offering_of_financial_products(input_params, doc, output_parser):
    return {
        "is_offering_financial_products": input_params["is_offering_financial_products"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_REACH(input_params, doc, output_parser):
    return {
        "is_REACH": input_params["is_REACH"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_battery(input_params, doc, output_parser):
    return {
        "is_battery": input_params["is_battery"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_jurisdiction(input_params, doc, output_parser):
    return {
        "jurisdiction": input_params["jurisdiction"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_markets(input_params, doc, output_parser):
    return {
        "markets": input_params["markets"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_sourcing(input_params, doc, output_parser):
    return {
        "sourcing": input_params["sourcing"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_production(input_params, doc, output_parser):
    return {
        "production": input_params["production"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_products_and_services_offered(input_params, doc, output_parser):
    return {
        "products_and_services_offered": input_params["products_and_services_offered"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }

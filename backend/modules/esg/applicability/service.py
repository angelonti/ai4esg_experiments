import json
import logging
import os
import sys

from modules.embedding.utils import to_relevant_embeddings
from modules.prompts.applicability_evaluation_prompts import (
    KEY_PARAMETERS,
    SEARCH_PROMPT_MAP,
    APPLICABILITY_PROMPT_MAP,
    KEY_PARAMETERS_TO_VARIABLES_MAP
)
from dotenv import load_dotenv, find_dotenv
import warnings
from config import config
import openai
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import SimpleJsonOutputParser
from modules.document.pydantic.models import KeyParameterEvaluation
from modules.document.utils.token_utils import TokenStats
from modules.llm.utils import get_text_embedding
from modules.llm.clients.base import LLMClient
from modules.evaluation_result.schemas import EvaluationResultCreate
from modules.evaluation_result.service import create as create_evaluation_result

logging.basicConfig(level=logging.DEBUG, filename=config.log_path, format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)

warnings.filterwarnings("ignore")

_ = load_dotenv(find_dotenv(filename="demo.env"))

openai.api_key = config.azure_openai_key
openai.api_base = config.api_endpoint
openai.api_version = "2023-05-15"

warnings.filterwarnings("ignore")

chatOpenAI = AzureChatOpenAI(
    temperature=config.temperature,
    deployment_name=config.azure_gpt4_deployment_name,
    openai_api_base=openai.api_base,
    openai_api_version=openai.api_version,
    openai_api_key=openai.api_key,
)


def load_saved_results(results_file):
    with open(results_file, "r") as f:
        json_data = json.load(f)
    return json_data


def load_saved_evaluations(results_file):
    if os.path.isfile(results_file):  # check if there are saved results and load them
        saved_results = load_saved_results(results_file)
        return saved_results
    return {}


def delete_saved_results(results_file):
    try:
        os.remove(results_file)
    except FileNotFoundError:
        logger.error(f"File {results_file} does not exist.")
    except OSError as e:
        logger.error(f"Error: {e.filename} - {e.strerror}")


def remove_old_saved_results():
    files = list(filter(lambda x: x.endswith("_results.json"), os.listdir()))

    if len(files) >= 2:
        for file in os.listdir():
            logger.info(f"removing file {file}")
            if file.endswith("_results.json"):
                delete_saved_results(file)


def get_remaining_key_parameters(remaining_key_parameters, saved_results, title):
    if "data" in saved_results:
        processed_key_parameters = [d["key_parameter"] for d in saved_results["data"] if d["title"] == title]
        remaining_key_parameters = list(set(remaining_key_parameters) - set(processed_key_parameters))
    return remaining_key_parameters


async def determine_applicability_single(input_params: dict, title: str, evaluation_name: str, recorder: list = None) -> dict:
    """
    Determine if a regulation applies to a company based on the company's key parameters.

    Args:
    input_params (dict): The input data.
    title (str): The title of the regulation.
    evaluation_name (str): The name of the evaluation.

    Returns:
    dict: The output data.
    """

    remove_old_saved_results()
    token_stats = TokenStats()
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    logger.info(f"Starting applicability evaluation with name: {evaluation_name}")
    logger.info(f"Starting applicability evaluation for {title}")
    logger.info(f"Input parameters:\n {input_params}")
    RESULTS_FILE = f"./{evaluation_name}_results.json"
    results = {"data": []}

    remaining_key_parameters = KEY_PARAMETERS

    saved_results = load_saved_evaluations(RESULTS_FILE)
    if "data" in saved_results:
        results = saved_results
        remaining_key_parameters = get_remaining_key_parameters(remaining_key_parameters, results, title)

    logger.info(f"Remaining key parameters: {remaining_key_parameters}")
    params_len = len(remaining_key_parameters)
    finished_params = 0
    for key_parameter in remaining_key_parameters:
        search_prompt = SEARCH_PROMPT_MAP[key_parameter]
        eval_prompt = APPLICABILITY_PROMPT_MAP[key_parameter]
        embedding_response = await get_text_embedding(search_prompt)
        question_embedding = embedding_response.data[0].embedding
        # Refactor this later. Now easier to test like this
        if config.use_hybrid:
            embeddings_with_scores = LLMClient.get_relevant_embeddings_hybrid(
                search_prompt, question_embedding, config.max_content, title=title)
        else:
            embeddings_with_scores = LLMClient.get_relevant_embeddings(question_embedding, config.max_content, title=title)

        embeddings = [embedding for embedding, _ in embeddings_with_scores]
        relevant_embeddings = to_relevant_embeddings(embeddings_with_scores)
        document_id = embeddings[0].document.id
        prompt = PromptTemplate.from_template(eval_prompt)
        doc = "".join([embedding.text + "\n\n" for embedding in embeddings])
        doc_title = embeddings[0].document.title
        output_parser = SimpleJsonOutputParser(pydantic_object=KeyParameterEvaluation)
        chain = LLMChain(llm=chatOpenAI, verbose=True, prompt=prompt, output_parser=output_parser, output_key="response")
        invoke_params = get_invoke_params(input_params, key_parameter, doc, output_parser)
        prepped_prompt = chain.prep_prompts([invoke_params])
        input_tokens = token_stats._calculate_total_document_tokens([prepped_prompt[0][0].text])
        logger.info(f"Input tokens: {input_tokens}")
        total_input_tokens += input_tokens
        response = chain.invoke(invoke_params)
        output_tokens = token_stats._calculate_total_document_tokens([str(response["response"])])
        logger.info(f"Output tokens: {output_tokens}")
        total_output_tokens += output_tokens
        record = {
            "key_parameter": key_parameter,
            "key_parameter_value": input_params[KEY_PARAMETERS_TO_VARIABLES_MAP[key_parameter]],
            "response": response["response"],
            "relevant_embeddings": relevant_embeddings,
            "title": doc_title,
        }
        if key_parameter in ["Assets", "Revenue"]:
            record["currency"] = input_params["currency"]

        results["data"].append(record)

        with open(RESULTS_FILE, "w", encoding="utf8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"saved results to results/{RESULTS_FILE} for key parameter {key_parameter}")

        if recorder is not None:
            finished_params += 1
            message = f"Parameter: **{key_parameter}** done. {finished_params} out of {params_len} completed..."
            recorder.append(message)
            logger.info(message)

        if response["response"]["answer"] == "yes":
            message = f"Parameter **{key_parameter}** is applicable to the company. Other parameters will be skipped."
            recorder.append(message)
            logger.info(message)
            break

    # save to database
    evaluation_result = EvaluationResultCreate(
        document_id=document_id,
        evaluation_name=evaluation_name,
        evaluation=results
    )
    create_evaluation_result(evaluation_result)

    if recorder is not None:
        recorder.append(f"Applicability evaluation **{evaluation_name}** completed")

    logger.info(f"Applicability evaluation {evaluation_name} completed")
    logger.info(f"deleting temp results file: {RESULTS_FILE}")
    delete_saved_results(RESULTS_FILE)
    logger.info(f"Total input tokens: {total_input_tokens}")
    logger.info(f"Total output tokens: {total_output_tokens}")


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
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_number_of_employees(input_params, doc, output_parser):
    return {
        "num_employees": input_params["num_employees"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_assets(input_params, doc, output_parser):
    return {
        "assets": input_params["assets"],
        "currency": input_params["currency"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_revenue(input_params, doc, output_parser):
    return {
        "revenue": input_params["revenue"],
        "currency": input_params["currency"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_offering_of_financial_products(input_params, doc, output_parser):
    return {
        "is_offering_financial_products": input_params["is_offering_financial_products"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_REACH(input_params, doc, output_parser):
    return {
        "is_REACH": input_params["is_REACH"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_battery(input_params, doc, output_parser):
    return {
        "is_battery": input_params["is_battery"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_jurisdiction(input_params, doc, output_parser):
    return {
        "jurisdiction": input_params["jurisdiction"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_markets(input_params, doc, output_parser):
    return {
        "markets": input_params["markets"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_sourcing(input_params, doc, output_parser):
    return {
        "sourcing": input_params["sourcing"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_production(input_params, doc, output_parser):
    return {
        "production": input_params["production"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }


def get_invoke_params_products_and_services_offered(input_params, doc, output_parser):
    return {
        "products_and_services_offered": input_params["products_and_services_offered"],
        "company_name": input_params["company_name"],
        "doc": doc,
        "format_instructions": output_parser.get_format_instructions()
    }

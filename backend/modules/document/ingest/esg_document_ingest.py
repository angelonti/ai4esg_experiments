import json
import logging
import os
import sys
from typing import Union

import openai
from dotenv import load_dotenv, find_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import SimpleJsonOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate
from unstructured.partition.pdf import Element

from backend.config import config
from backend.modules.document.pydantic.models import (
    RegulationKeyParameterDataList,
    RegulationKeyParameterData,
    RequirementsAndPenalties
)
from backend.modules.prompts.legal_info_extraction_prompts import (
    priming,
    prompt_key_parameters,
    prompt_requirements_and_penalties,
    key_parameters
)

from backend.modules.document.utils.DocumentReader import (
    DocumentReader,
    get_document_metadata,
)
from backend.modules.document.utils.DocumentReaderProviders import Providers
from modules.document.schemas import DocumentParsed, DocType
from modules.document.service import create_from_partitions as create_document_from_partitions
from modules.embedding.utils import chunk_partitions

logging.basicConfig(level=logging.DEBUG, filename="ai4esg.log", format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)

_ = load_dotenv(find_dotenv(filename="local.env"))

OUTPUT_KEY = "response"
# KEY_PARAMETERS_FILE = "key_parameters.json"
REQUIREMENTS_AND_PENALTIES_FILE = "reqs_and_penalties.json"
# KEY_PARAMETERS_DIR = "key_parameters"
REQUIREMENTS_AND_PENALTIES_DIR = "reqs_and_penalties"


class EsgRegulationIngestor:
    def __init__(self, file_path: str, title: str = None, batch_size: int = 2, num_pages: int = None,
                 init_docs: bool = True) -> None:
        if init_docs:
            self.documents = (DocumentReader(provider=Providers.UNSTRUCTURED, file_path=file_path)).read()
            self.documents_paged = self.to_paged_texts(self.documents)
            self.num_pages = num_pages or len(self.documents_paged)
            self.metadata = get_document_metadata(self.documents, title=title)
        # self.key_parameters_parser = self.get_default_key_parameters_parser()
        self.reqs_and_penalties_parser = self.get_default_reqs_and_penalties_parser()
        self.system_message_prompt_template = SystemMessagePromptTemplate.from_template(" ".join(priming.split()))
        # self.prompt_template_key_parameters = self.system_message_prompt_template + prompt_key_parameters
        self.prompt_template_reqs_and_penalties = self.system_message_prompt_template + prompt_requirements_and_penalties
        self.chatModel = self.get_chat_model()
        self.batch_size = batch_size

    async def ingest_all(self) -> None:
        # self.ingest_key_parameters()
        await create_document_from_partitions(self.documents, title=self.metadata["title"])
        await self.ingest_reqs_and_penalties()

    async def ingest_reqs_and_penalties(self) -> None:
        chain_reqs_and_penalties = self.get_chain_reqs_and_penalties()

        start = 0

        title = self.metadata["title"].replace(" ", "_").replace("/", "_")

        full_file_path = os.path.join(REQUIREMENTS_AND_PENALTIES_DIR, f'{title}_{REQUIREMENTS_AND_PENALTIES_FILE}')

        reqs_and_penalties_data = self.load_saved_data(full_file_path)

        if reqs_and_penalties_data is not None:
            start = reqs_and_penalties_data["metadata"]["processed_pages"]

        for i in range(start, self.num_pages, self.batch_size):
            end = min(i + self.batch_size, self.num_pages)
            logger.debug(f"########## READING PAGES {i} to {end}  ##########")
            doc_batch = "".join([f'{doc}\n\n' for doc in self.documents_paged[i:end]])

            response_reqs_and_penalties = chain_reqs_and_penalties.apply([
                {
                    "doc": doc_batch,
                    "format_instructions": self.reqs_and_penalties_parser.get_format_instructions()
                }
            ])
            response_reqs_and_penalties = response_reqs_and_penalties[0]["response"]
            logger.debug("########## RESPONSE ##########")
            logger.debug(response_reqs_and_penalties)
            if reqs_and_penalties_data is None:
                reqs_and_penalties_data = response_reqs_and_penalties
            else:
                reqs_and_penalties_data = self.merge_reqs_and_penalties_json(reqs_and_penalties_data,
                                                                             response_reqs_and_penalties)
            reqs_and_penalties_data["metadata"] = self.metadata
            reqs_and_penalties_data["metadata"]["processed_pages"] = end
            os.makedirs(REQUIREMENTS_AND_PENALTIES_DIR, exist_ok=True)
            with open(full_file_path, "w") as f:
                json.dump(reqs_and_penalties_data, f, indent=4)

        if reqs_and_penalties_data["metadata"]["processed_pages"] == len(self.documents_paged):
            # save_reqs_and_penalties_db(reqs_and_penalties_data) TODO: Implement this function
            logger.debug("##########REQS AND PENALTIES INGESTION COMPLETED ##########")

    """
    def ingest_key_parameters(self) -> None:
        chain_key_parameters = self.get_chain_key_parameters()

        start = 0

        title = self.metadata["title"].replace(" ", "_").replace("/", "_")

        full_file_path = os.path.join(KEY_PARAMETERS_DIR, f'{title}_{KEY_PARAMETERS_FILE}')

        key_parameters_data = self.load_saved_data(full_file_path)

        if key_parameters_data is not None:
            start = key_parameters_data["metadata"]["processed_pages"]

        for i in range(start, self.num_pages, self.batch_size):
            end = min(i + self.batch_size, self.num_pages)
            logger.debug(f"########## READING PAGES {i} to {end}  ##########")
            doc_batch = "".join([f'{doc}\n\n' for doc in self.documents_paged[i:end]])

            response_key_parameters = chain_key_parameters.apply([
                {
                    "doc": doc_batch,
                    "key_parameters": key_parameters,
                    "format_instructions": self.key_parameters_parser.get_format_instructions()
                }
            ])
            response_key_parameters = response_key_parameters[0]["response"]
            logger.debug("########## RESPONSE ##########")
            logger.debug(response_key_parameters)
            if key_parameters_data is None:
                key_parameters_data = response_key_parameters
            else:
                key_parameters_data = self.merge_key_parameters_json(key_parameters_data, response_key_parameters)

            key_parameters_data["metadata"] = self.metadata
            key_parameters_data["metadata"]["processed_pages"] = end
            os.makedirs(KEY_PARAMETERS_DIR, exist_ok=True)
            with open(full_file_path, "w") as f:
                json.dump(key_parameters_data, f, indent=4)
          

    def get_chain_key_parameters(self):
        return LLMChain(
            llm=self.chatModel,
            verbose=True,
            prompt=self.prompt_template_key_parameters,
            output_parser=self.key_parameters_parser,
            output_key=OUTPUT_KEY
        )
    
        
    @staticmethod
    def merge_key_parameters_json(dest_json: dict[str, list[RegulationKeyParameterData]],
                                  source_json: dict[str, list[RegulationKeyParameterData]]) -> dict[
        str, list[RegulationKeyParameterData]]:
        for source_data in source_json["data"]:
            key_parameter_name = source_data["key_parameter"]
            key_parameter_excerpts = source_data["excerpts"]
            for dest_data in dest_json["data"]:
                if dest_data["key_parameter"] == key_parameter_name:
                    dest_data["excerpts"].extend(key_parameter_excerpts)
                    break
            else:
                dest_json["data"].append(source_data)
        return dest_json
        
    @staticmethod
    def get_default_key_parameters_parser():
        return SimpleJsonOutputParser(pydantic_object=RegulationKeyParameterDataList)
    """
    def get_chain_reqs_and_penalties(self):
        return LLMChain(
            llm=self.chatModel,
            verbose=True,
            prompt=self.prompt_template_reqs_and_penalties,
            output_parser=self.reqs_and_penalties_parser,
            output_key=OUTPUT_KEY
        )

    @staticmethod
    def load_saved_data(filename: str) -> Union[dict, None]:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                return data
        return None

    @staticmethod
    def merge_reqs_and_penalties_json(dest_json: dict[str, dict],
                                      source_json: dict[str, dict]) -> dict[str, dict]:
        for source_key, source_value in source_json["data"].items():
            key_excerpts = source_value["excerpts"]
            for dest_key, dest_value in dest_json["data"].items():
                if source_key == dest_key:
                    dest_value["excerpts"].extend(key_excerpts)
                    break
        return dest_json

    @staticmethod
    def get_default_reqs_and_penalties_parser():
        return SimpleJsonOutputParser(pydantic_object=RequirementsAndPenalties)

    @staticmethod
    def get_chat_model():
        openai.api_key = config.azure_openai_key
        openai.api_base = config.api_endpoint
        openai.api_version = "2023-05-15"

        return AzureChatOpenAI(
            temperature=0.0,
            deployment_name=config.azure_gpt4_deployment_name,
            openai_api_base=openai.api_base,
            openai_api_version=openai.api_version,
            openai_api_key=openai.api_key,
        )

    @staticmethod
    def to_paged_texts(documents: list[Element]) -> list[str]:
        num_pages = documents[-1].metadata.page_number
        documents_paged = [[x for x in documents if x.metadata.page_number == page] for page in range(1, num_pages + 1)]
        text_documents_paged = [
            str(" ".join([f'{x.text}\n\n' if type(x).__name__ == "Title" else x.text for x in page])) for page in
            documents_paged]
        return text_documents_paged

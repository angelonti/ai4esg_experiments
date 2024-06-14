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

from config import config
from modules.document.pydantic.models import (
    RequirementsAndPenalties
)
from modules.document.utils.DocumentReader import (
    DocumentReader,
    get_document_metadata,
)
from modules.document.utils.DocumentReaderProviders import Providers
from modules.prompts.legal_info_extraction_prompts import (
    priming,
    prompt_requirements_and_penalties
)
from modules.document.schemas import Document
from modules.document.service import create_from_partitions as create_document_from_partitions
from modules.penalty.schemas import PenaltyCreate
from modules.penalty.service import create as create_penalty
from modules.requirement.schemas import RequirementCreate
from modules.requirement.service import create as create_requirement
from modules.requirement.service import get_summary_by_document_id as get_requirement_summary_by_document_id
from modules.penalty.service import get_summary_by_document_id as get_penalty_summary_by_document_id
from modules.document.summary.service import SummaryService

logging.basicConfig(level=logging.DEBUG, filename=config.log_path, format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)

_ = load_dotenv(find_dotenv(filename="demo.env"))

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
        self.summary_service = SummaryService(self.chatModel)
        self.batch_size = batch_size

    async def ingest_all(self) -> None:
        # self.ingest_key_parameters()
        created_doc = await create_document_from_partitions(self.documents, title=self.metadata["title"])
        await self.ingest_reqs_and_penalties(created_doc)
        await self.create_summaries(created_doc.id)

    async def create_summaries(self, document_id) -> None:
        requirements_summary = get_requirement_summary_by_document_id(document_id)
        if requirements_summary is None:
            await self.summary_service.create_requirements_summary(document_id)
        else:
            logger.debug("Requirements summary already exists")

        penalties_summary = get_penalty_summary_by_document_id(document_id)
        if penalties_summary is None:
            await self.summary_service.create_penalties_summary(document_id)
        else:
            logger.debug("Penalties summary already exists")

    async def ingest_reqs_and_penalties(self, created_doc) -> None:
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
            if response_reqs_and_penalties is not None:
                self.save_reqs_db(response_reqs_and_penalties, doc=created_doc, pages_start=i, pages_end=end)
                self.save_penalties_db(response_reqs_and_penalties, doc=created_doc, pages_start=i, pages_end=end)
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

        #if reqs_and_penalties_data["metadata"]["processed_pages"] == len(self.documents_paged):
        # save_reqs_and_penalties_db(reqs_and_penalties_data) TODO: Implement this function
        logger.debug("##########REQS AND PENALTIES INGESTION COMPLETED ##########")

    def find_text_page_number(self, text: str, pages_start, pages_end):
        for i in range(pages_start, pages_end):
            if text in self.documents_paged[i]:
                return i + 1  # page numbers are 1-indexed
        return 0

    def save_reqs_db(self, response_reqs_and_penalties: dict, doc: Document, pages_start: int, pages_end: int):
        data = response_reqs_and_penalties["data"]
        reqs = data["requirements_for_compliance"]["excerpts"]
        for req in reqs:
            req_create = RequirementCreate(
                document_id=doc.id,
                text=req["text"],
                page_number=self.find_text_page_number(req["text"], pages_start, pages_end),
            )
            create_requirement(req_create)

    def save_penalties_db(self, response_reqs_and_penalties: dict, doc: Document, pages_start: int, pages_end: int):
        data = response_reqs_and_penalties["data"]
        penalties = data["penalties"]["excerpts"]
        for penalty in penalties:
            penalty_create = PenaltyCreate(
                document_id=doc.id,
                text=penalty["text"],
                page_number=self.find_text_page_number(penalty["text"], pages_start, pages_end),
            )
            create_penalty(penalty_create)

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
            model=config.azure_gpt4_deployment_name,
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

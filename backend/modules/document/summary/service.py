import tiktoken
import logging
import sys
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document as LangChainDocument

from modules.requirement.schemas import Requirement, RequirementSummaryCreate, RequirementSummary
from modules.penalty.schemas import Penalty, PenaltySummaryCreate, PenaltySummary
from modules.requirement.service import create_summary as create_requirement_summary
from modules.requirement.service import get_by_document_id as get_requirements_by_document_id
from modules.penalty.service import create_summary as create_penalty_summary
from modules.penalty.service import get_by_document_id as get_penalties_by_document_id
from modules.prompts.summary_prompts import prompt_summary_requirements, prompt_summary_penalties


from app_config import config

logging.basicConfig(level=logging.DEBUG, filename=config.log_path, format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)


class SummaryService:
    def __init__(self, chat_model):
        self.chat_model = chat_model

    async def create_requirements_summary(self, document_id: str) -> RequirementSummary:
        requirements: list[Requirement] = get_requirements_by_document_id(document_id)
        prompt = PromptTemplate(template=prompt_summary_requirements, input_variables=["text"])
        requirement_summary: str = await self.create_summary_from_texts([requirement.text for requirement in requirements], prompt=prompt)
        requirement_summary_create = RequirementSummaryCreate(
            document_id=document_id,
            summary=requirement_summary
        )
        return create_requirement_summary(requirement_summary_create)

    async def create_penalties_summary(self, document_id: str) -> PenaltySummary:
        penalties: list[Penalty] = get_penalties_by_document_id(document_id)
        prompt = PromptTemplate(template=prompt_summary_penalties, input_variables=["text"])
        penalty_summary: str = await self.create_summary_from_texts([penalty.text for penalty in penalties], prompt=prompt)
        penalty_summary_create = PenaltySummaryCreate(
            document_id=document_id,
            summary=penalty_summary
        )
        return create_penalty_summary(penalty_summary_create)

    async def create_summary_from_texts(self, texts: list[str], prompt: PromptTemplate) -> str:
        joined_texts: str = "\n\n".join(texts)
        docs = [LangChainDocument(page_content=t) for t in texts]
        token_encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(token_encoding.encode(joined_texts))
        max_tokens = config.prompt_size

        logger.info(f"Max number of tokens: {max_tokens}")
        logger.info(f"Number of tokens: {num_tokens}")

        if num_tokens < config.prompt_size:
            logger.debug("Using stuff chain for summarization")
            chain = load_summarize_chain(llm=self.chat_model, prompt=prompt, chain_type="stuff", verbose=True)
        else:
            logger.debug("Using map reduce chain for summarization")
            chain = load_summarize_chain(llm=self.chat_model, combine_prompt=prompt, chain_type="map_reduce", verbose=True)

        summary = chain.run(docs)

        return summary

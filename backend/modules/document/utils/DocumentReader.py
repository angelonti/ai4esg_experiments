from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.document_loaders import PyPDFLoader
from llama_index import SimpleDirectoryReader
from unstructured.cleaners.core import clean_non_ascii_chars, replace_unicode_quotes, clean_extra_whitespace, \
    bytes_string_to_string
from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf

from modules.document.utils.DocumentReaderProviders import Providers as providers


class DocumentReader:
    def __init__(self, file_path, provider):
        self.file_path = file_path
        self.provider = provider
        self.documents = None
        self.documents_paged = None

    def read(self, is_directory=False):
        if self.provider == providers.LANG_CHAIN:
            if is_directory:
                return PyPDFDirectoryLoader(self.file_path).load()
            else:
                return PyPDFLoader(self.file_path).load()
        elif self.provider == providers.LLAMA_INDEX:
            return SimpleDirectoryReader(
                input_files=[self.file_path]
            ).load_data()
        elif self.provider == providers.UNSTRUCTURED:
            self.documents = partition_pdf(
                filename=self.file_path,
                strategy="hi_res",
                chunking_strategy="by-title",
            )
            return self.preprocess_documents(self.documents)
        else:
            raise Exception("Unknown provider")

    def preprocess_documents(self, documents: list[Element]) -> list[Element]:
        documents = self.filter_elements(documents)
        self.clean_text(documents)
        return documents

    @staticmethod
    def filter_elements(documents: list[Element]):
        filtered_documents = [x for x in documents if type(x).__name__ != "Header" and type(x).__name__ != "Footer"]
        return filtered_documents

    @staticmethod
    def clean_text(documents: list[Element]) -> None:
        for element in documents:
            element.apply(clean_non_ascii_chars)
            element.apply(replace_unicode_quotes)
            element.apply(clean_extra_whitespace)
            element.apply(bytes_string_to_string)

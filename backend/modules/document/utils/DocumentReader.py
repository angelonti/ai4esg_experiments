from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import PyPDFDirectoryLoader
from modules.document.utils.DocumentReaderProviders import Providers as providers
from llama_index import SimpleDirectoryReader
from unstructured.partition.pdf import partition_pdf


class DocumentReader:
    def __init__(self, file_path, provider):
        self.file_path = file_path
        self.provider = provider

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
            return partition_pdf(self.file_path)
        else:
            raise Exception("Unknown provider")

from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.document_loaders import PyPDFLoader
from unstructured.cleaners.core import clean_non_ascii_chars, replace_unicode_quotes, clean_extra_whitespace, \
    bytes_string_to_string
from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf

from modules.document.schemas import DocumentParsed, DocType
from modules.document.utils.DocumentReaderProviders import Providers
from modules.embedding.utils import chunk_partitions


class DocumentReader:
    def __init__(self, file_path, provider):
        self.file_path = file_path
        self.provider = provider
        self.documents = None
        self.documents_paged = None

    def read(self, is_directory=False):
        if self.provider.value == Providers.LANG_CHAIN.value:
            if is_directory:
                return PyPDFDirectoryLoader(self.file_path).load()
            else:
                return PyPDFLoader(self.file_path).load()
        elif self.provider.value == Providers.UNSTRUCTURED.value:
            self.documents = partition_pdf(
                filename=self.file_path,
                strategy="hi_res"
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
        exclusion_list = ["Header", "Footer", "Image", "FigureCaption"]
        filtered_documents = [x for x in documents if type(x).__name__ not in exclusion_list]
        return filtered_documents

    @staticmethod
    def clean_text(documents: list[Element]) -> None:
        for element in documents:
            # element.apply(clean_non_ascii_chars)
            element.apply(replace_unicode_quotes)
            element.apply(clean_extra_whitespace)
            # element.apply(bytes_string_to_string)


def get_document_metadata(documents: list[Element], title: str = None) -> dict[str, str]:
    if title is None:
        title = extract_title(documents)
    source = documents[0].metadata.filename
    metadata = {"title": title, "source": source}
    return metadata


def parse_esg_document(partitions: list[Element], title: str = None) -> DocumentParsed:
    metadata = get_document_metadata(partitions, title=title)
    chunks = chunk_partitions(partitions)
    text = "".join([x.text for x in chunks])
    return DocumentParsed(
        title=metadata["title"],
        text=text,
        doc_type=DocType.PDF,
        source=metadata["source"]
    )


def extract_title(documents):
    title = ""
    title_found = False
    for doc in documents:
        if title_found and type(doc).__name__ != "Title":
            title = title.strip()
            break
        if type(doc).__name__ == "Title":
            if len(doc.text) > 1:
                title_found = True
                title += doc.text + " "
    return title

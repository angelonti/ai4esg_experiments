import tiktoken


class TokenStats:
    token_encoding = tiktoken.get_encoding("cl100k_base")

    def __init__(self, token_encoding: str = "cl100k_base"):
        self.token_encoding = tiktoken.get_encoding(token_encoding)

    def get_stats(self, documents: list[str]):
        return {
            "avg_tokens_per_page": self._calculate_avg_tokens_per_page(documents),
            "total_document_tokens": self._calculate_total_document_tokens(documents),
            "max_tokens_per_page": self._calculate_max_tokens_per_page(documents),
        }

    def _calculate_avg_tokens_per_page(self, documents):
        total_tokens = 0
        total_pages = 0
        for doc in documents:
            total_tokens += len(self.token_encoding.encode(doc))
            total_pages += 1
        return total_tokens / total_pages

    def _calculate_total_document_tokens(self, documents):
        total_tokens = 0
        for doc in documents:
            total_tokens += len(self.token_encoding.encode(doc))
        return total_tokens

    def _calculate_max_tokens_per_page(self, documents):
        max_tokens = 0
        for doc in documents:
            max_tokens = max(max_tokens, len(self.token_encoding.encode(doc)))
        return max_tokens

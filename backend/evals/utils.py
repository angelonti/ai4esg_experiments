def normalize_text(text: str) -> str:
    if text.endswith("."):
        text = text[:-1]
    text = text.lower()
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text

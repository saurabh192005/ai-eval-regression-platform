import re
import unicodedata

EVALUATOR_VERSION = "exact_match_v2"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.strip().lower()
    text = re.sub(r"^[\"'`]+|[\"'`.!]+$", "", text)
    return text.strip()


def is_match(response: str, expected: str) -> bool:
    return normalize(response) == normalize(expected)
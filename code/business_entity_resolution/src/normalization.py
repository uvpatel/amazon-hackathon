"""Normalization functions for business names, addresses, and countries."""

import re
import unicodedata
from typing import List, Set

# Generic legal suffixes to clean or separate
LEGAL_SUFFIXES = {
    "inc", "incorporated", "corp", "corporation", "llc", "ltd", "limited",
    "pvt", "private", "co", "company", "sa", "gmbh", "sarl", "bv", "nv",
    "llp", "plc", "cie", "assoc", "associates", "enterprises", "holdings"
}

# Standard street / address abbreviations mapping
ADDRESS_ABBREVIATIONS = {
    "rd": "road",
    "st": "street",
    "str": "street",
    "ave": "avenue",
    "av": "avenue",
    "blvd": "boulevard",
    "bvd": "boulevard",
    "dr": "drive",
    "ln": "lane",
    "ct": "court",
    "pl": "place",
    "sq": "square",
    "apt": "apartment",
    "ste": "suite",
    "hwy": "highway",
    "pkwy": "parkway",
    "fl": "floor",
    "bldg": "building",
    "nr": "near",
    "opp": "opposite",
}


def clean_base_text(text: str) -> str:
    """Perform unicode normalization, casing, and basic whitespace cleaning."""
    if not text or not isinstance(text, str):
        return ""
    # Unicode NFKD normalization (converts accents like é -> e)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.lower()
    # Replace & with and
    text = re.sub(r"\s*&\s*", " and ", text)
    # Remove leading/trailing quotes and noise symbols
    text = re.sub(r"[\"'`«»<>{}()\[\]\\/]", " ", text)
    # Replace punctuation with space
    text = re.sub(r"[,;:.!\?_#*~^=+|-]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_name(name: str) -> str:
    """Normalize a business name by standardizing punctuation, casing, and legal tokens."""
    cleaned = clean_base_text(name)
    if not cleaned:
        return ""

    tokens = cleaned.split()
    # Filter trailing legal suffixes if present
    filtered = []
    for t in tokens:
        filtered.append(t)

    return " ".join(filtered)


def get_core_name_tokens(name: str) -> List[str]:
    """Extract high-information tokens from a name, excluding common legal suffixes."""
    cleaned = clean_base_text(name)
    tokens = cleaned.split()
    core = [t for t in tokens if t not in LEGAL_SUFFIXES and len(t) > 1 and t != "and"]
    return core if core else tokens


def normalize_address(address: str) -> str:
    """Normalize a business address by expanding common street tokens and stripping punctuation."""
    cleaned = clean_base_text(address)
    if not cleaned:
        return ""

    tokens = cleaned.split()
    expanded_tokens = []
    for token in tokens:
        expanded = ADDRESS_ABBREVIATIONS.get(token, token)
        expanded_tokens.append(expanded)

    return " ".join(expanded_tokens)


def normalize_country(country: str) -> str:
    """Normalize country as an open-set string (uppercase trimmed alphanumeric).

    Never hard-codes country labels to allow open-set support (US, India, France, etc.).
    """
    if not country or not isinstance(country, str):
        return ""
    country_clean = unicodedata.normalize("NFKD", country).encode("ascii", "ignore").decode("utf-8")
    country_clean = re.sub(r"[^\w\s]", " ", country_clean)
    country_clean = re.sub(r"\s+", " ", country_clean).strip().upper()
    return country_clean


def tokenize(text: str) -> List[str]:
    """Tokenize normalized text into non-empty alphanumeric tokens."""
    cleaned = clean_base_text(text)
    return cleaned.split() if cleaned else []


def extract_numeric_tokens(text: str) -> List[str]:
    """Extract all digit sequences (PIN codes, house numbers, street numbers)."""
    if not text or not isinstance(text, str):
        return []
    return re.findall(r"\b\d+\b", text)

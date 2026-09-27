"""Unit tests for text, name, address, and open-set country normalization."""

import pytest
from src.normalization import (
    clean_base_text,
    normalize_name,
    get_core_name_tokens,
    normalize_address,
    normalize_country,
    tokenize,
    extract_numeric_tokens,
)


def test_clean_base_text_accents():
    assert clean_base_text("Café des Artistes") == "cafe des artistes"
    assert clean_base_text("<< Team École >>") == "team ecole"


def test_clean_base_text_ampersand_and_punctuation():
    assert clean_base_text("A & B, Inc. / LLC") == "a and b inc llc"
    assert clean_base_text("  Spaced   Out   Name  ") == "spaced out name"


def test_normalize_name():
    assert normalize_name("Prime Money, LLC") == "prime money llc"
    assert normalize_name("Orelee's Barbershop") == "orelee s barbershop"
    assert normalize_name("") == ""
    assert normalize_name(None) == ""


def test_get_core_name_tokens():
    core = get_core_name_tokens("Vision Partners Corp")
    assert "vision" in core
    assert "partners" in core
    assert "corp" not in core


def test_normalize_address_abbreviations():
    addr = "1064 Newton Rd, Unit 11, Ste 400"
    norm = normalize_address(addr)
    assert "road" in norm
    assert "suite" in norm
    assert "1064" in norm
    assert "11" in norm


def test_normalize_country_open_set():
    # US, India, France, and unknown countries
    assert normalize_country("US") == "US"
    assert normalize_country("  india  ") == "INDIA"
    assert normalize_country("France") == "FRANCE"
    assert normalize_country("germany") == "GERMANY"
    assert normalize_country("Japon / 日本") == "JAPON"
    assert normalize_country("") == ""
    assert normalize_country(None) == ""


def test_extract_numeric_tokens():
    addr = "1795 Westchester Drive, High Point, NC 27262"
    nums = extract_numeric_tokens(addr)
    assert nums == ["1795", "27262"]

    assert extract_numeric_tokens("No numbers here") == []
    assert extract_numeric_tokens("") == []

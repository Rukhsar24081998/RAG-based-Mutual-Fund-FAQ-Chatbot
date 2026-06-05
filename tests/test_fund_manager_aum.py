"""
Tests for Fund Manager and AUM intent handling in build_structured_answer.
Run from the project root:  python -m pytest tests/test_fund_manager_aum.py -v
"""

import os
import sys

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.assembler import SCHEME_DATA, build_structured_answer, extract_scheme_name

# ---------------------------------------------------------------------------
# extract_scheme_name
# ---------------------------------------------------------------------------


def test_extract_exact_scheme_names():
    """Full scheme names embedded in a question should resolve correctly."""
    assert (
        extract_scheme_name("Who is the fund manager of HDFC Flexi Cap Fund?")
        == "HDFC Flexi Cap Fund"
    )
    assert (
        extract_scheme_name("What is the AUM of HDFC Mid Cap Fund?")
        == "HDFC Mid Cap Fund"
    )
    assert (
        extract_scheme_name("What is the AUM of HDFC Small Cap Fund?")
        == "HDFC Small Cap Fund"
    )
    assert extract_scheme_name("Who manages HDFC Defence Fund?") == "HDFC Defence Fund"
    assert (
        extract_scheme_name("What is the AUM of HDFC Silver ETF Fund of Fund?")
        == "HDFC Silver ETF Fund of Fund"
    )


def test_extract_partial_alias_flexi_cap():
    assert (
        extract_scheme_name("Who is the fund manager of the flexi cap?")
        == "HDFC Flexi Cap Fund"
    )


def test_extract_partial_alias_mid_cap():
    assert extract_scheme_name("What is the AUM of mid cap?") == "HDFC Mid Cap Fund"


def test_extract_partial_alias_small_cap():
    assert extract_scheme_name("fund manager of small cap") == "HDFC Small Cap Fund"


def test_extract_partial_alias_defence():
    assert extract_scheme_name("AUM of hdfc defence") == "HDFC Defence Fund"


def test_extract_partial_alias_defense_spelling():
    assert extract_scheme_name("AUM of hdfc defense fund") == "HDFC Defence Fund"


def test_extract_partial_alias_silver_etf():
    assert (
        extract_scheme_name("fund manager of silver etf")
        == "HDFC Silver ETF Fund of Fund"
    )


def test_extract_no_match_returns_none():
    assert extract_scheme_name("What is a mutual fund?") is None


# ---------------------------------------------------------------------------
# Fund Manager — build_structured_answer
# ---------------------------------------------------------------------------

FUND_MANAGER_CASES = [
    ("HDFC Flexi Cap Fund", "Chirag Setalvad"),
    ("HDFC Mid Cap Fund", "Srinivas Rao Ravuri"),
    ("HDFC Small Cap Fund", "Srinivas Rao Ravuri"),
    ("HDFC Defence Fund", "Amit Sethiya"),
    ("HDFC Silver ETF Fund of Fund", "Anil Bamboli"),
]


def test_fund_manager_primary_phrase():
    """'fund manager' phrase triggers the correct answer for every scheme."""
    for scheme, manager in FUND_MANAGER_CASES:
        query = f"Who is the fund manager of {scheme}?"
        result = build_structured_answer(query)
        expected = f"The fund manager of {scheme} is {manager}."
        assert result == expected, f"Failed for {scheme}: got {result!r}"


def test_fund_manager_who_manages_phrase():
    """'who manages' phrase is also recognised as a fund-manager query."""
    for scheme, manager in FUND_MANAGER_CASES:
        query = f"Who manages {scheme}?"
        result = build_structured_answer(query)
        expected = f"The fund manager of {scheme} is {manager}."
        assert result == expected, f"Failed for {scheme}: got {result!r}"


def test_fund_manager_response_format():
    """Response must match exactly: 'The fund manager of <Scheme> is <Name>.'"""
    result = build_structured_answer("Who is the fund manager of HDFC Defence Fund?")
    assert result == "The fund manager of HDFC Defence Fund is Amit Sethiya."


def test_fund_manager_no_scheme_returns_none():
    """No scheme in query → build_structured_answer returns None (falls to LLM)."""
    result = build_structured_answer("Who is the fund manager?")
    assert result is None


# ---------------------------------------------------------------------------
# AUM — build_structured_answer
# ---------------------------------------------------------------------------

AUM_CASES = [
    ("HDFC Flexi Cap Fund", "52,347"),
    ("HDFC Mid Cap Fund", "41,892"),
    ("HDFC Small Cap Fund", "32,145"),
    ("HDFC Defence Fund", "15,678"),
    ("HDFC Silver ETF Fund of Fund", "8,542"),
]


def test_aum_primary_phrase():
    """'AUM' keyword triggers the correct answer for every scheme."""
    for scheme, aum in AUM_CASES:
        query = f"What is the AUM of {scheme}?"
        result = build_structured_answer(query)
        expected = (
            f"The assets under management (AUM) of {scheme} are \u20b9{aum} crore."
        )
        assert result == expected, f"Failed for {scheme}: got {result!r}"


def test_aum_assets_under_management_phrase():
    """'assets under management' phrase is also recognised."""
    for scheme, aum in AUM_CASES:
        query = f"What are the assets under management of {scheme}?"
        result = build_structured_answer(query)
        expected = (
            f"The assets under management (AUM) of {scheme} are \u20b9{aum} crore."
        )
        assert result == expected, f"Failed for {scheme}: got {result!r}"


def test_aum_assets_under_short_phrase():
    """'assets under' short form is also recognised."""
    result = build_structured_answer(
        "What are the assets under for HDFC Small Cap Fund?"
    )
    assert (
        result
        == "The assets under management (AUM) of HDFC Small Cap Fund are \u20b932,145 crore."
    )


def test_aum_response_format():
    """Response must match: 'The assets under management (AUM) of <Scheme> are \u20b9<Value> crore.'"""
    result = build_structured_answer("What is the AUM of HDFC Silver ETF Fund of Fund?")
    assert (
        result
        == "The assets under management (AUM) of HDFC Silver ETF Fund of Fund are \u20b98,542 crore."
    )


def test_aum_no_scheme_returns_none():
    """No scheme in query → build_structured_answer returns None."""
    result = build_structured_answer("What is the AUM?")
    assert result is None


# ---------------------------------------------------------------------------
# SCHEME_DATA completeness
# ---------------------------------------------------------------------------

REQUIRED_SCHEMES = [
    "HDFC Flexi Cap Fund",
    "HDFC Mid Cap Fund",
    "HDFC Small Cap Fund",
    "HDFC Defence Fund",
    "HDFC Silver ETF Fund of Fund",
]


def test_all_schemes_have_fund_manager():
    for scheme in REQUIRED_SCHEMES:
        assert scheme in SCHEME_DATA, f"Missing scheme: {scheme}"
        assert SCHEME_DATA[scheme].get("fund_manager"), (
            f"Missing fund_manager for {scheme}"
        )


def test_all_schemes_have_aum():
    for scheme in REQUIRED_SCHEMES:
        assert scheme in SCHEME_DATA, f"Missing scheme: {scheme}"
        assert SCHEME_DATA[scheme].get("aum"), f"Missing aum for {scheme}"

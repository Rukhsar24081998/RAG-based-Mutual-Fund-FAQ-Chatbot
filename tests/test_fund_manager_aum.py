"""
Tests for Fund Manager and AUM intent handling in build_structured_answer.
Run from the project root:  python3 -m pytest tests/test_fund_manager_aum.py -v
"""

import os
import sys

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.assembler import (
    SCHEME_DATA,
    SCHEME_URLS,
    CITATION_UNAVAILABLE,
    SCHEME_DATA_AS_OF,
    build_structured_answer,
    extract_scheme_name,
)

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

# Updated per Fund Facts May 2026 PDFs
FUND_MANAGER_CASES = [
    ("HDFC Flexi Cap Fund", "Amit Ganatra (since February 01, 2026)"),
    ("HDFC Mid Cap Fund", "Chirag Setalvad (since June 25, 2007)"),
    ("HDFC Small Cap Fund", "Chirag Setalvad (since June 28, 2014)"),
    ("HDFC Defence Fund", "Rahul Baijal & Priya Ranjan (w.e.f. April 18, 2025)"),
    ("HDFC Silver ETF Fund of Fund", "Anil Bamboli"),
]


def test_fund_manager_primary_phrase():
    """'fund manager' phrase triggers the correct answer for every scheme."""
    for scheme, manager in FUND_MANAGER_CASES:
        query = f"Who is the fund manager of {scheme}?"
        answer, citation = build_structured_answer(query)
        expected = f"The fund manager of {scheme} is {manager}."
        assert answer == expected, f"Failed for {scheme}: got {answer!r}"
        assert citation == SCHEME_URLS[scheme], f"Citation missing for {scheme}"


def test_fund_manager_who_manages_phrase():
    """'who manages' phrase is also recognised as a fund-manager query."""
    for scheme, manager in FUND_MANAGER_CASES:
        query = f"Who manages {scheme}?"
        answer, citation = build_structured_answer(query)
        expected = f"The fund manager of {scheme} is {manager}."
        assert answer == expected, f"Failed for {scheme}: got {answer!r}"
        assert citation == SCHEME_URLS[scheme], f"Citation missing for {scheme}"


def test_fund_manager_response_format():
    """Response must include correct updated fund manager name."""
    answer, citation = build_structured_answer(
        "Who is the fund manager of HDFC Defence Fund?"
    )
    assert answer == (
        "The fund manager of HDFC Defence Fund is "
        "Rahul Baijal & Priya Ranjan (w.e.f. April 18, 2025)."
    )
    assert citation == SCHEME_URLS["HDFC Defence Fund"]


def test_fund_manager_flexi_cap_updated():
    """Flexi Cap fund manager must be Amit Ganatra (updated Feb 2026)."""
    answer, citation = build_structured_answer(
        "Who is the fund manager of HDFC Flexi Cap Fund?"
    )
    assert "Amit Ganatra" in answer, f"Expected Amit Ganatra, got: {answer}"
    assert "Chirag Setalvad" not in answer, f"Stale data still present: {answer}"


def test_fund_manager_mid_cap_updated():
    """Mid Cap fund manager must be Chirag Setalvad, not Srinivas Rao Ravuri."""
    answer, citation = build_structured_answer(
        "Who is the fund manager of HDFC Mid Cap Fund?"
    )
    assert "Chirag Setalvad" in answer, f"Expected Chirag Setalvad, got: {answer}"
    assert "Srinivas Rao Ravuri" not in answer, f"Stale data still present: {answer}"


def test_fund_manager_no_scheme_returns_none():
    """No scheme in query → build_structured_answer returns None (falls to LLM)."""
    result = build_structured_answer("Who is the fund manager?")
    assert result is None


# ---------------------------------------------------------------------------
# AUM — build_structured_answer
# ---------------------------------------------------------------------------

# Updated per Fund Facts May 2026 PDFs
AUM_CASES = [
    ("HDFC Flexi Cap Fund", "1,00,479.23"),
    ("HDFC Mid Cap Fund", "94,744.72"),
    ("HDFC Small Cap Fund", "38,168.18"),
    ("HDFC Defence Fund", "9,123.61"),
    ("HDFC Silver ETF Fund of Fund", "8,542"),
]


def test_aum_primary_phrase():
    """'AUM' keyword triggers the correct answer for every scheme."""
    for scheme, aum in AUM_CASES:
        query = f"What is the AUM of {scheme}?"
        answer, citation = build_structured_answer(query)
        expected = (
            f"The assets under management (AUM) of {scheme} are \u20b9{aum} crore."
        )
        assert answer == expected, f"Failed for {scheme}: got {answer!r}"
        assert citation == SCHEME_URLS[scheme], f"Citation missing for {scheme}"


def test_aum_assets_under_management_phrase():
    """'assets under management' phrase is also recognised."""
    for scheme, aum in AUM_CASES:
        query = f"What are the assets under management of {scheme}?"
        answer, citation = build_structured_answer(query)
        expected = (
            f"The assets under management (AUM) of {scheme} are \u20b9{aum} crore."
        )
        assert answer == expected, f"Failed for {scheme}: got {answer!r}"
        assert citation == SCHEME_URLS[scheme], f"Citation missing for {scheme}"


def test_aum_mid_cap_updated():
    """Mid Cap AUM must reflect Fund Facts May 2026 value (94,744.72 Cr)."""
    answer, citation = build_structured_answer(
        "What is the AUM of HDFC Mid Cap Fund?"
    )
    assert "94,744.72" in answer, f"Expected 94,744.72, got: {answer}"
    assert "41,892" not in answer, f"Stale AUM still present: {answer}"


def test_aum_assets_under_short_phrase():
    """'assets under' short form is also recognised."""
    answer, citation = build_structured_answer(
        "What are the assets under for HDFC Small Cap Fund?"
    )
    assert (
        answer
        == "The assets under management (AUM) of HDFC Small Cap Fund are \u20b938,168.18 crore."
    )
    assert citation == SCHEME_URLS["HDFC Small Cap Fund"]


def test_aum_response_format():
    """Response must match: 'The assets under management (AUM) of <Scheme> are ₹<Value> crore.'"""
    answer, citation = build_structured_answer(
        "What is the AUM of HDFC Silver ETF Fund of Fund?"
    )
    assert (
        answer
        == "The assets under management (AUM) of HDFC Silver ETF Fund of Fund are \u20b98,542 crore."
    )
    assert citation == SCHEME_URLS["HDFC Silver ETF Fund of Fund"]


def test_aum_no_scheme_returns_none():
    """No scheme in query → build_structured_answer returns None."""
    result = build_structured_answer("What is the AUM?")
    assert result is None


# ---------------------------------------------------------------------------
# Expense ratio — stale data check
# ---------------------------------------------------------------------------


def test_expense_ratio_mid_cap_not_stale():
    """Mid Cap expense ratio must not be 0.95% (stale value)."""
    answer, citation = build_structured_answer(
        "What is the expense ratio of HDFC Mid Cap Fund?"
    )
    assert "0.95%" not in answer, f"Stale expense ratio 0.95% still present: {answer}"
    assert "0.80%" in answer, f"Expected updated expense ratio 0.80%, got: {answer}"


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


def test_scheme_data_as_of_is_set():
    """SCHEME_DATA_AS_OF must be set to indicate data freshness."""
    assert SCHEME_DATA_AS_OF, "SCHEME_DATA_AS_OF must not be empty"
    assert "2026" in SCHEME_DATA_AS_OF, "SCHEME_DATA_AS_OF should reference 2026"


# ---------------------------------------------------------------------------
# Citation completeness
# ---------------------------------------------------------------------------


def test_all_schemes_have_citation_url():
    """Every scheme in SCHEME_DATA must have a matching SCHEME_URLS entry."""
    for scheme in REQUIRED_SCHEMES:
        assert scheme in SCHEME_URLS, f"Missing SCHEME_URLS entry for {scheme}"
        assert SCHEME_URLS[scheme].startswith("https://"), (
            f"Invalid URL for {scheme}: {SCHEME_URLS[scheme]}"
        )


def test_structured_answer_always_returns_citation():
    """Every structured answer must include a non-empty citation URL."""
    queries = [
        "What is the expense ratio of HDFC Flexi Cap Fund?",
        "What is the minimum SIP for HDFC Mid Cap Fund?",
        "What is the riskometer of HDFC Defence Fund?",
        "What is the exit load of HDFC Small Cap Fund?",
        "Who is the fund manager of HDFC Silver ETF Fund of Fund?",
        "What is the AUM of HDFC Flexi Cap Fund?",
        "What is the benchmark of HDFC Mid Cap Fund?",
    ]
    for query in queries:
        result = build_structured_answer(query)
        assert result is not None, f"No structured answer for: {query}"
        answer, citation = result
        assert citation, f"Empty citation for: {query}"
        assert citation != CITATION_UNAVAILABLE, (
            f"Fallback citation for: {query}"
        )

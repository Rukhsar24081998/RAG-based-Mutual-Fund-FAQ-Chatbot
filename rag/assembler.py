import os
import re
import tempfile

# Set up temporary directory first
os.environ["TMPDIR"] = "/tmp"
tempfile.tempdir = "/tmp"

from dotenv import load_dotenv
from groq import Groq

from rag.retriever import retrieve, get_source_documents

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LAST_UPDATED = "June 2026"

# Document date for the most recent Fund Facts PDFs (May 2026)
SCHEME_DATA_AS_OF = "May 2026"

# Partial-name aliases so queries like "HDFC Silver ETF" or "defence fund" still resolve
SCHEME_ALIASES = {
    "flexi cap": "HDFC Flexi Cap Fund",
    "mid cap": "HDFC Mid Cap Fund",
    "midcap": "HDFC Mid Cap Fund",
    "small cap": "HDFC Small Cap Fund",
    "smallcap": "HDFC Small Cap Fund",
    "defence fund": "HDFC Defence Fund",
    "defense fund": "HDFC Defence Fund",
    "hdfc defence": "HDFC Defence Fund",
    "hdfc defense": "HDFC Defence Fund",
    "silver etf": "HDFC Silver ETF Fund of Fund",
    "silver fund": "HDFC Silver ETF Fund of Fund",
}

# Official scheme page URLs for citations
SCHEME_URLS = {
    "HDFC Flexi Cap Fund": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
    "HDFC Mid Cap Fund": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-mid-cap-fund/direct",
    "HDFC Small Cap Fund": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-small-cap-fund/direct",
    "HDFC Defence Fund": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-defence-fund/direct",
    "HDFC Silver ETF Fund of Fund": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-silver-etf-fund-fund/direct",
}

HDFC_PORTAL_URL = "https://www.hdfcfund.com"
CITATION_UNAVAILABLE = "Source unavailable. Please verify with official scheme documents."

# Define scheme data from custom facts for structured access
# UPDATED: June 6, 2026 - Synced with custom_facts.txt
SCHEME_DATA = {
    "HDFC Flexi Cap Fund": {
        "expense_ratio": "0.68%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "NIFTY 500 Index (Total Returns Index)",
        "riskometer": "Very High",
        "fund_manager": "Amit Ganatra (since February 01, 2026)",
        "aum": "1,01,821.82",
    },
    "HDFC Mid Cap Fund": {
        "expense_ratio": "0.73%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "NIFTY Midcap 150 Index (Total Returns Index)",
        "riskometer": "Very High",
        "fund_manager": "Chirag Setalvad (since June 25, 2007)",
        "aum": "97,350.48",
    },
    "HDFC Small Cap Fund": {
        "expense_ratio": "0.73%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "BSE 250 SmallCap Index (TRI)",
        "riskometer": "Very High",
        "fund_manager": "Chirag Setalvad (since June 28, 2014)",
        "aum": "38,809.48",
    },
    "HDFC Defence Fund": {
        "expense_ratio": "0.83%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "Nifty India Defence Index TRI (Total Returns Index)",
        "riskometer": "Very High",
        "fund_manager": "Rahul Baijal & Priya Ranjan (w.e.f. April 18, 2025)",
        "aum": "9,724.27",
    },
    "HDFC Silver ETF Fund of Fund": {
        "expense_ratio": "0.21%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 15 days from the date of allotment.",
        "benchmark": "Domestic Price of Silver (based on MCX)",
        "riskometer": "Very High",
        "fund_manager": "Nandita Menezes & Arun Agarwal",
        "aum": "4,893.86",
    },
}


def extract_scheme_name(query):
    """Extract scheme name from user query (exact match first, then aliases)."""
    query_lower = query.lower()
    # Prefer longest exact match to avoid "HDFC Mid Cap" matching inside longer names
    matched = [
        (scheme, len(scheme))
        for scheme in SCHEME_DATA.keys()
        if scheme.lower() in query_lower
    ]
    if matched:
        return max(matched, key=lambda x: x[1])[0]
    # Fall back to short-name aliases
    for alias, scheme in SCHEME_ALIASES.items():
        if alias in query_lower:
            return scheme
    return None


def get_citation_for_scheme(scheme):
    """Return the official source URL for a scheme, or fallback message."""
    return SCHEME_URLS.get(scheme, CITATION_UNAVAILABLE)


def build_structured_answer(query):
    """Try to answer using structured data first.
    
    Returns:
        tuple: (answer_text, citation_url) or None if no structured answer available.
    """
    scheme = extract_scheme_name(query)
    if not scheme:
        return None

    query_lower = query.lower()
    citation = get_citation_for_scheme(scheme)

    # Riskometer (highest priority)
    if (
        "riskometer" in query_lower
        or "risk level" in query_lower
        or "high risk" in query_lower
    ):
        return (
            f"{scheme} is classified as {SCHEME_DATA[scheme]['riskometer']} Risk on the Riskometer.",
            citation,
        )

    # Expense Ratio
    if "expense" in query_lower or "ter" in query_lower:
        return (
            f"The expense ratio of {scheme} \u2013 Direct Plan is {SCHEME_DATA[scheme]['expense_ratio']}.",
            citation,
        )

    # Minimum SIP
    if "minimum" in query_lower and "sip" in query_lower:
        return (
            f"The minimum SIP amount for {scheme} is {SCHEME_DATA[scheme]['minimum_sip']} per installment.",
            citation,
        )

    # Exit Load
    if "exit load" in query_lower or ("exit" in query_lower and "load" in query_lower):
        return (SCHEME_DATA[scheme]["exit_load"], citation)

    # Benchmark
    if "benchmark" in query_lower:
        return (
            f"The benchmark index for {scheme} is {SCHEME_DATA[scheme]['benchmark']}.",
            citation,
        )

    # Fund Manager
    if (
        "fund manager" in query_lower
        or "who manages" in query_lower
        or "who is the manager" in query_lower
        or ("manager" in query_lower and "fund" in query_lower)
    ):
        if SCHEME_DATA[scheme].get("fund_manager"):
            return (
                f"The fund manager of {scheme} is {SCHEME_DATA[scheme]['fund_manager']}.",
                citation,
            )
        else:
            return (
                f"I couldn't find the fund manager information for {scheme}.",
                citation,
            )

    # AUM
    if (
        "aum" in query_lower
        or "assets under management" in query_lower
        or "assets under" in query_lower
    ):
        if SCHEME_DATA[scheme].get("aum"):
            return (
                f"The assets under management (AUM) of {scheme} are \u20b9{SCHEME_DATA[scheme]['aum']} crore.",
                citation,
            )
        else:
            return (
                f"I couldn't find the AUM information for {scheme}.",
                citation,
            )

    return None


def build_prompt(query, chunks):
    context = "\n---\n".join([c["text"] for c in chunks])

    prompt = f"""You are a facts-only mutual fund FAQ assistant for HDFC Mutual Fund.
Answer ONLY from the context below. Answer directly without referencing documents.
Maximum 3 sentences.
Use simple, investor-friendly language.
ALWAYS mention the scheme name in your answer.

If the answer is not explicitly in the context, say "I couldn't find this information in the available scheme data and documents."

If the question asks for advice, recommendations, or return predictions,
refuse politely and link to https://www.amfiindia.com/investor-corner/knowledge-center

Context:
{context}

Question: {query}"""
    return prompt


def _get_best_citation(chunks):
    """Select the highest-confidence citation URL from retrieved chunks.
    
    Priority: Fund Facts > FOF Book > KIM > SID > Scheme Page > other.
    The retriever already sorts Custom Facts first, but for citations
    we prefer the most authoritative official document type.
    """
    TYPE_PRIORITY = {
        "Fund Facts": 1,
        "FOF Book": 2,
        "KIM": 3,
        "SID": 4,
        "Scheme Page": 5,
    }
    
    best_url = None
    best_priority = 999
    
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        url = meta.get("url", "")
        doc_type = meta.get("type", "")
        
        if not url or url.startswith("file://"):
            continue
        
        priority = TYPE_PRIORITY.get(doc_type, 99)
        if priority < best_priority:
            best_priority = priority
            best_url = url
    
    return best_url if best_url else CITATION_UNAVAILABLE


def generate_answer(query):
    query_lower = query.lower()

    # Check for investor login / account access FIRST
    if (
        "login" in query_lower
        or "log in" in query_lower
        or "account access" in query_lower
        or "investor portal" in query_lower
    ):
        answer = (
            "You can log in to your HDFC Mutual Fund account on their investor portal."
        )
        answer += "\n\n\u2022 HDFC Mutual Fund Investor Portal: `https://www.hdfcfund.com`"
        return {
            "answer": answer,
            "citation_url": HDFC_PORTAL_URL,
            "last_updated": LAST_UPDATED,
            "source_documents": [{"url": HDFC_PORTAL_URL, "type": "Investor Portal", "scheme": "", "doc_date": ""}],
        }

    # Then try structured answer
    structured_result = build_structured_answer(query)
    if structured_result:
        answer, citation_url = structured_result
        scheme = extract_scheme_name(query)
        return {
            "answer": answer,
            "citation_url": citation_url,
            "last_updated": LAST_UPDATED,
            "source_documents": [{
                "url": citation_url,
                "type": "SCHEME_DATA (hardcoded, as of " + SCHEME_DATA_AS_OF + ")",
                "scheme": scheme or "",
                "doc_date": SCHEME_DATA_AS_OF,
            }],
        }

    # Check for capital gains / account statement questions
    if (
        "capital gains" in query_lower or "account statement" in query_lower
    ) and "statement" in query_lower:
        answer = "You can download your capital gains statement from:"
        answer += "\n\n\u2022 HDFC Mutual Fund Investor Portal: `https://www.hdfcfund.com`"
        answer += "\n\u2022 AMFI CAS Service: `https://www.amfiindia.com`"
        answer += "\n\nUse the HDFC portal for scheme-specific statements and investor services. Use AMFI CAS for consolidated mutual fund statements across participating AMCs."
        return {
            "answer": answer,
            "citation_url": HDFC_PORTAL_URL,
            "last_updated": LAST_UPDATED,
            "source_documents": [{"url": HDFC_PORTAL_URL, "type": "Investor Portal", "scheme": "", "doc_date": ""}],
        }

    # Check for SID / KIM / factsheet download questions
    if "download" in query_lower and (
        "sid" in query_lower or "kim" in query_lower or "factsheet" in query_lower
    ):
        answer = (
            "You can download the scheme documents from the HDFC Mutual Fund website."
        )
        answer += "\n\n\u2022 HDFC Mutual Fund: `https://www.hdfcfund.com`"
        return {
            "answer": answer,
            "citation_url": HDFC_PORTAL_URL,
            "last_updated": LAST_UPDATED,
            "source_documents": [{"url": HDFC_PORTAL_URL, "type": "Investor Portal", "scheme": "", "doc_date": ""}],
        }

    # If structured answer not available, use LLM with recency-aware retrieval
    chunks = retrieve(query)
    if not chunks:
        return {
            "answer": "I couldn't find this information in the available scheme data and official documents.",
            "citation_url": CITATION_UNAVAILABLE,
            "last_updated": LAST_UPDATED,
            "source_documents": [],
        }

    prompt = build_prompt(query, chunks)

    client = Groq(api_key=GROQ_API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=500,
    )

    answer = chat_completion.choices[0].message.content.strip()
    citation_url = _get_best_citation(chunks)
    source_documents = get_source_documents(chunks)

    return {
        "answer": answer,
        "citation_url": citation_url,
        "last_updated": LAST_UPDATED,
        "source_documents": source_documents,
    }

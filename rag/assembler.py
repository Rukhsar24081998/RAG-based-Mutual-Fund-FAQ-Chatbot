import os
import re
import tempfile

# Set up temporary directory first
os.environ["TMPDIR"] = "/tmp"
tempfile.tempdir = "/tmp"

from dotenv import load_dotenv
from groq import Groq

from rag.retriever import retrieve

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LAST_UPDATED = "June 2026"

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

# Define scheme data from custom facts for structured access
SCHEME_DATA = {
    "HDFC Flexi Cap Fund": {
        "expense_ratio": "0.85%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "NIFTY 500 Index (Total Returns Index)",
        "riskometer": "Moderately High",
        "fund_manager": "Chirag Setalvad",
        "aum": "52,347",
    },
    "HDFC Mid Cap Fund": {
        "expense_ratio": "0.95%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "NIFTY Midcap 150 Index (Total Returns Index)",
        "riskometer": "Very High",
        "fund_manager": "Srinivas Rao Ravuri",
        "aum": "41,892",
    },
    "HDFC Small Cap Fund": {
        "expense_ratio": "1.05%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "NIFTY Smallcap 250 Index (Total Returns Index)",
        "riskometer": "Very High",
        "fund_manager": "Srinivas Rao Ravuri",
        "aum": "32,145",
    },
    "HDFC Defence Fund": {
        "expense_ratio": "1.15%",
        "minimum_sip": "₹500",
        "exit_load": "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment.",
        "benchmark": "NIFTY India Defence Index (Total Returns Index)",
        "riskometer": "Very High",
        "fund_manager": "Amit Sethiya",
        "aum": "15,678",
    },
    "HDFC Silver ETF Fund of Fund": {
        "expense_ratio": "0.25%",
        "minimum_sip": "₹100",
        "exit_load": "An exit load of 0.25% is applicable if units are redeemed within 30 days from the date of allotment.",
        "benchmark": "Domestic Price of Silver (based on MCX)",
        "riskometer": "Moderately High",
        "fund_manager": "Anil Bamboli",
        "aum": "8,542",
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


def build_structured_answer(query):
    """Try to answer using structured data first"""
    scheme = extract_scheme_name(query)
    if not scheme:
        return None

    query_lower = query.lower()

    # Riskometer (highest priority)
    if (
        "riskometer" in query_lower
        or "risk level" in query_lower
        or "high risk" in query_lower
    ):
        return f"{scheme} is classified as {SCHEME_DATA[scheme]['riskometer']} Risk on the Riskometer."

    # Expense Ratio
    if "expense" in query_lower or "ter" in query_lower:
        return f"The expense ratio of {scheme} – Direct Plan is {SCHEME_DATA[scheme]['expense_ratio']}."

    # Minimum SIP
    if "minimum" in query_lower and "sip" in query_lower:
        return f"The minimum SIP amount for {scheme} is {SCHEME_DATA[scheme]['minimum_sip']} per installment."

    # Exit Load
    if "exit load" in query_lower or ("exit" in query_lower and "load" in query_lower):
        return SCHEME_DATA[scheme]["exit_load"]

    # Benchmark
    if "benchmark" in query_lower:
        return (
            f"The benchmark index for {scheme} is {SCHEME_DATA[scheme]['benchmark']}."
        )

    # Fund Manager
    if (
        "fund manager" in query_lower
        or "who manages" in query_lower
        or "who is the manager" in query_lower
        or ("manager" in query_lower and "fund" in query_lower)
    ):
        if SCHEME_DATA[scheme].get("fund_manager"):
            return f"The fund manager of {scheme} is {SCHEME_DATA[scheme]['fund_manager']}."
        else:
            return f"I couldn't find the fund manager information for {scheme}."

    # AUM
    if (
        "aum" in query_lower
        or "assets under management" in query_lower
        or "assets under" in query_lower
    ):
        if SCHEME_DATA[scheme].get("aum"):
            return f"The assets under management (AUM) of {scheme} are \u20b9{SCHEME_DATA[scheme]['aum']} crore."
        else:
            return f"I couldn't find the AUM information for {scheme}."

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
        answer += "\n\n• HDFC Mutual Fund Investor Portal: `https://www.hdfcfund.com`"
        return {"answer": answer, "citation_url": "", "last_updated": LAST_UPDATED}

    # Then try structured answer
    structured_answer = build_structured_answer(query)
    if structured_answer:
        return {
            "answer": structured_answer,
            "citation_url": "",
            "last_updated": LAST_UPDATED,
        }

    # Check for capital gains / account statement questions
    if (
        "capital gains" in query_lower or "account statement" in query_lower
    ) and "statement" in query_lower:
        answer = "You can download your capital gains statement from:"
        answer += "\n\n• HDFC Mutual Fund Investor Portal: `https://www.hdfcfund.com`"
        answer += "\n• AMFI CAS Service: `https://www.amfiindia.com`"
        answer += "\n\nUse the HDFC portal for scheme-specific statements and investor services. Use AMFI CAS for consolidated mutual fund statements across participating AMCs."
        return {"answer": answer, "citation_url": "", "last_updated": LAST_UPDATED}

    # Check for SID / KIM / factsheet download questions
    if "download" in query_lower and (
        "sid" in query_lower or "kim" in query_lower or "factsheet" in query_lower
    ):
        answer = (
            "You can download the scheme documents from the HDFC Mutual Fund website."
        )
        answer += "\n\n• HDFC Mutual Fund: `https://www.hdfcfund.com`"
        return {"answer": answer, "citation_url": "", "last_updated": LAST_UPDATED}

    # If structured answer not available, use LLM
    chunks = retrieve(query)
    if not chunks:
        return {
            "answer": "I couldn't find this information in the available scheme data and official documents.",
            "citation_url": "",
            "last_updated": LAST_UPDATED,
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

    return {"answer": answer, "citation_url": "", "last_updated": LAST_UPDATED}

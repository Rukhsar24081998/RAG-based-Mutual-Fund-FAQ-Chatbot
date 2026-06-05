import re

ADVICE_KEYWORDS = [
    "should i", "recommend", "best fund", "which fund",
    "worth investing", "good investment", "better fund",
    "suggest", "buy", "sell", "will it grow", "returns"
]

PII_PATTERNS = [
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),  # PAN
    re.compile(r"\b[0-9]{12}\b"),              # Aadhaar
    re.compile(r"\b[0-9]{10}\b"),              # Phone
    re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"),  # Email
    re.compile(r"\b[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{4}\b")  # Card
]

AMFI_EDUCATION_URL = "https://www.amfiindia.com/investor-corner/knowledge-center"

def check_pii(text):
    for pattern in PII_PATTERNS:
        if pattern.search(text):
            return True
    return False

def check_advice(text):
    text_lower = text.lower()
    for keyword in ADVICE_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def get_advice_refusal():
    return {
        'status': 'refused',
        'answer': f"I'm a facts-only assistant and cannot provide investment advice. For educational resources, please visit: {AMFI_EDUCATION_URL}",
        'citation_url': AMFI_EDUCATION_URL,
        'last_updated': "June 2026"
    }

def get_pii_refusal():
    return {
        'status': 'refused',
        'answer': "This assistant does not accept personal information.",
        'citation_url': "",
        'last_updated': "June 2026"
    }

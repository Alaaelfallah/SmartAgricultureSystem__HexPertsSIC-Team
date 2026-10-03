"""
Shared safety rules for the HexPerts RAG pipeline.

Used in two places:
1. scripts.build_rag  -> sentences that mention hazardous substances are removed
                      before anything is stored in the knowledge base
  2. rag_chain.py  -> hazardous documents are filtered out at retrieval time,
                      and the final LLM answer is checked before it is returned

Place this file in the models/ folder (models/safety.py).

NOTE: this is a starting list of highly toxic or banned/heavily restricted
substances. Review it with an agronomist and extend it for your country.
"""

import re


HAZARDOUS_TERMS = [
    # Mercury compounds
    "mercuric",
    "mercury",
    "mercurial",
    "calomel",
    "phenylmercuric",
    "organomercury",
    "ceresan",
    "agrosan",

    # Arsenic compounds
    "arsenic",
    "arsenate",
    "arsenite",

    # Banned / heavily restricted pesticides
    "ddt",
    "aldrin",
    "dieldrin",
    "endrin",
    "chlordane",
    "heptachlor",
    "lindane",
    "bhc",
    "parathion",
    "monocrotophos",
    "endosulfan",
    "carbofuran",
    "methamidophos",
    "phorate",
    "methyl bromide",
    "paraquat",
    "2,4,5-t",

    # Other highly toxic substances
    "cadmium",
    "thallium",
    "strychnine",
    "sodium cyanide",
    "potassium cyanide",
    "zinc phosphide",
    "aluminium phosphide",
    "aluminum phosphide",

    # Arabic
    "زئبق",
    "زرنيخ",
]


_HAZARD_PATTERN = re.compile(
    r"(?<![a-z])(" + "|".join(re.escape(term) for term in HAZARDOUS_TERMS) + r")(?![a-z])",
    re.IGNORECASE,
)


def find_hazardous_substances(text):
    """Return the sorted set of hazardous terms found in the text."""

    if not text:
        return []

    return sorted({match.lower() for match in _HAZARD_PATTERN.findall(str(text))})


def contains_hazardous_substance(text):
    """True if the text mentions any hazardous substance."""

    return bool(find_hazardous_substances(text))


def remove_hazardous_sentences(text):
    """
    Remove every sentence (or line) that mentions a hazardous substance
    and keep the rest of the text.

    This keeps the safe part of an answer (for example "use disease-free
    seed and rotate crops") while dropping the unsafe recommendation.
    Returns an empty string if nothing is left.
    """

    if not text:
        return ""

    parts = re.split(r"(?<=[.!?])\s+|\n+", str(text))

    kept = [
        part.strip()
        for part in parts
        if part.strip() and not contains_hazardous_substance(part)
    ]

    return " ".join(kept)


SAFETY_NOTICE = (
    "⚠️ Safety notice: this guidance comes from a general knowledge base and "
    "is not a substitute for professional advice. Consult a qualified "
    "agronomist and check local regulations before using any pesticide or "
    "chemical treatment, and always follow the product label."
)


HAZARD_BLOCKED_MESSAGE = (
    "The retrieved guidance mentioned a chemical that is highly toxic or "
    "restricted, so it was withheld for safety. Please consult a qualified "
    "agronomist for treatment options that are approved in your area."
)

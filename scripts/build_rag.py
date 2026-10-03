from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import chromadb
import re
from pathlib import Path

from models.safety import (
    contains_hazardous_substance,
    find_hazardous_substances,
    remove_hazardous_sentences,
)


# ============================================================
# Configuration
# ============================================================

DATASET_NAME = "abdulhamed/agriculture_qa_en_ar_pairs"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_PATH = str(PROJECT_ROOT / "rag_data" / "chroma")

COLLECTION_NAME = "agriculture_rag"

BATCH_SIZE = 128

# Minimum length of an answer that is kept after unsafe sentences are removed
MIN_CLEAN_ANSWER_LENGTH = 60


# ============================================================
# Crop and disease vocabulary
# ============================================================

CROP_NAMES = [
    "apple",
    "blueberry",
    "cherry",
    "corn",
    "grape",
    "orange",
    "peach",
    "pepper",
    "potato",
    "raspberry",
    "soybean",
    "squash",
    "strawberry",
    "tomato",
]


# Other names used for the same crop in the dataset
CROP_SYNONYMS = {
    "maize": "corn",
    "soyabean": "soybean",
    "soya bean": "soybean",
}


DISEASE_NAMES = [
    "powdery mildew",
    "early blight",
    "late blight",
    "bacterial spot",
    "bacterial leaf spot",
    "black rot",
    "cedar apple rust",
    "cercospora leaf spot",
    "common rust",
    "northern leaf blight",
    "esca",
    "leaf blight",
    "citrus greening",
    "septoria leaf spot",
    "spider mites",
    "target spot",
    "tomato yellow leaf curl virus",
    "tomato mosaic virus",
    "leaf scorch",
]


# Wording used in the knowledge base for names that appear in
# several forms. Must stay consistent with CNN_DISEASE_ALIASES
# in models/rag_chain.py.
DISEASE_ALIASES = {
    "bacterial spot": "bacterial leaf spot",
}


# ============================================================
# Helper functions
# ============================================================

def normalize_text(text):
    """
    Normalize text for metadata extraction.
    """
    text = str(text).lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    return text


def crop_pattern(crop):
    """
    Regex for a crop name including simple plurals
    (tomato -> tomatoes, cherry -> cherries).
    "sweet potato" is a different crop and is excluded.
    """

    if crop.endswith("y"):
        return rf"\b{re.escape(crop[:-1])}(?:y|ies)\b"

    if crop == "potato":
        return r"(?<!sweet )\bpotato(?:e?s)?\b"

    return rf"\b{re.escape(crop)}(?:e?s)?\b"


def dominant_crop(text, min_mentions=1):
    """
    Return the crop a text is clearly about, or "".

    - one crop mentioned            -> that crop (if it is mentioned
                                       at least min_mentions times)
    - several crops mentioned       -> the most frequent one, but only
                                       if it is mentioned at least twice
                                       as often as the runner-up
    - otherwise the text is ambiguous (e.g. a list of crops), and
      no crop is returned. A wrong crop tag is worse than no tag,
      because the crop filter would retrieve advice about the wrong crop.
    """

    text = normalize_text(text)

    for synonym, crop in CROP_SYNONYMS.items():

        text = re.sub(
            rf"\b{re.escape(synonym)}(?:e?s)?\b",
            crop,
            text
        )

    counts = []

    for crop in CROP_NAMES:

        positions = [
            match.start()
            for match in re.finditer(
                crop_pattern(crop),
                text
            )
        ]

        if positions:
            counts.append(
                (len(positions), -positions[0], crop)
            )

    if not counts:
        return None

    counts.sort(reverse=True)

    # A crop mentioned only once is often incidental
    if counts[0][0] < min_mentions:
        return None

    if len(counts) == 1:
        return counts[0][2]

    if counts[0][0] >= 2 * counts[1][0]:
        return counts[0][2]

    return ""


def detect_crop(question, answer):
    """
    Detect the crop a document is about.

    The question defines the topic, so it is used first.
    The answer is only used when the question names no crop, and
    then the crop must be mentioned at least twice.

    Returns:
        crop name or empty string
    """

    crop = dominant_crop(question)

    if crop is not None:
        return crop

    # In an answer, a single passing mention is not enough
    return dominant_crop(answer, min_mentions=2) or ""


def detect_disease(question, answer):
    """
    Detect disease from question + answer.

    Returns:
        disease name or empty string
    """

    text = normalize_text(
        f"{question} {answer}"
    )

    # Check longer names first
    # to avoid partial matches.
    sorted_diseases = sorted(
        DISEASE_NAMES,
        key=len,
        reverse=True
    )

    for disease in sorted_diseases:

        # Word boundaries avoid false matches such as
        # "esca" inside "escape".
        if re.search(
            rf"\b{re.escape(disease)}\b",
            text
        ):
            return DISEASE_ALIASES.get(disease, disease)

    return ""


# ============================================================
# 1. Load dataset
# ============================================================

print("=" * 60)
print("Loading agriculture knowledge base...")
print("=" * 60)

dataset = load_dataset(
    DATASET_NAME,
    split="train"
)

print(
    f"Total records loaded: {len(dataset)}"
)


# ============================================================
# 2. Prepare documents
# ============================================================

QUESTION_COLUMN = "question"
ANSWER_COLUMN = "answers"


documents = []
metadatas = []
ids = []


seen_documents = set()

hazardous_removed = 0
hazardous_redacted = 0
hazardous_terms_found = {}


for index, row in enumerate(dataset):

    question = row[QUESTION_COLUMN]
    answer = row[ANSWER_COLUMN]

    question_text = str(question).strip()
    answer_text = str(answer).strip()

    if not question_text or not answer_text:
        continue


    # --------------------------------------------------------
    # Safety: highly toxic or banned substances (e.g. mercuric
    # chloride) must never reach the knowledge base.
    #
    # - hazardous term in the question -> the document is dropped
    # - hazardous term in the answer   -> only the unsafe sentences
    #   are removed; the safe advice around them is kept. The
    #   document is dropped if too little useful text remains.
    # --------------------------------------------------------

    hazards_in_document = find_hazardous_substances(
        f"{question_text} {answer_text}"
    )

    if hazards_in_document:

        for term in hazards_in_document:
            hazardous_terms_found[term] = (
                hazardous_terms_found.get(term, 0) + 1
            )

        if contains_hazardous_substance(question_text):

            hazardous_removed += 1
            continue

        cleaned_answer = remove_hazardous_sentences(
            answer_text
        )

        if len(cleaned_answer) < MIN_CLEAN_ANSWER_LENGTH:

            hazardous_removed += 1
            continue

        answer_text = cleaned_answer
        hazardous_redacted += 1


    document = (
        f"Question: {question_text}\n"
        f"Answer: {answer_text}"
    )


    # --------------------------------------------------------
    # Remove exact duplicate Q&A pairs
    # --------------------------------------------------------

    if document in seen_documents:
        continue

    seen_documents.add(document)


    # --------------------------------------------------------
    # Detect crop and disease
    # --------------------------------------------------------

    crop = detect_crop(
        question_text,
        answer_text
    )

    disease = detect_disease(
        question_text,
        answer_text
    )


    documents.append(document)


    metadatas.append({

        "source": DATASET_NAME,

        "record_id": str(index),

        "crop": crop,

        "disease": disease,

    })


    ids.append(
        f"agriculture_{index}"
    )


print(
    f"Valid documents prepared: "
    f"{len(documents)}"
)

print(
    f"Documents with unsafe sentences removed (kept): "
    f"{hazardous_redacted}"
)

print(
    f"Hazardous documents dropped completely: "
    f"{hazardous_removed}"
)

if hazardous_terms_found:

    print(
        f"Hazardous terms found: "
        f"{hazardous_terms_found}"
    )

print(
    f"Duplicate/empty documents removed: "
    f"{len(dataset) - len(documents) - hazardous_removed}"
)


# ============================================================
# 3. Show metadata statistics
# ============================================================

documents_with_crop = sum(
    1
    for metadata in metadatas
    if metadata["crop"]
)

documents_with_disease = sum(
    1
    for metadata in metadatas
    if metadata["disease"]
)


print()
print("=" * 60)
print("Metadata extraction")
print("=" * 60)

print(
    f"Documents with crop metadata: "
    f"{documents_with_crop}"
)

print(
    f"Documents with disease metadata: "
    f"{documents_with_disease}"
)


# ============================================================
# 4. Load embedding model
# ============================================================

print("=" * 60)
print("Loading embedding model...")
print("=" * 60)

embedder = SentenceTransformer(
    EMBEDDING_MODEL
)


# ============================================================
# 5. Create ChromaDB
# ============================================================

print("=" * 60)
print("Initializing ChromaDB...")
print("=" * 60)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# Delete old collection if it exists
try:

    chroma_client.delete_collection(
        name=COLLECTION_NAME
    )

    print("Old collection deleted.")

except Exception:

    print("No previous collection found.")


collection = chroma_client.create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# 6. Generate embeddings and store documents
# ============================================================

print("=" * 60)
print("Building vector database...")
print("=" * 60)


total_documents = len(documents)


for start in range(
    0,
    total_documents,
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        total_documents
    )


    batch_documents = documents[start:end]

    batch_metadatas = metadatas[start:end]

    batch_ids = ids[start:end]


    print(
        f"Processing documents "
        f"{start + 1}-{end} "
        f"of {total_documents}"
    )


    embeddings = embedder.encode(
        batch_documents,
        show_progress_bar=False
    ).tolist()


    collection.add(

        documents=batch_documents,

        embeddings=embeddings,

        metadatas=batch_metadatas,

        ids=batch_ids

    )


# ============================================================
# 7. Final information
# ============================================================

print()

print("=" * 60)
print("RAG KNOWLEDGE BASE CREATED SUCCESSFULLY")
print("=" * 60)

print(
    f"Collection: "
    f"{COLLECTION_NAME}"
)

print(
    f"Documents stored: "
    f"{collection.count()}"
)

print(
    f"Embedding model: "
    f"{EMBEDDING_MODEL}"
)

print(
    f"Chroma path: "
    f"{CHROMA_PATH}"
)

print("=" * 60)

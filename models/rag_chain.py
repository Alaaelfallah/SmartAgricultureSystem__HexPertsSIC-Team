import os
import re
import time

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import errors

from models.safety import (
    HAZARD_BLOCKED_MESSAGE,
    SAFETY_NOTICE,
    contains_hazardous_substance,
)


# ============================================================
# 1. Project paths
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "rag_data",
    "chroma"
)


# ============================================================
# 2. Load environment variables
# ============================================================

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# ============================================================
# 3. Gemini client
# ============================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# 4. ChromaDB
# ============================================================

COLLECTION_NAME = "agriculture_rag"

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


# ============================================================
# 5. Embedding model
# ============================================================

embedder = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# 6. CNN label -> knowledge-base vocabulary
# ============================================================

# The knowledge base (built by scripts.build_rag) tags each document
# with a lowercase crop name and a lowercase disease name such as
# "early blight" or "bacterial leaf spot".
#
# The CNN returns PlantVillage class names such as
# "Tomato___Bacterial_spot", which never match those tags directly.
# This table maps the few CNN disease names whose wording differs
# from the knowledge-base tag (after cleaning) to the tag used
# in the knowledge base.

CNN_DISEASE_ALIASES = {
    "bacterial spot": "bacterial leaf spot",
    "spider mites two-spotted spider mite": "spider mites",
    "haunglongbing": "citrus greening",
    "cercospora leaf spot gray leaf spot": "cercospora leaf spot",
}


def parse_cnn_label(label):
    """
    Convert a CNN class name into (crop, disease) values that
    match the metadata stored in ChromaDB.

    Examples:
        "Tomato___Bacterial_spot" -> ("tomato", "bacterial leaf spot")
        "Tomato___Early_blight"   -> ("tomato", "early blight")
        "Pepper,_bell___healthy"  -> ("pepper", None)
        "Corn_(maize)___Common_rust_" -> ("corn", "common rust")

    A healthy plant returns disease=None because there is no
    disease to filter on.
    """

    if not label or not isinstance(label, str):
        return None, None

    crop_raw, _, disease_raw = label.partition("___")

    # First alphabetic word: "Pepper,_bell" -> "pepper",
    # "Cherry_(including_sour)" -> "cherry"
    crop_parts = [
        part
        for part in re.split(r"[^a-z]+", crop_raw.lower())
        if part
    ]

    crop = crop_parts[0] if crop_parts else None

    # Remove parentheses, underscores and extra spaces
    disease = re.sub(r"\(.*?\)", "", disease_raw)
    disease = re.sub(r"[_\s]+", " ", disease).strip().lower()

    if not disease or disease == "healthy":
        return crop, None

    disease = CNN_DISEASE_ALIASES.get(disease, disease)

    return crop, disease


# ============================================================
# 7. Retrieve relevant agricultural context
# ============================================================

def retrieve_context(
    user_query,
    n_results=3,
    crop_type=None,
    disease=None
):
    """
    Retrieve relevant agricultural documents.

    Crop and disease metadata are used to avoid retrieving
    crop-specific information from a different crop.
    """

    if not user_query:
        return []


    # ========================================================
    # Prepare query
    # ========================================================

    query_parts = []

    if crop_type:
        query_parts.append(
            f"Crop: {crop_type}"
        )

    if disease:
        query_parts.append(
            f"Disease: {disease}"
        )

    query_parts.append(
        f"Question: {user_query}"
    )

    smart_query = "\n".join(
        query_parts
    )


    # ========================================================
    # Create embedding
    # ========================================================

    query_embedding = embedder.encode(
        [smart_query]
    ).tolist()


    # ========================================================
    # Build metadata filter
    # ========================================================

    where_filter = None


    if crop_type and disease:

        where_filter = {
            "$and": [
                {
                    "crop": crop_type.lower().strip()
                },
                {
                    "disease": disease.lower().strip()
                }
            ]
        }


    elif crop_type:

        where_filter = {
            "crop": crop_type.lower().strip()
        }


    elif disease:

        where_filter = {
            "disease": disease.lower().strip()
        }


    # ========================================================
    # Retrieve documents
    # ========================================================

    try:

        if where_filter:

            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where_filter
            )

        else:

            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )


    except Exception as e:

        print(
            "Metadata-filtered retrieval failed:"
        )

        print(e)

        # ----------------------------------------------------
        # Do NOT silently fall back to unrestricted retrieval
        # when crop/disease information is available.
        # ----------------------------------------------------

        return []


    # ========================================================
    # Extract documents
    # ========================================================

    documents = results.get(
        "documents",
        [[]]
    )[0]


    return documents


# ============================================================
# 8. Safe retrieval (removes hazardous documents)
# ============================================================

def retrieve_safe_context(
    user_query,
    n_results=3,
    crop_type=None,
    disease=None
):
    """
    Retrieve documents, drop any that mention a hazardous
    substance, and return the top n_results safe ones.

    More documents are requested than needed so that removing
    unsafe ones still leaves enough context.
    """

    documents = retrieve_context(
        user_query=user_query,
        n_results=n_results * 4,
        crop_type=crop_type,
        disease=disease
    )

    safe_documents = [
        document
        for document in documents
        if not contains_hazardous_substance(document)
    ]

    return safe_documents[:n_results]


# ============================================================
# 9. Generate grounded agricultural recommendation
# ============================================================

def generate_rag_llm_advice(
    user_query,
    cnn_result=None,
    irrigation_result=None,
    sensor_data=None,
    crop_type=None
):
    """
    Generate an agricultural recommendation using
    retrieved knowledge from the RAG database.

    The LLM does NOT replace the CNN or irrigation model.
    """


    # ========================================================
    # Retrieve context
    # ========================================================

    # Crop used for filtering: the crop selected by the user.
    # If it was not provided, use the crop detected by the CNN.
    crop_filter = None

    if crop_type:

        crop_filter = str(
            crop_type
        ).lower().strip()


    # Disease used for filtering: converted from the CNN class name
    # into the same wording used in the knowledge base.
    disease_filter = None

    if cnn_result and isinstance(
        cnn_result,
        dict
    ):

        cnn_crop, disease_filter = parse_cnn_label(
            cnn_result.get(
                "name"
            )
        )

        if not crop_filter:

            crop_filter = cnn_crop


    retrieved_documents = retrieve_safe_context(
        user_query=user_query,
        n_results=3,
        crop_type=crop_filter,
        disease=disease_filter
    )


    # ----------------------------------------------------
    # Fallback: same crop only.
    # This never retrieves information about a different crop.
    # ----------------------------------------------------

    if not retrieved_documents and disease_filter and crop_filter:

        retrieved_documents = retrieve_safe_context(
            user_query=user_query,
            n_results=3,
            crop_type=crop_filter,
            disease=None
        )


    retrieved_context = "\n\n".join(
        retrieved_documents
    )


    # ========================================================
    # Prepare system information
    # ========================================================

    # Only the information that really exists is listed. In a free
    # chat question nothing is provided, so the answer must not
    # contain a "System Information" section at all.

    system_lines = []

    if crop_type is not None:

        system_lines.append(
            f"Crop type:\n{crop_type}"
        )

    if cnn_result is not None:

        system_lines.append(
            f"CNN disease prediction:\n{cnn_result}"
        )

    if irrigation_result is not None:

        system_lines.append(
            f"Irrigation model result:\n{irrigation_result}"
        )

    if sensor_data is not None:

        system_lines.append(
            f"Sensor values:\n{sensor_data}"
        )


    if system_lines:

        system_section = "\n\n".join(
            system_lines
        )

        output_rule = (
            "Clearly separate existing model outputs from\n"
            "    knowledge-base-based recommendations."
        )

    else:

        system_section = (
            "No system outputs are available for this question."
        )

        output_rule = (
            "No model outputs or sensor values are available for\n"
            "    this question. Answer the user's question directly from the\n"
            "    retrieved context. Do NOT print a System Information section,\n"
            "    and do NOT mention the CNN, the irrigation model, sensor\n"
            "    values, or the crop type being \"not provided\"."
        )


    # ========================================================
    # Grounded RAG prompt
    # ========================================================

    prompt = f"""
You are the agricultural recommendation assistant
for the HexPerts Smart Agriculture System.

Your task is to provide a concise agricultural
recommendation using ONLY the retrieved agricultural
knowledge provided below.

IMPORTANT RULES:

1. Use the retrieved agricultural context as the ONLY source
   for agricultural recommendations and treatment information.

2. Do NOT invent agricultural facts, treatments, pesticides,
   chemicals, dosages, irrigation amounts, or disease-control
   methods that are not supported by the retrieved context.

3. The CNN prediction is an existing system output.
   Do NOT change, override, or reinterpret the CNN prediction
   or its confidence value.

4. The irrigation model result is an existing system output.
   Do NOT change, override, or recalculate the irrigation result
   or water amount.

5. You may mention the CNN and irrigation model results exactly
   as provided in the system information.

6. Only use retrieved agricultural information when it matches
   the detected crop.

7. Do not transfer a treatment or management recommendation
   from one crop to another.

8. If the retrieved context does not contain enough
   crop-specific information for the detected disease, state:

   "The available knowledge base does not contain enough
   crop-specific information to provide a specific
   recommendation."

9. The detected crop and CNN disease prediction are system
   outputs. Do not change or reinterpret them.

10. Do NOT use the CNN or irrigation result as a source for
    inventing additional agricultural facts.

11. If the retrieved context does not contain enough information
    to provide a specific agricultural recommendation, clearly
    state:

    "The available knowledge base does not contain enough
    information to provide a specific recommendation."

12. Keep the recommendation concise and practical.

13. Do not claim that you independently diagnosed the plant.

14. {output_rule}

15. If no relevant retrieved context is provided, do NOT invent
    a recommendation. Use the appropriate insufficient-
    information message instead.

------------------------------------------------------------
SYSTEM INFORMATION
------------------------------------------------------------

{system_section}

------------------------------------------------------------
RETRIEVED AGRICULTURAL CONTEXT
------------------------------------------------------------

{retrieved_context}

------------------------------------------------------------
USER QUERY
------------------------------------------------------------

{user_query}

------------------------------------------------------------
TASK
------------------------------------------------------------

Provide a concise agricultural recommendation.

Use the retrieved agricultural context as the only source
for agricultural advice and treatment information.

You may refer to the CNN prediction and irrigation model
result as existing system outputs, but do not modify,
recalculate, or reinterpret them.

If the retrieved context does not support a specific
recommendation, clearly state that the available knowledge
base does not contain enough information.
"""


    # ========================================================
    # Gemini generation with retry
    # ========================================================

    max_retries = 3

    response = None


    for attempt in range(
        max_retries
    ):

        try:

            response = (
                gemini_client
                .models
                .generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )
            )

            break


        except errors.ServerError:

            if attempt == max_retries - 1:
                raise


            wait_time = 5 * (
                attempt + 1
            )


            print(
                f"Gemini temporarily unavailable "
                f"(503). Retrying in "
                f"{wait_time} seconds..."
            )


            time.sleep(
                wait_time
            )


    # ========================================================
    # Return generated recommendation
    # ========================================================

    if response is not None:

        if response.text:

            answer = response.text.strip()

            # Safety net: never return a recommendation
            # that mentions a hazardous substance.
            if contains_hazardous_substance(answer):

                return HAZARD_BLOCKED_MESSAGE

            # Standing notice on every real recommendation
            if "does not contain enough" not in answer:

                answer = f"{answer}\n\n{SAFETY_NOTICE}"

            return answer


    return (
        "The AI model did not return a recommendation."
    )

import time
from io import BytesIO
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel

from models.cnn_model import CLASS_NAMES, predict_cnn_plant_disease
from models.irrigation_model import predict_ml_irrigation_need
from models.rag_chain import generate_rag_llm_advice, parse_cnn_label


# ============================================================
# Settings
# ============================================================

DEFAULT_QUERY = (
    "Provide a practical recommendation based on the plant "
    "disease prediction and irrigation result."
)

# Below this confidence (%) the disease prediction is flagged as uncertain
LOW_CONFIDENCE_THRESHOLD = 70.0

# Irrigation-model crop names -> crop names used by the disease model
CROP_ALIASES = {
    "chilli": "pepper",
}

# Crops the disease model can recognise (derived from its class names)
CNN_CROPS = {
    parse_cnn_label(name)[0]
    for name in CLASS_NAMES
}


# ============================================================
# Response schema
# ============================================================

class PlantAnalysis(BaseModel):
    disease: str
    confidence: float
    crop: Optional[str] = None
    is_healthy: bool
    low_confidence: bool


class IrrigationResult(BaseModel):
    prediction: int
    status: str
    confidence: float


class PredictResponse(BaseModel):
    success: bool
    plant_analysis: PlantAnalysis
    irrigation: IrrigationResult
    recommendation: str
    warnings: List[str] = []


# ============================================================
# Consistency checks
# ============================================================

def check_crop_consistency(crop_id, cnn_label):
    """
    Compare the crop selected by the user with the crop the
    disease model recognised in the image.

    Returns:
        (crop_matches, warnings)
    """

    cnn_crop, _ = parse_cnn_label(cnn_label)

    selected = crop_id.strip().lower()
    selected = CROP_ALIASES.get(selected, selected)

    if selected == cnn_crop:
        return True, []

    if selected not in CNN_CROPS:
        return False, [
            f"The disease model does not cover {crop_id}, so the "
            f"leaf diagnosis is not reliable for this crop."
        ]

    return False, [
        f"The leaf image was classified as {cnn_crop}, but the "
        f"selected crop is {crop_id}. Check the crop selection "
        f"or retake the photo."
    ]


def normalize_crop(crop_id):
    """
    Crop name used for knowledge-base retrieval.

    The knowledge base is tagged with the disease-model vocabulary
    (for example "pepper"), while the irrigation model uses "Chilli".
    """

    crop = crop_id.strip().lower()

    return CROP_ALIASES.get(crop, crop)


def irrigation_summary(irrigation_result, sensor_data):
    """
    One factual sentence built only from the irrigation model output
    and the sensor readings. It contains no agronomic advice, so it is
    safe to use when the LLM is not called.
    """

    if irrigation_result["prediction"] == 1:
        verdict = "The irrigation model indicates that irrigation is required"
    else:
        verdict = "The irrigation model indicates that irrigation is not required"

    return (
        f"{verdict} (confidence {irrigation_result['confidence']}%) "
        f"based on soil moisture {sensor_data['soil_moisture']}%, "
        f"temperature {sensor_data['temperature']}\u00b0C and "
        f"air humidity {sensor_data['humidity']}%."
    )


# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="HexPerts Smart Agriculture API",
    version="1.0.0",
    description="AI-powered smart agriculture backend",
)


# ============================================================
# Latency header (used when testing with Postman)
# ============================================================

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.0f}"
    return response


# ============================================================
# Root
# ============================================================

@app.get("/")
def root():
    return {
        "message": "HexPerts API is running"
    }


# ============================================================
# Health check
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ============================================================
# Prediction endpoint
# ============================================================

@app.post("/predict", response_model=PredictResponse)
def predict(
    image: UploadFile = File(...),

    crop_id: str = Form(...),
    soil_type: str = Form(...),
    seedling_stage: str = Form(...),

    MOI: float = Form(..., ge=0, le=100),
    temp: float = Form(..., ge=-10, le=60),
    humidity: float = Form(..., ge=0, le=100),

    user_query: str = Form(DEFAULT_QUERY),
):
    """
    This is a plain `def` (not `async def`) on purpose: the CNN, the
    Random Forest and the Gemini call are blocking, so FastAPI runs
    this function in a worker thread and the server stays responsive.

    Run the complete HexPerts AI pipeline:

    1. CNN -> plant disease prediction
    2. Random Forest -> irrigation prediction
    3. Consistency checks (crop vs. image, confidence)
    4. RAG -> grounded agricultural recommendation
    """

    user_query = user_query.strip() or DEFAULT_QUERY

    # ========================================================
    # 1. Validate image
    # ========================================================

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file must be an image."
        )

    try:
        image_bytes = image.file.read()
        plant_image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read the uploaded image: {str(e)}"
        )


    # ========================================================
    # 2. CNN prediction
    # ========================================================

    try:
        cnn_result = predict_cnn_plant_disease(
            plant_image
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"CNN prediction failed: {str(e)}"
        )


    # ========================================================
    # 3. Random Forest irrigation prediction
    # ========================================================

    try:
        irrigation_result = predict_ml_irrigation_need(
            crop_id=crop_id,
            soil_type=soil_type,
            seedling_stage=seedling_stage,
            moi=MOI,
            temp=temp,
            humidity=humidity,
        )

    except ValueError as e:
        # Unknown crop / soil type / growth stage
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Irrigation model prediction failed: {str(e)}"
        )


    # ========================================================
    # 4. Consistency checks
    # ========================================================

    cnn_crop, cnn_disease = parse_cnn_label(
        cnn_result["name"]
    )

    is_healthy = cnn_disease is None

    crop_matches, warnings = check_crop_consistency(
        crop_id,
        cnn_result["name"]
    )

    low_confidence = (
        cnn_result["confidence"] < LOW_CONFIDENCE_THRESHOLD
    )

    if low_confidence:
        warnings.append(
            f"The disease prediction confidence is low "
            f"({cnn_result['confidence']}%). Retake the photo with a "
            f"single, well-lit leaf before relying on this result."
        )


    # ========================================================
    # 5. Recommendation
    # ========================================================

    sensor_data = {
        "soil_moisture": MOI,
        "temperature": temp,
        "humidity": humidity,
    }

    irrigation_text = irrigation_summary(
        irrigation_result,
        sensor_data
    )

    if not crop_matches:

        # The image does not match the selected crop, so a
        # disease-specific recommendation would be misleading.
        # The irrigation result does not depend on the photo, so
        # it is still reported.
        recommendation = (
            "No disease-specific recommendation was generated "
            "because the photo does not appear to match the "
            "selected crop. Please check the crop selection or "
            "retake the photo.\n\n"
            f"Irrigation: {irrigation_text}"
        )

    elif is_healthy and user_query == DEFAULT_QUERY:

        recommendation = (
            "Plant health: no disease was detected in the leaf "
            "image. Continue routine monitoring.\n\n"
            f"Irrigation: {irrigation_text}"
        )

    else:

        try:
            recommendation = generate_rag_llm_advice(
                user_query=user_query,
                cnn_result=cnn_result,
                irrigation_result=irrigation_result,
                sensor_data=sensor_data,
                crop_type=normalize_crop(crop_id),
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"RAG recommendation failed: {str(e)}"
            )


    # ========================================================
    # 6. Final response
    # ========================================================

    return PredictResponse(
        success=True,
        plant_analysis=PlantAnalysis(
            disease=cnn_result["name"],
            confidence=cnn_result["confidence"],
            crop=cnn_crop,
            is_healthy=is_healthy,
            low_confidence=low_confidence,
        ),
        irrigation=IrrigationResult(
            prediction=irrigation_result["prediction"],
            status=irrigation_result["status"],
            confidence=irrigation_result["confidence"],
        ),
        recommendation=recommendation,
        warnings=warnings,
    )

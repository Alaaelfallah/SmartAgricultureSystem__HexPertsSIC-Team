from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "random_forest_model.pkl"
ENCODER_PATH = ARTIFACTS_DIR / "encoder.pkl"
SCALER_PATH = ARTIFACTS_DIR / "scaler.pkl"
FEATURE_ORDER_PATH = ARTIFACTS_DIR / "feature_order.txt"


# =========================================================
# Load trained artifacts once
# =========================================================

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)
scaler = joblib.load(SCALER_PATH)


# =========================================================
# Feature definitions
# =========================================================

CATEGORICAL_FEATURES = [
    "crop ID",
    "soil_type",
    "Seedling Stage",
]

NUMERICAL_FEATURES = [
    "MOI",
    "temp",
    "humidity",
]


# =========================================================
# Load expected feature order
# =========================================================

with open(FEATURE_ORDER_PATH, "r", encoding="utf-8") as f:
    FEATURE_ORDER = [
        line.strip()
        for line in f
        if line.strip()
    ]


# =========================================================
# Valid categorical values
# =========================================================

# The encoder was trained with handle_unknown="ignore", so an
# unknown value (for example a misspelled growth stage) would NOT
# raise an error: it would silently be encoded as all zeros and the
# model would return a meaningless prediction. Values are therefore
# validated here against the categories the encoder actually knows.

_CATEGORIES = dict(
    zip(
        CATEGORICAL_FEATURES,
        [
            [str(value) for value in values]
            for values in encoder.categories_
        ],
    )
)


def get_valid_options():
    """
    Values accepted for each categorical input.

    Returns:
        {
            "crop_id": [...],
            "soil_type": [...],
            "seedling_stage": [...],
        }
    """

    return {
        "crop_id": list(_CATEGORIES["crop ID"]),
        "soil_type": list(_CATEGORIES["soil_type"]),
        "seedling_stage": list(_CATEGORIES["Seedling Stage"]),
    }


def _match_option(value, valid_values, field_name):
    """
    Match a value to the encoder's categories, ignoring case and
    surrounding spaces. Raises ValueError if it is not a known value.
    """

    text = str(value).strip().casefold()

    for option in valid_values:
        if option.casefold() == text:
            return option

    raise ValueError(
        f"Invalid {field_name}: {value!r}. "
        f"Valid options: {', '.join(valid_values)}"
    )


# =========================================================
# Prediction function
# =========================================================

def predict_ml_irrigation_need(
    crop_id,
    soil_type,
    seedling_stage,
    moi,
    temp,
    humidity,
):
    """
    Predict irrigation requirement using the trained
    Random Forest model and the original preprocessing artifacts.

    Raises:
        ValueError: if crop_id, soil_type or seedling_stage is not
        one of the values the model was trained on.

    Returns:
        dict:
            prediction
            status
            confidence
    """

    # -----------------------------------------------------
    # Validate categorical inputs
    # -----------------------------------------------------

    crop_id = _match_option(
        crop_id,
        _CATEGORIES["crop ID"],
        "crop_id",
    )

    soil_type = _match_option(
        soil_type,
        _CATEGORIES["soil_type"],
        "soil_type",
    )

    seedling_stage = _match_option(
        seedling_stage,
        _CATEGORIES["Seedling Stage"],
        "seedling_stage",
    )

    # -----------------------------------------------------
    # Create raw input DataFrame
    # -----------------------------------------------------

    data = pd.DataFrame([{
        "crop ID": crop_id,
        "soil_type": soil_type,
        "Seedling Stage": seedling_stage,
        "MOI": moi,
        "temp": temp,
        "humidity": humidity,
    }])

    # -----------------------------------------------------
    # Encode categorical features
    # -----------------------------------------------------

    encoded = encoder.transform(
        data[CATEGORICAL_FEATURES]
    )

    if hasattr(encoded, "toarray"):
        encoded = encoded.toarray()

    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out(
            CATEGORICAL_FEATURES
        ),
    )

    # -----------------------------------------------------
    # Scale numerical features
    # -----------------------------------------------------

    scaled = scaler.transform(
        data[NUMERICAL_FEATURES]
    )

    scaled_df = pd.DataFrame(
        scaled,
        columns=NUMERICAL_FEATURES,
    )

    # -----------------------------------------------------
    # Combine encoded + scaled features
    # -----------------------------------------------------

    processed = pd.concat(
        [encoded_df, scaled_df],
        axis=1,
    )

    # -----------------------------------------------------
    # Reorder exactly as expected by the trained model
    # -----------------------------------------------------

    processed = processed.reindex(
        columns=FEATURE_ORDER,
        fill_value=0,
    )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    prediction = int(
        model.predict(processed)[0]
    )

    probabilities = model.predict_proba(processed)[0]

    confidence = float(
        probabilities[prediction] * 100
    )

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    if prediction == 1:
        status = "Irrigation Required"
    else:
        status = "Irrigation Not Required"

    # -----------------------------------------------------
    # Return clean result
    # -----------------------------------------------------

    return {
        "prediction": prediction,
        "status": status,
        "confidence": round(confidence, 2),
    }

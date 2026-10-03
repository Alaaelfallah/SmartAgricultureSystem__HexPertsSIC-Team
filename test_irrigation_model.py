import joblib
import pandas as pd
import numpy as np


# =========================
# Load trained artifacts
# =========================

MODEL_PATH = "artifacts/random_forest_model.pkl"
ENCODER_PATH = "artifacts/encoder.pkl"
SCALER_PATH = "artifacts/scaler.pkl"

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)
scaler = joblib.load(SCALER_PATH)


# =========================
# Test input
# =========================

data = pd.DataFrame([{
    "crop ID": "Tomato",
    "soil_type": "Red Soil",
    "Seedling Stage": "Vegetative Growth / Root or Tuber Development",
    "MOI": 32,
    "temp": 28,
    "humidity": 65
}])


# =========================
# Feature groups
# =========================

categorical_features = [
    "crop ID",
    "soil_type",
    "Seedling Stage"
]

numerical_features = [
    "MOI",
    "temp",
    "humidity"
]


# =========================
# Encoding
# =========================

encoded = encoder.transform(
    data[categorical_features]
)

if hasattr(encoded, "toarray"):
    encoded = encoded.toarray()


# =========================
# Scaling
# =========================

scaled = scaler.transform(
    data[numerical_features]
)


# =========================
# Combine
# =========================

X = np.hstack([
    encoded,
    scaled
])


print("\nProcessed input shape:")
print(X.shape)


# =========================
# Prediction
# =========================

prediction = model.predict(X)[0]

probabilities = model.predict_proba(X)[0]


# =========================
# Result
# =========================

if prediction == 1:
    status = "Irrigation Required"
else:
    status = "Irrigation Not Required"


print("\n==============================")
print("IRRIGATION MODEL TEST")
print("==============================")

print("Prediction:", prediction)
print("Status:", status)

print("\nClass probabilities:")
print("No irrigation:", round(probabilities[0] * 100, 2), "%")
print("Irrigation:", round(probabilities[1] * 100, 2), "%")

print("==============================\n")
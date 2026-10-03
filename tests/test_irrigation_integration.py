from models.irrigation_model import predict_ml_irrigation_need


result = predict_ml_irrigation_need(
    crop_id="Tomato",
    soil_type="Red Soil",
    seedling_stage="Vegetative Growth / Root or Tuber Development",
    moi=32,
    temp=28,
    humidity=65,
)


print("\n==============================")
print("IRRIGATION INTEGRATION TEST")
print("==============================")

print("Prediction:", result["prediction"])
print("Status:", result["status"])
print("Confidence:", result["confidence"], "%")

print("==============================\n")


# Unknown values must be rejected (the encoder alone would silently ignore them)
try:
    predict_ml_irrigation_need(
        crop_id="Tomato",
        soil_type="Red Soil",
        seedling_stage="Vegetative Growth",
        moi=32,
        temp=28,
        humidity=65,
    )
    print("FAIL: an invalid growth stage was accepted")
except ValueError as error:
    print("OK: invalid growth stage rejected ->", error)

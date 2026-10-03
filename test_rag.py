from models.rag_chain import generate_rag_llm_advice


print("=" * 60)
print("RAG + GEMINI TEST")
print("=" * 60)


query = "How can I manage this plant disease?"


cnn_result = {
    "name": "Tomato___Bacterial_spot",
    "confidence": 99.97
}


irrigation_result = {
    "prediction": 1,
    "status": "Irrigation Required",
    "confidence": 90.66
}


sensor_data = {
    "soil_moisture": 32,
    "temperature": 28,
    "humidity": 65
}


crop_type = "Tomato"


print("\nGenerating recommendation...\n")


advice = generate_rag_llm_advice(
    user_query=query,
    cnn_result=cnn_result,
    irrigation_result=irrigation_result,
    sensor_data=sensor_data,
    crop_type=crop_type
)


print("=" * 60)
print("RAG RECOMMENDATION")
print("=" * 60)

print(advice)

print("\n" + "=" * 60)
print("TEST FINISHED")
print("=" * 60)
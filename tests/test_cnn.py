from pathlib import Path

from PIL import Image

from models.cnn_model import predict_cnn_plant_disease


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / "assets" / "test_samples" / "tomato_leaf.jpg"


image = Image.open(IMAGE_PATH)


result = predict_cnn_plant_disease(image)


print("===================================")
print("CNN PREDICTION")
print("===================================")

print("Disease:", result["name"])
print("Confidence:", result["confidence"], "%")

print("===================================")
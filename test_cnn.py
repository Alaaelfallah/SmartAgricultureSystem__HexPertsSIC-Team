from PIL import Image

from models.cnn_model import predict_cnn_plant_disease


IMAGE_PATH = "assets/test_samples/tomato_leaf.jpg"


image = Image.open(IMAGE_PATH)


result = predict_cnn_plant_disease(image)


print("===================================")
print("CNN PREDICTION")
print("===================================")

print("Disease:", result["name"])
print("Confidence:", result["confidence"], "%")

print("===================================")
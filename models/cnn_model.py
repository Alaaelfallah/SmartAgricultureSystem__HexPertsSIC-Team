import os
import torch
import timm

from PIL import Image
from torchvision import transforms


# ============================================================
# 1. Configuration
# ============================================================

MODEL_NAME = "mobilenetv3_large_100"

# Project root = parent of the models folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "artifacts",
    "checkpoint_mobilenetv3_large_100.pth"
)

IMAGE_SIZE = 224

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# 2. Class names
# ============================================================

CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]


# ============================================================
# 3. Image preprocessing
# ============================================================

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ============================================================
# 4. Load trained model
# ============================================================

def load_model():
    """
    Load the trained MobileNetV3-Large model
    and its checkpoint.
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model checkpoint not found: {MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )

    model = timm.create_model(
        MODEL_NAME,
        pretrained=False,
        num_classes=len(CLASS_NAMES)
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(DEVICE)
    model.eval()

    return model


# Load model once when this module is imported
model = load_model()


# ============================================================
# 5. CNN prediction
# ============================================================

def predict_cnn_plant_disease(image):
    """
    Predict plant disease from a PIL image.

    Returns:
        {
            "name": disease_class,
            "confidence": confidence_percentage
        }
    """

    if not isinstance(image, Image.Image):
        raise TypeError(
            "image must be a PIL.Image.Image object"
        )

    # Make sure image is RGB
    image = image.convert("RGB")

    # Preprocess image
    image_tensor = transform(image)

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    # Move to CPU/GPU
    image_tensor = image_tensor.to(DEVICE)

    # Inference
    with torch.no_grad():

        outputs = model(image_tensor)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, predicted_class = torch.max(
            probabilities,
            dim=1
        )

    class_index = predicted_class.item()

    predicted_name = CLASS_NAMES[class_index]

    confidence_percentage = confidence.item() * 100

    return {
        "name": predicted_name,
        "confidence": round(
            confidence_percentage,
            2
        )
    }
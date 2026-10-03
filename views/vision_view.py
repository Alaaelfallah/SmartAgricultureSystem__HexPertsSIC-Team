import re

from PIL import Image
import streamlit as st

from models.cnn_model import predict_cnn_plant_disease

LOW_CONFIDENCE_THRESHOLD = 70.0


def format_label(label: str) -> tuple[str, str]:
    """
    'Tomato___Bacterial_spot' -> ('Tomato', 'Bacterial spot')
    'Pepper,_bell___healthy'  -> ('Pepper, bell', 'Healthy')
    """
    crop, _, disease = label.partition("___")
    crop = re.sub(r"\(.*?\)", "", crop).replace(",_", ", ").replace("_", " ").strip()
    disease = disease.replace("_", " ").strip()
    return crop, disease.capitalize() if disease.lower() == "healthy" else disease


def render_vision_tab() -> None:
    st.markdown('<h2 class="module-title">Plant Disease Diagnosis</h2>', unsafe_allow_html=True)
    st.divider()

    uploaded_image = None
    input_column, result_column = st.columns(2, gap="medium")
    with input_column:
        with st.container(border=True):
            st.markdown('<h3 class="card-title">Leaf Image Input</h3>', unsafe_allow_html=True)
            input_mode = st.radio(
                "Choose Input Method",
                ["Upload File", "Take Camera Photo"],
                horizontal=True,
            )
            if input_mode == "Upload File":
                image_file = st.file_uploader(
                    "Choose a leaf image", type=["jpg", "png", "jpeg"]
                )
            else:
                image_file = st.camera_input("Take photo")

            if image_file:
                uploaded_image = Image.open(image_file)
                st.image(uploaded_image, caption="Selected Leaf", width="stretch")

    with result_column:
        with st.container(border=True):
            st.markdown('<h3 class="card-title">Diagnostic Result</h3>', unsafe_allow_html=True)
            if uploaded_image and st.button("Run Disease Analysis", key="btn_vision"):
                try:
                    with st.spinner("Analyzing image features..."):
                        result = predict_cnn_plant_disease(uploaded_image)
                except Exception as error:
                    st.error(f"Could not analyze the image: {error}")
                else:
                    crop, disease = format_label(result["name"])
                    confidence = result["confidence"]

                    st.success("Analysis Complete!")
                    st.markdown(f"**Crop:** {crop}")
                    st.markdown(f"**Detected Condition:** {disease}")
                    st.markdown(f"Confidence: {confidence}%")

                    if confidence < LOW_CONFIDENCE_THRESHOLD:
                        st.warning(
                            "Low confidence. Retake the photo with a single, well-lit leaf "
                            "on a plain background before relying on this result."
                        )
            else:
                st.info("Upload an image and click Run Disease Analysis to see the result.")

    st.divider()
    st.caption(
        "Upload a clear photo of a single leaf. The model was trained on PlantVillage-style images, "
        "so photos with cluttered backgrounds may be classified less reliably."
    )

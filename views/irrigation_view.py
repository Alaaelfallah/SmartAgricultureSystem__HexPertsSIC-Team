import streamlit as st

from models.irrigation_model import (
    get_valid_options,
    predict_ml_irrigation_need,
)


def render_irrigation_tab() -> None:
    st.markdown('<h2 class="module-title">Environmental Smart Irrigation</h2>', unsafe_allow_html=True)
    st.divider()

    # Options come from the trained encoder, so the form can never
    # send a value the model does not know.
    options = get_valid_options()
    crops = options["crop_id"]
    default_crop = crops.index("Tomato") if "Tomato" in crops else 0

    input_column, result_column = st.columns(2, gap="medium")
    with input_column:
        with st.container(border=True):
            st.markdown('<h3 class="card-title">Field Sensors Data</h3>', unsafe_allow_html=True)
            crop = st.selectbox("Crop Type", crops, index=default_crop)
            soil_type = st.selectbox("Soil Type", options["soil_type"])
            growth_stage = st.selectbox("Growth Stage", options["seedling_stage"])
            moisture = st.slider("Soil Moisture (%)", 0.0, 100.0, 32.0, 0.5)
            temperature = st.slider("Temperature (C)", -5.0, 50.0, 28.0, 0.5)
            humidity = st.slider("Air Humidity (%)", 0.0, 100.0, 50.0, 0.5)

    with result_column:
        with st.container(border=True):
            st.markdown('<h3 class="card-title">ML Irrigation Recommendation</h3>', unsafe_allow_html=True)
            if st.button("Check Irrigation Need", key="btn_irrig"):
                try:
                    with st.spinner("Calculating irrigation requirements..."):
                        result = predict_ml_irrigation_need(
                            crop_id=crop,
                            soil_type=soil_type,
                            seedling_stage=growth_stage,
                            moi=moisture,
                            temp=temperature,
                            humidity=humidity,
                        )
                except Exception as error:
                    st.error(f"Could not calculate the irrigation need: {error}")
                else:
                    if result["prediction"] == 1:
                        st.warning(f"**{result['status']}**")
                    else:
                        st.success(f"**{result['status']}**")
                    st.markdown(f"Model confidence: {result['confidence']}%")
            else:
                st.info("Set the field readings and check the irrigation need.")

    st.divider()
    st.caption(
        "The model uses crop, soil type, growth stage, soil moisture, temperature, and humidity "
        "to predict whether irrigation is needed. It does not calculate a water volume."
    )

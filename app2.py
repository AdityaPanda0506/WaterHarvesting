import streamlit as st
import asyncio
from rainwater__pipeline import run_rainwater_pipeline

st.title("🌧️ Rooftop Rainwater Harvesting Recommendation System 🌧️")

# ------------------ User Inputs ------------------
roof_area = st.number_input("Roof Area (m²):", min_value=1.0, value=60.0)
rainfall_mm = st.number_input("Annual Rainfall (mm):", min_value=0.0, value=900.0)
soil_type = st.selectbox("Soil Type:", ["clay", "sandy", "loam", "rocky"])
budget = st.number_input("Budget (in local currency):", min_value=0.0, value=150000.0)

# ------------------ Run Pipeline ------------------
if st.button("Run Recommendation"):
    with st.spinner("Generating recommendation..."):
        final_report = asyncio.run(
            run_rainwater_pipeline(roof_area, rainfall_mm, soil_type, budget)
        )

    st.header("🌊 Rainwater Harvesting Feasibility Report 🌊")
    st.subheader("🏠 Input Details")
    st.markdown(f"- **Roof Area:** {final_report.input_data.roof_area} m²")
    st.markdown(f"- **Annual Rainfall:** {final_report.input_data.rainfall_mm} mm")
    st.markdown(f"- **Soil Type:** {final_report.input_data.soil_type}")
    st.markdown(f"- **Budget:** {final_report.input_data.budget}")

    st.subheader("📊 Calculations")
    st.markdown(f"- **Recommended Tank Volume:** {final_report.calculation_result.tank_volume} liters")
    st.markdown(f"- **Estimated Cost:** {final_report.calculation_result.cost_estimate}")
    st.markdown(f"- **Expected Overflow / Recharge:** {final_report.calculation_result.overflow} liters")

    st.subheader("🛠️ Design Recommendations")
    st.markdown(f"- **Tank Type:** {final_report.design_recommendation.tank_type}")
    st.markdown(f"- **Material:** {final_report.design_recommendation.material}")
    dims = final_report.design_recommendation.dimensions
    st.markdown(f"- **Dimensions (L x W x H):** {dims['length']} x {dims['width']} x {dims['height']} m")

    st.subheader("💡 Detailed Recommendations")
    st.markdown(final_report.recommendation_report.text)

    # ------------------ Download Full Report ------------------
    st.download_button(
        label="📄 Download Full Report as JSON",
        data=final_report.json(indent=4),
        file_name="rainwater_report.json",
        mime="application/json"
    )


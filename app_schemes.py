# app_schemes.py
import streamlit as st
from govt_schemes_pipeline import get_govt_schemes

st.title("🏛️ Government Schemes for Rainwater Harvesting")

# ------------------ User Input ------------------
state = st.text_input("Enter your State:", placeholder="e.g., Tamil Nadu, Maharashtra, Karnataka")

# ------------------ Run Query ------------------
if st.button("Find Schemes"):
    if state.strip() == "":
        st.warning("⚠️ Please enter a state name.")
    else:
        with st.spinner("Fetching government schemes..."):
            schemes = get_govt_schemes(state)

        st.subheader(f"📜 Schemes Available in {state}")
        st.markdown(schemes)

        # Download option
        st.download_button(
            label="📄 Download Schemes Report",
            data=schemes,
            file_name=f"{state}_rainwater_schemes.txt",
            mime="text/plain"
        )

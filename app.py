import streamlit as st
import pandas as pd
from pricing_engine import run_pricing

st.set_page_config(page_title="Bond Pricing Engine", layout="wide")

st.title("📊 Bond Pricing & Liquidity Engine")

# =====================
# SIDEBAR - INPUTS
# =====================
st.sidebar.header("Inputs")

uploaded_file = st.sidebar.file_uploader(
    "Upload Bond Cashflow Excel",
    type=["xlsx"]
)

liquidity_days = st.sidebar.slider(
    "Liquidity Threshold (days)",
    min_value=0,
    max_value=180,
    value=30,
    step=5
)

liquidity_spread = st.sidebar.number_input(
    "Liquidity Spread",
    min_value=0.0,
    max_value=0.10,
    value=0.01,
    step=0.001,
    format="%.3f"
)

run_button = st.sidebar.button("🚀 Run Pricing")

# =====================
# MAIN LOGIC
# =====================
if run_button:
    if uploaded_file is None:
        st.error("❌ Please upload an Excel file.")
    else:
        try:
            cashflow_df = pd.read_excel(uploaded_file)

            result = run_pricing(
                cashflow_df=cashflow_df,
                liquidity_days=liquidity_days,
                liquidity_spread=liquidity_spread,
            )

            st.success("✅ Pricing completed successfully")

            # =====================
            # RESULTS TABLE
            # =====================
            st.subheader("Bond Pricing Results")
            st.dataframe(
                result["bond_table"],
                use_container_width=True
            )

            # =====================
            # YIELD CURVE
            # =====================
            st.subheader("Fitted Yield Curve")
            curve_df = pd.DataFrame({
                "Maturity (Years)": result["yield_curve_x"],
                "Yield": result["yield_curve_y"],
            })

            st.line_chart(
                curve_df,
                x="Maturity (Years)",
                y="Yield",
                use_container_width=True
            )

            # =====================
            # PARAMETERS
            # =====================
            st.subheader("Optimized NSS Parameters")
            st.write(result["params"])

        except Exception as e:
            st.error("❌ An error occurred during pricing")
            st.exception(e)

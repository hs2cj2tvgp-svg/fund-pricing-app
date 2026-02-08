# app.py dosya aktarma
import streamlit as st
import pandas as pd
from pricing_engine import run_pricing

st.title("Fon Fiyatlama Uygulaması")
# Excel dosyası seçme
uploaded_file = st.file_uploader(
    "Cash Flow Excel dosyasını seç",
    type=["xlsx"]
)

if uploaded_file:
    cashflow_df = pd.read_excel(uploaded_file)
    st.write("Yüklenen veri:")
    st.dataframe(cashflow_df)
    # Likidite butonu
    liquidity_level = st.slider(
        "Likidite Derecesi",
        1, 5, 3
    )
    # ÇALIŞTIR butonu
if st.button("Çalıştır"):
    try:
        prices, curve = run_pricing(
            cashflow_df,
            liquidity_level
        )

        st.success("Hesaplama tamamlandı")
        st.dataframe(prices)

    except Exception as e:
        st.error("Hata oluştu")
        st.exception(e)


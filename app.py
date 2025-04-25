import streamlit as st

st.set_page_config(page_title="Crypto Strategy Engine", layout="wide")

st.title("🚀 Crypto Strategy Engine")
st.markdown("Benvenuto! Scegli una sezione per iniziare:")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧮 Data Management")
    st.markdown("Gestisci e aggiorna i dati storici delle crypto.")
    if st.button("📊 Vai a Data Management"):
        st.switch_page("pages/1_Data_Management.py")

with col2:
    st.subheader("📈 Strategie")
    st.markdown("Sperimenta strategie di trading basate su dati reali.")
    if st.button("🚀 Vai a Strategie"):
        st.switch_page("pages/2_Strategie.py")

st.divider()
st.markdown("🧠 Powered by CoinGecko API · PostgreSQL · Streamlit · Python")

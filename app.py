import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# Home page
st.title("🏠 Home")
st.markdown("Benvenuto! Scegli una sezione per iniziare:")

st.divider()

col1, col2, col3 = st.columns(3)

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

with col3:
    st.subheader("🔧 Data Console")
    st.markdown("Configura e monitora le fonti dati esterne.")
    if st.button("🖥️ Vai a Data Console"):
        st.switch_page("pages/3_Data_Console.py")

st.divider()
st.markdown("🧠 Powered by CoinGecko API · PostgreSQL · Streamlit · Python")

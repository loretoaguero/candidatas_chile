import streamlit as st

st.title("Candidatas Mujeres en Elecciones 2025 - Chile")
st.write(f"Total candidatas: {len(votacion_por_comuna)}")

region = st.selectbox("Selecciona una región", votacion_por_comuna["Comuna"].unique())
filtradas = votacion_por_comuna[votacion_por_comuna['Comuna']=='ALGARROBO']

st.dataframe(filtradas[["Comuna", "Primer apellido"]])
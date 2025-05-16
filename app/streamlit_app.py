# streamlit_app.py

import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Candidatas Mujeres - Elecciones Chile 2025")

# 🗳️ Título
st.title("📊 Candidatas Mujeres en las Elecciones de Chile 2025")

# 📂 Cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("../data/2024_10_Alcaldes_Datos_Eleccion.xlsx", sheet_name='votacion_por_comuna')
        return df
    except FileNotFoundError:
        st.error("No se encontró el archivo Excel. Asegúrate de colocarlo en la carpeta /data/")
        return pd.DataFrame()

df = load_data()
#st.write("Columnas disponibles:", df.columns.tolist())

if not df.empty:
    # 🧼 Normalizar nombres de columnas
    df.columns = df.columns.str.lower().str.strip()

    # 🧭 Filtros dinámicos
    comunas = df["comuna"].dropna().unique()
    cargos = df["cargo"].dropna().unique()

    comuna = st.selectbox("Filtrar por comuna:", sorted(comunas))
    cargo = st.selectbox("Filtrar por cargo:", sorted(cargos))

    filtradas = df[(df["comuna"] == comuna) & (df["cargo"] == cargo)]

    st.markdown(f"### 👩‍💼 Candidatas en {comuna} para el cargo de {cargo}")
    st.write(f"Total: {len(filtradas)} candidatas")

    st.dataframe(filtradas[["nombres", "partido", "comuna"]].sort_values("nombres"))

    # 📥 Función para generar Excel en memoria
    def to_excel_bytes(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    excel_bytes = to_excel_bytes(filtradas)

    st.download_button(
        label="📥 Descargar como Excel",
        data=excel_bytes,
        file_name=f"candidatas_{comuna}_{cargo}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No hay datos para mostrar todavía.")
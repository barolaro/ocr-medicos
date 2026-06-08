import streamlit as st

st.set_page_config(
    page_title="OCR Médicos",
    page_icon="📄",
    layout="wide"
)

st.title("📄 OCR Médicos")

st.write("Aplicación creada por Bayron Retamal")

archivo = st.file_uploader(
    "Seleccione un PDF",
    type=["pdf"]
)

if archivo:
    st.success("PDF cargado correctamente")
    st.write("Nombre:", archivo.name)
    st.write("Tamaño:", archivo.size, "bytes")

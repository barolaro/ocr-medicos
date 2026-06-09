import streamlit as st
import pandas as pd
import re
import io

from PyPDF2 import PdfReader

st.set_page_config(
    page_title="OCR Médicos",
    page_icon="📄",
    layout="wide"
)

st.title("📄 OCR Médicos")
st.write("Convierte PDF a TXT y Excel.")

archivo = st.file_uploader(
    "Sube un archivo PDF",
    type=["pdf"]
)

def limpiar_texto(texto):
    if texto is None:
        return ""
    texto = str(texto)
    texto = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", texto)
    texto = texto.replace("\f", "")
    return texto.strip()

if archivo is not None:
    st.success("PDF cargado correctamente")
    st.write("Nombre:", archivo.name)

    if st.button("Convertir a TXT y Excel"):
        reader = PdfReader(archivo)
        total_paginas = len(reader.pages)

        st.info(f"Total de páginas detectadas: {total_paginas}")

        datos_excel = []
        texto_total = ""

        barra = st.progress(0)

        for i, pagina in enumerate(reader.pages, start=1):
            texto = pagina.extract_text()
            texto = limpiar_texto(texto)

            texto_total += f"\n\n===== PÁGINA {i} =====\n\n{texto}"

            datos_excel.append({
                "Pagina": i,
                "Texto extraido": texto
            })

            barra.progress(i / total_paginas)

        df = pd.DataFrame(datos_excel)

        txt_bytes = texto_total.encode("utf-8")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.success("Conversión finalizada")

        st.download_button(
            label="Descargar TXT",
            data=txt_bytes,
            file_name="resultado_ocr.txt",
            mime="text/plain"
        )

        st.download_button(
            label="Descargar Excel",
            data=excel_buffer,
            file_name="resultado_ocr.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

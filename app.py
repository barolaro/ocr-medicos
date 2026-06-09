import streamlit as st
import pandas as pd
import pytesseract
import fitz
import re
import io

from PIL import Image

st.set_page_config(page_title="OCR Médicos", page_icon="📄", layout="wide")

st.title("📄 OCR Médicos")
st.write("Convierte PDF escaneado a TXT y Excel mediante OCR.")

archivo = st.file_uploader("Sube un archivo PDF", type=["pdf"])

def limpiar_texto(texto):
    texto = str(texto)
    texto = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", texto)
    return texto.replace("\f", "").strip()

if archivo is not None:
    st.success("PDF cargado correctamente")
    st.write("Nombre:", archivo.name)

    if st.button("Procesar OCR"):
        pdf_bytes = archivo.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        datos_excel = []
        texto_total = ""

        barra = st.progress(0)

        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            texto = pytesseract.image_to_string(
                img,
                lang="spa",
                config="--oem 3 --psm 6"
            )

            texto = limpiar_texto(texto)

            texto_total += f"\n\n===== PÁGINA {i} =====\n\n{texto}"

            datos_excel.append({
                "Pagina": i,
                "Texto extraido": texto
            })

            barra.progress(i / len(doc))

        df = pd.DataFrame(datos_excel)

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.success("OCR finalizado")

        st.download_button(
            "Descargar TXT",
            data=texto_total.encode("utf-8"),
            file_name="resultado_ocr.txt",
            mime="text/plain"
        )

        st.download_button(
            "Descargar Excel",
            data=excel_buffer,
            file_name="resultado_ocr.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

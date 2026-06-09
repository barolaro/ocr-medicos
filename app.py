import streamlit as st
import pandas as pd
import pytesseract
import fitz
import re
import io
import cv2
import numpy as np

from PIL import Image, ImageEnhance

st.set_page_config(page_title="OCR Médicos", page_icon="📄", layout="wide")

st.title("📄 OCR Médicos Mejorado")
st.write("OCR optimizado para PDFs escaneados con tablas y marcaciones.")

archivo = st.file_uploader("Sube un archivo PDF", type=["pdf"])

def limpiar_texto(texto):
    texto = str(texto)
    texto = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", texto)
    texto = texto.replace("\f", "")
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def mejorar_imagen(pil_img):
    # Convertir PIL a OpenCV
    img = np.array(pil_img)

    # Escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Aumentar contraste
    gray = cv2.equalizeHist(gray)

    # Reducir ruido
    gray = cv2.fastNlMeansDenoising(gray, h=30)

    # Binarización adaptativa
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15
    )

    # Agrandar imagen
    thresh = cv2.resize(
        thresh,
        None,
        fx=1.5,
        fy=1.5,
        interpolation=cv2.INTER_CUBIC
    )

    return Image.fromarray(thresh)

if archivo is not None:
    st.success("PDF cargado correctamente")
    st.write("Nombre:", archivo.name)

    col1, col2 = st.columns(2)

    with col1:
        dpi = st.selectbox(
            "Calidad OCR",
            [2, 2.5, 3],
            index=1,
            help="Más alto = mejor OCR, pero más lento"
        )

    with col2:
        modo_ocr = st.selectbox(
            "Modo OCR",
            [
                "--oem 3 --psm 6",
                "--oem 3 --psm 11",
                "--oem 3 --psm 4"
            ],
            index=0
        )

    if st.button("Procesar OCR Mejorado"):
        pdf_bytes = archivo.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        datos_excel = []
        texto_total = ""

        barra = st.progress(0)

        for i, page in enumerate(doc, start=1):
            st.write(f"Procesando página {i} de {len(doc)}")

            pix = page.get_pixmap(
                matrix=fitz.Matrix(dpi, dpi),
                alpha=False
            )

            img = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            img_mejorada = mejorar_imagen(img)

            texto = pytesseract.image_to_string(
                img_mejorada,
                lang="spa",
                config=modo_ocr
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
            file_name="resultado_ocr_mejorado.txt",
            mime="text/plain"
        )

        st.download_button(
            "Descargar Excel",
            data=excel_buffer,
            file_name="resultado_ocr_mejorado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

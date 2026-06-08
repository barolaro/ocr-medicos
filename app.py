# ==========================================================
# OCR PDF GRANDE A TXT Y EXCEL - GOOGLE COLAB
# Procesa página por página para no usar toda la RAM
# ==========================================================

!apt-get update -qq
!apt-get install -y tesseract-ocr tesseract-ocr-spa poppler-utils
!pip install -q pytesseract pdf2image pandas openpyxl PyPDF2 pillow

import os
import re
import gc
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from google.colab import files
from PyPDF2 import PdfReader

# ==========================================================
# SUBIR PDF
# ==========================================================

print("Sube el archivo PDF")
uploaded = files.upload()

pdf_file = list(uploaded.keys())[0]
print("Archivo cargado:", pdf_file)

# ==========================================================
# CONTAR PÁGINAS AUTOMÁTICAMENTE
# ==========================================================

reader = PdfReader(pdf_file)
total_paginas = len(reader.pages)

print(f"Total de páginas detectadas: {total_paginas}")

# ==========================================================
# FUNCIÓN PARA LIMPIAR TEXTO PARA EXCEL
# ==========================================================

def limpiar_texto(texto):
    if texto is None:
        return ""
    texto = str(texto)
    texto = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", texto)
    texto = texto.replace("\f", "")
    return texto.strip()

# ==========================================================
# OCR PÁGINA POR PÁGINA
# ==========================================================

txt_file = "resultado_ocr.txt"
excel_file = "resultado_ocr.xlsx"

datos_excel = []

with open(txt_file, "w", encoding="utf-8") as archivo_txt:

    for pagina in range(1, total_paginas + 1):

        print(f"Procesando página {pagina}/{total_paginas}")

        try:
            imagen = convert_from_path(
                pdf_file,
                dpi=150,
                first_page=pagina,
                last_page=pagina
            )[0]

            texto = pytesseract.image_to_string(
                imagen,
                lang="spa",
                config="--oem 3 --psm 6"
            )

            texto = limpiar_texto(texto)

            archivo_txt.write(f"\n\n===== PÁGINA {pagina} =====\n\n")
            archivo_txt.write(texto)

            datos_excel.append({
                "Pagina": pagina,
                "Texto extraido": texto
            })

            del imagen
            gc.collect()

        except Exception as e:
            print(f"Error en página {pagina}: {e}")

            datos_excel.append({
                "Pagina": pagina,
                "Texto extraido": f"ERROR OCR: {e}"
            })

# ==========================================================
# CREAR EXCEL
# ==========================================================

df = pd.DataFrame(datos_excel)

df.to_excel(
    excel_file,
    index=False,
    engine="openpyxl"
)

print("TXT generado:", txt_file)
print("Excel generado:", excel_file)

# ==========================================================
# DESCARGAR ARCHIVOS
# ==========================================================

files.download(txt_file)
files.download(excel_file)

print("Proceso finalizado correctamente")

# Descargar los datos del Censo 2018 del DANE

# Importar librerías

import pandas as pd
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
from io import BytesIO
import shutil
import hashlib
import json

ruta = Path(__file__).resolve().parent
datos = ruta / "datos"
datos.mkdir(exist_ok=True)
enlace = "https://microdatos.dane.gov.co/index.php/catalog/643/download/12144"
zip_dane = datos / "08_Atlantico.zip"
personas_csv = datos / "CNPV2018_5PER_A2_08.CSV"

# Descargar el ZIP de Atlántico si no existe

if not zip_dane.exists():
    print("Descargando 08_Atlantico.zip...", flush=True)
    urlretrieve(enlace, zip_dane)

# Extraer el archivo de personas

with ZipFile(zip_dane) as archivo:
    contenido = archivo.read("08Atlantico/08_Atlantico_CSV.zip")

with ZipFile(BytesIO(contenido)) as archivo:
    with archivo.open("CNPV2018_5PER_A2_08.CSV") as entrada:
        with open(personas_csv, "wb") as salida:
            shutil.copyfileobj(entrada, salida)

# Leer por partes para usar menos memoria

# Barranquilla: U_DPTO = 08 y U_MPIO = 001
primera_parte = True
total = 0
total_atlantico = 0
for parte in pd.read_csv(personas_csv, dtype=str, chunksize=100000):
    total_atlantico += len(parte)
    barranquilla = parte[(parte["U_DPTO"] == "08") & (parte["U_MPIO"] == "001")]
    if barranquilla.empty:
        continue
    if primera_parte:
        barranquilla.to_csv(
            datos / "poblacion_original.csv",
            index=False,
            encoding="utf-8"
        )
        primera_parte = False
    else:
        barranquilla.to_csv(
            datos / "poblacion_original.csv",
            index=False,
            encoding="utf-8",
            mode="a",
            header=False
        )
    total += len(barranquilla)

# Revisar la cantidad de filas y guardar la fuente

if total <= 10000:
    raise ValueError("Barranquilla no supera los 10.000 registros. Revisar la fuente.")

with open(zip_dane, "rb") as archivo:
    huella = hashlib.file_digest(archivo, "sha256").hexdigest()

fuente = {
    "nombre": "DANE — Censo Nacional de Población y Vivienda 2018",
    "pagina": "https://microdatos.dane.gov.co/catalog/643/get_microdata",
    "descarga": enlace,
    "archivo": "08_Atlantico.zip",
    "personas": personas_csv.name,
    "sha256_zip": huella,
    "registros_atlantico": total_atlantico,
    "registros_barranquilla": total,
    "columnas_originales": parte.columns.tolist(),
    "filtro": "U_DPTO = 08 y U_MPIO = 001; código completo 08001.",
    "anio": 2018,
    "asistencia": (
        "https://microdatos.dane.gov.co/index.php/catalog/643/"
        "variable/F11/V587?name=PA_ASISTENCIA"
    ),
    "edad": (
        "https://microdatos.dane.gov.co/index.php/catalog/643/"
        "variable/F11/V576?name=P_EDADR"
    ),
    "sexo": (
        "https://microdatos.dane.gov.co/index.php/catalog/643/"
        "variable/F11/V575?name=P_SEXO"
    ),
    "parentesco": (
        "https://microdatos.dane.gov.co/index.php/catalog/643/"
        "variable/F11/V577?name=P_PARENTESCOR"
    )
}
with open(datos / "fuente.json", "w", encoding="utf-8") as salida:
    json.dump(fuente, salida, ensure_ascii=False, indent=2)

# Borrar el CSV temporal de Atlántico; queda una copia en el ZIP
personas_csv.unlink()
print("Personas de Atlántico:", total_atlantico)
print("Personas originales de Barranquilla:", total)
print("Se conservaron todas las columnas originales de PERSONAS.")

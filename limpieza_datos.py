# Limpiar los datos de Barranquilla

# Importar librerías

import pandas as pd
from pathlib import Path
import json

ruta = Path(__file__).resolve().parent
datos = ruta / "datos"

# Leer las columnas necesarias

# Dos personas pueden tener la misma edad, sexo y parentesco
columnas = [
    "U_DPTO",
    "U_MPIO",
    "UA_CLASE",
    "COD_ENCUESTAS",
    "U_VIVIENDA",
    "P_NROHOG",
    "P_NRO_PER",
    "P_EDADR",
    "P_SEXO",
    "P_PARENTESCOR",
    "PA_ASISTENCIA"
]
df = pd.read_csv(datos / "poblacion_original.csv", usecols=columnas, dtype=str)
originales = len(df)
print(df.head())
df.info()
nulos = df.isnull().sum()
print("Valores nulos en las columnas seleccionadas:\n", nulos)

# Revisar duplicados usando también los códigos de cada persona

duplicados = int(df.duplicated().sum())
print("Duplicados exactos:", duplicados)
df = df.drop_duplicates().copy()
clave = [
    "U_DPTO",
    "U_MPIO",
    "UA_CLASE",
    "COD_ENCUESTAS",
    "U_VIVIENDA",
    "P_NROHOG",
    "P_NRO_PER"
]
if df.duplicated(clave).any():
    raise ValueError(
        "Hay registros contradictorios para una persona. Revisar antes de seguir."
    )

if not ((df["U_DPTO"] == "08") & (df["U_MPIO"] == "001")).all():
    raise ValueError("El CSV contiene personas fuera de Barranquilla.")

# Convertir las variables a números

codigos = {
    "P_EDADR": list(range(1, 22)),
    "P_SEXO": [1, 2],
    "P_PARENTESCOR": [1, 2, 3, 4, 5, 6],
    "PA_ASISTENCIA": [1, 2, 4, 9]
}
codigos_invalidos = {}
for columna in codigos:
    convertido = pd.to_numeric(df[columna], errors="coerce")
    incorrectos = df[columna].notna() & ~convertido.isin(codigos[columna])
    codigos_invalidos[columna] = int(incorrectos.sum())
    convertido = convertido.where(convertido.isin(codigos[columna]))
    # Int64 permite guardar enteros y valores vacíos
    df[columna] = convertido.astype("Int64")

# Guardar los datos de todas las edades

# Una respuesta vacía no significa que la persona no asistía
# En alojamientos especiales, el hogar y el parentesco pueden estar vacíos
df.to_csv(datos / "poblacion_limpia.csv", index=False, encoding="utf-8-sig")
# Contar los seis perfiles más frecuentes para la tabla de la página
grupos = df.groupby(["P_EDADR", "P_SEXO", "P_PARENTESCOR"]).size()
grupos = grupos.reset_index(name="PERSONAS").sort_values("PERSONAS", ascending=False)
grupos.head(6).to_csv(datos / "resumen_poblacion.csv", index=False, encoding="utf-8-sig")

# Contar las personas que se pueden usar en el modelo

jovenes = df[df["P_EDADR"].isin([2, 3, 4, 5])].copy()
respuesta_valida = jovenes["PA_ASISTENCIA"].isin([1, 2])
entradas_validas = (
    jovenes["P_SEXO"].isin([1, 2])
    & jovenes["P_PARENTESCOR"].isin([1, 2, 3, 4, 5])
)
hogar_valido = jovenes[["COD_ENCUESTAS", "U_VIVIENDA", "P_NROHOG"]].notna().all(axis=1)
personas_modelo = jovenes[respuesta_valida & entradas_validas & hogar_valido]
if len(personas_modelo) <= 10000:
    raise ValueError("No hay suficientes personas utilizables para el objetivo.")

resumen = {
    "originales": originales,
    "limpios": len(df),
    "duplicados_eliminados": duplicados,
    "nulos_originales": nulos.to_dict(),
    "codigos_invalidos": codigos_invalidos,
    "columnas_limpias": columnas,
    "personas_5_24": len(jovenes),
    "fuera_edad_modelo": len(df) - len(jovenes),
    "sin_respuesta_modelo": int((~respuesta_valida).sum()),
    "sin_entradas_modelo": int((respuesta_valida & ~entradas_validas).sum()),
    "sin_hogar_modelo": int(
        (respuesta_valida & entradas_validas & ~hogar_valido).sum()
    ),
    "personas_modelo": len(personas_modelo),
    "asistencia_5_24": {
        "si": int((jovenes["PA_ASISTENCIA"] == 1).sum()),
        "no": int((jovenes["PA_ASISTENCIA"] == 2).sum()),
        "no_informa": int((jovenes["PA_ASISTENCIA"] == 9).sum()),
        "no_aplica": int((jovenes["PA_ASISTENCIA"] == 4).sum()),
        "vacio": int(jovenes["PA_ASISTENCIA"].isna().sum())
    }
}
with open(datos / "resumen_limpieza.json", "w", encoding="utf-8") as salida:
    json.dump(resumen, salida, ensure_ascii=False, indent=2)

print("Registros originales:", originales)
print("Registros limpios conservados:", len(df))
print("Personas de 5 a 24 años:", len(jovenes))
print("Personas utilizables para el árbol:", len(personas_modelo))

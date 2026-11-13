# Revisar los datos, el modelo y la página
# Si una comprobación falla, assert detiene el programa
from pathlib import Path
import hashlib
import json
import pandas as pd
import numpy as np
from app import app, guardado

ruta = Path(__file__).resolve().parent
with open(ruta / "datos/resultados.json", encoding="utf-8") as archivo:
    resultados = json.load(archivo)

with open(ruta / "datos/resumen_limpieza.json", encoding="utf-8") as archivo:
    limpieza = json.load(archivo)

# Revisar las filas, el municipio y las respuestas vacías

columnas = ["U_DPTO", "U_MPIO", "P_EDADR", "PA_ASISTENCIA"]
original = pd.read_csv(
    ruta / "datos/poblacion_original.csv",
    usecols=columnas,
    dtype=str
)
limpio = pd.read_csv(
    ruta / "datos/poblacion_limpia.csv",
    usecols=columnas,
    dtype=str
)
assert len(original) > 10000
assert len(original) == limpieza["originales"]
assert len(limpio) == limpieza["limpios"]
assert ((original["U_DPTO"] == "08") & (original["U_MPIO"] == "001")).all()
assert ((limpio["U_DPTO"] == "08") & (limpio["U_MPIO"] == "001")).all()
assert original["PA_ASISTENCIA"].value_counts(dropna=False).equals(
    limpio["PA_ASISTENCIA"].value_counts(dropna=False)
)

# Revisar las edades y que no se repitan hogares entre los dos grupos

datos = pd.read_csv(ruta / "datos/datos_modelo.csv", dtype={"hogar": str})
assert len(datos) == resultados["personas_modelo"] == limpieza["personas_modelo"]
assert len(datos) > 10000
assert datos["P_EDADR"].isin([2, 3, 4, 5]).all()
assert datos["PA_ASISTENCIA"].isin([1, 2]).all()
assert datos["P_PARENTESCOR"].isin([1, 2, 3, 4, 5]).all()
train = datos[datos["conjunto"] == "Entrenamiento"]
test = datos[datos["conjunto"] == "Prueba"]
assert set(train["PA_ASISTENCIA"]) == set(test["PA_ASISTENCIA"]) == {1, 2}
assert set(train["hogar"]).isdisjoint(set(test["hogar"]))
assert len(train) == resultados["entrenamiento"]
assert len(test) == resultados["prueba"]
assert guardado["modelo"].tree_.n_node_samples[0] == len(train)
assert guardado["modelo"].get_depth() <= 3
assert guardado["variables"] == ["P_EDADR", "P_SEXO", "P_PARENTESCOR"]
assert "PA_ASISTENCIA" not in guardado["columnas"]

# Comparar las predicciones del modelo con las guardadas

# Comprobar las columnas de parentesco con get_dummies
entradas = pd.get_dummies(
    test[guardado["variables"]],
    columns=["P_PARENTESCOR"],
    dtype=int
)
entradas = entradas.reindex(columns=guardado["columnas"], fill_value=0)
calculadas = guardado["modelo"].predict(entradas.to_numpy())
guardadas = pd.read_csv(ruta / "datos/predicciones_prueba.csv")
assert np.array_equal(calculadas, guardadas["prediccion"].to_numpy())
assert np.array_equal(
    test["PA_ASISTENCIA"].to_numpy(),
    guardadas["PA_ASISTENCIA"].to_numpy()
)
matriz = [[0, 0], [0, 0]]
for real, predicha in zip(guardadas["PA_ASISTENCIA"], calculadas):
    matriz[int(real) - 1][int(predicha) - 1] += 1

assert matriz == resultados["matriz"]
exactitud = (matriz[0][0] + matriz[1][1]) / len(test)
assert abs(exactitud - resultados["exactitud"]) < 0.000000001

# Probar las 40 combinaciones del formulario

app.testing = True
cliente = app.test_client()
assert cliente.get("/").status_code == 200
predicciones_web = set()
for edad in [2, 3, 4, 5]:
    for sexo in [1, 2]:
        for parentesco in [1, 2, 3, 4, 5]:
            # Preparar las entradas para comprobar la respuesta del formulario
            fila = [edad, sexo]
            for opcion in [1, 2, 3, 4, 5]:
                fila.append(int(parentesco == opcion))
            esperado = int(guardado["modelo"].predict([fila])[0])
            respuesta = cliente.post(
                "/",
                data={
                    "P_EDADR": edad,
                    "P_SEXO": sexo,
                    "P_PARENTESCOR": parentesco
                }
            )
            assert respuesta.status_code == 200
            assert f'data-prediccion="{esperado}"' in respuesta.get_data(as_text=True)
            predicciones_web.add(esperado)

assert predicciones_web == {1, 2}

# Comprobar que el formulario rechace opciones inválidas

for variable, valor in [
    ("P_EDADR", ""),
    ("P_EDADR", "1"),
    ("P_EDADR", "6"),
    ("P_SEXO", "9"),
    ("P_PARENTESCOR", "6"),
    ("P_EDADR", "NaN")
]:
    formulario = {"P_EDADR": "3", "P_SEXO": "1", "P_PARENTESCOR": "3"}
    formulario[variable] = valor
    assert cliente.post("/", data=formulario).status_code == 400

for archivo in ["arbol.png", "graficas.png", "matriz_confusion.png"]:
    respuesta = cliente.get("/imagenes/" + archivo)
    assert respuesta.status_code == 200 and respuesta.data.startswith(b"\x89PNG")

assert cliente.get("/static/style.css").status_code == 200
assert cliente.get("/descargar/predicciones").status_code == 200
assert cliente.get("/imagenes/../modelo.pkl").status_code == 404

# Comprobar que el ejemplo de clase no haya cambiado

ejemplo = ruta / "arbol_ejemplo.py"
if ejemplo.exists():
    huella = hashlib.sha256(ejemplo.read_bytes()).hexdigest()
    assert huella == "0f02444336be5ef56b6331e0aac50c23cfddce0fab3a2d24ff4637e0c9882419"
    print("arbol_ejemplo.py permanece intacto.")
else:
    print("No se comprobó arbol_ejemplo.py porque no está en la carpeta.")
print(
    "Verificación correcta: datos, hogares, predicciones, métricas, "
    "40 perfiles web, entradas inválidas e imágenes."
)

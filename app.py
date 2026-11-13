# Página de datos y predicciones

# Importar librerías y crear la página

from flask import Flask, render_template, request, send_from_directory
from pathlib import Path
import pandas as pd
import pickle
import json

ruta = Path(__file__).resolve().parent
app = Flask(__name__)

# Cargar el modelo entrenado

with open(ruta / "modelo.pkl", "rb") as archivo:
    guardado = pickle.load(archivo)

modelo = guardado["modelo"]
variables = guardado["variables"]
opciones = {
    "P_EDADR": guardado["edades"],
    "P_SEXO": guardado["sexos"],
    "P_PARENTESCOR": guardado["parentescos"]
}

# Leer los resultados y las filas de ejemplo

with open(ruta / "datos/resultados.json", encoding="utf-8") as archivo:
    resultados = json.load(archivo)

with open(ruta / "datos/resumen_limpieza.json", encoding="utf-8") as archivo:
    limpieza = json.load(archivo)

with open(ruta / "datos/fuente.json", encoding="utf-8") as archivo:
    fuente = json.load(archivo)

muestra = pd.read_csv(
    ruta / "datos/poblacion_limpia.csv",
    dtype=str,
    nrows=6
).fillna("Vacío")
pruebas = pd.read_csv(ruta / "datos/predicciones_prueba.csv", nrows=8)

# Mostrar la página y recibir el formulario

@app.route("/", methods=["GET", "POST"])
def inicio():
    # Opciones iniciales del formulario
    valores = {"P_EDADR": 3, "P_SEXO": 1, "P_PARENTESCOR": 3}
    prediccion = None
    codigo_prediccion = None
    error = None
    estado = 200
    if request.method == "POST":
        try:
            # Revisar las opciones seleccionadas
            for variable in variables:
                valor = int(request.form.get(variable, ""))
                if valor not in opciones[variable]:
                    raise ValueError("Código no permitido")
                valores[variable] = valor

            # Usar el mismo orden de entradas que en el entrenamiento
            entrada = [valores["P_EDADR"], valores["P_SEXO"]]
            for codigo in [1, 2, 3, 4, 5]:
                if valores["P_PARENTESCOR"] == codigo:
                    entrada.append(1)
                else:
                    entrada.append(0)

            # Predecir con los datos del formulario
            nuevos_valores = [entrada]
            predicciones = modelo.predict(nuevos_valores)
            codigo_prediccion = int(predicciones[0])
            prediccion = guardado["clases"][codigo_prediccion]
        except ValueError:
            error = (
                "Selecciona una opción válida en edad, sexo y parentesco. "
                "Solo se admiten edades de 5 a 24 años."
            )
            estado = 400

    # Enviar los datos al HTML
    return render_template(
        "index.html",
        resultados=resultados,
        limpieza=limpieza,
        fuente=fuente,
        opciones=opciones,
        clases=guardado["clases"],
        valores=valores,
        prediccion=prediccion,
        codigo_prediccion=codigo_prediccion,
        error=error,
        muestra=muestra.to_dict("records"),
        pruebas=pruebas.to_dict("records")
    ), estado

# Mostrar imágenes y descargar predicciones

@app.route("/imagenes/<path:nombre>")
def imagen(nombre):
    return send_from_directory(ruta / "imagenes", nombre)

@app.route("/descargar/predicciones")
def descargar_predicciones():
    return send_from_directory(
        ruta / "datos",
        "predicciones_prueba.csv",
        as_attachment=True
    )

# Iniciar la página al ejecutar este archivo

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

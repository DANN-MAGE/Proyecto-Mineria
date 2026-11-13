# Predecir la asistencia escolar

# Importar librerías
from pathlib import Path
import os
import pickle
import json
import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import ConfusionMatrixDisplay

# Carpeta donde está este archivo
ruta = Path(__file__).resolve().parent
# Guardar la caché de Matplotlib en el proyecto
os.environ["MPLCONFIGDIR"] = str(ruta / ".venv/matplotlib")
import matplotlib
matplotlib.use("Agg")  # Guardar imágenes sin abrir ventanas
import matplotlib.pyplot as plt

# Leer los datos
df = pd.read_csv(
    ruta / "datos/poblacion_limpia.csv",
    dtype={"U_DPTO": str, "U_MPIO": str, "COD_ENCUESTAS": str,
           "U_VIVIENDA": str, "P_NROHOG": str}
)
# Barranquilla: departamento 08 y municipio 001
if not ((df["U_DPTO"] == "08") & (df["U_MPIO"] == "001")).all():
    raise ValueError("Los datos deben corresponder únicamente a Barranquilla.")
# Edades DANE: 2 = 5–9, 3 = 10–14, 4 = 15–19, 5 = 20–24
datos = df[df["P_EDADR"].isin([2, 3, 4, 5])].copy()
datos = datos[datos["PA_ASISTENCIA"].isin([1, 2])]
datos = datos[datos["P_SEXO"].isin([1, 2])]
datos = datos[datos["P_PARENTESCOR"].isin([1, 2, 3, 4, 5])]
datos = datos.dropna(subset=["COD_ENCUESTAS", "U_VIVIENDA", "P_NROHOG"])
variables = ["P_EDADR", "P_SEXO", "P_PARENTESCOR"]
datos[variables + ["PA_ASISTENCIA"]] = datos[variables + ["PA_ASISTENCIA"]].astype(int)
if len(datos) <= 10000:
    raise ValueError("Se necesitan más de 10.000 registros utilizables.")

# Preparar las entradas y la respuesta
entradas = datos[["P_EDADR", "P_SEXO"]].copy()
# Una columna por parentesco, porque sus códigos no indican un orden
for codigo in [1, 2, 3, 4, 5]:
    # 1 si pertenece a ese parentesco, 0 si no
    entradas["P_PARENTESCOR_" + str(codigo)] = (datos["P_PARENTESCOR"] == codigo).astype(int)
X = entradas.to_numpy()
y = datos["PA_ASISTENCIA"].to_numpy()
clases = {1: "Sí asistía", 2: "No asistía"}

# Separar entrenamiento y prueba por hogares
# Unir los tres códigos para identificar cada hogar
datos["hogar"] = datos["COD_ENCUESTAS"] + "-" + datos["U_VIVIENDA"] + "-" + datos["P_NROHOG"]
# Las personas de un mismo hogar deben quedar en el mismo grupo
hogares_entrenamiento, hogares_prueba = train_test_split(
    datos["hogar"].unique(), test_size=0.20, random_state=42
)
es_entrenamiento = datos["hogar"].isin(hogares_entrenamiento)
es_prueba = datos["hogar"].isin(hogares_prueba)
X_train = X[es_entrenamiento]
X_test = X[es_prueba]
y_train = y[es_entrenamiento]
y_test = y[es_prueba]
if set(y_train) != {1, 2} or set(y_test) != {1, 2}:
    raise ValueError("Ambos conjuntos deben contener las dos clases.")

# Crear y entrenar el árbol
modelo = tree.DecisionTreeClassifier(
    max_depth=3, min_samples_leaf=100, random_state=42
)
modelo.fit(X_train, y_train)

# Predecir y evaluar
predicciones = modelo.predict(X_test)
exactitud = accuracy_score(y_test, predicciones)
matriz = confusion_matrix(y_test, predicciones, labels=[1, 2])
reporte = classification_report(
    y_test, predicciones, labels=[1, 2], target_names=list(clases.values()),
    output_dict=True, zero_division=0
)
# Comparar con responder siempre la opción más común del entrenamiento
clase_frecuente = int(pd.Series(y_train).mode().iloc[0])
exactitud_base = accuracy_score(y_test, [clase_frecuente] * len(y_test))

# Mostrar las primeras predicciones y la exactitud
print("Personas de entrenamiento:", len(y_train))
print("Personas de prueba:", len(y_test))
print("Variables:", variables)
print("Categorías:", clases)
for real, pred in zip(y_test[:10], predicciones[:10]):
    print(f"Respuesta real: {clases[real]} -> Predicción: {clases[pred]}")
print(f"Exactitud: {exactitud:.2%}")
print(f"Exactitud de la clase más frecuente: {exactitud_base:.2%}")
print("Matriz de confusión:\n", matriz)

# Dibujar el árbol
imagenes = ruta / "imagenes"
imagenes.mkdir(exist_ok=True)
nombres = ["Grupo de edad", "Sexo (1=hombre, 2=mujer)", "Jefe/a (0/1)",
           "Pareja (0/1)", "Hijo/a (0/1)", "Otro pariente (0/1)", "No pariente (0/1)"]
plt.figure(figsize=(19, 9))
tree.plot_tree(
    modelo, feature_names=nombres, class_names=list(clases.values()),
    filled=True, rounded=True, fontsize=10, impurity=False
)
plt.title("Asistencia educativa · Barranquilla · Personas de 5–24 años · Censo 2018", fontsize=16)
plt.tight_layout()
plt.savefig(imagenes / "arbol.png", dpi=160, bbox_inches="tight")
plt.close()

# Matriz de confusión: filas reales y columnas predichas
figura, eje = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay(matriz, display_labels=list(clases.values())).plot(
    ax=eje, cmap="Blues", colorbar=False, values_format="d"
)
eje.set_title("Predicciones en hogares reservados para prueba")
eje.set_xlabel("Predicción del árbol")
eje.set_ylabel("Respuesta real del censo")
plt.tight_layout()
plt.savefig(imagenes / "matriz_confusion.png", dpi=160)
plt.close()

# Guardar el modelo y las opciones del formulario
guardado = {
    "modelo": modelo,
    "variables": variables,
    "columnas": entradas.columns.tolist(),
    "clases": clases,
    "edades": {2: "5–9 años", 3: "10–14 años", 4: "15–19 años", 5: "20–24 años"},
    "sexos": {1: "Hombre", 2: "Mujer"},
    "parentescos": {
        1: "Jefe(a) del hogar", 2: "Pareja", 3: "Hijo(a) o hijastro(a)",
        4: "Otro pariente", 5: "Otro no pariente"
    }
}
with open(ruta / "modelo.pkl", "wb") as archivo:
    pickle.dump(guardado, archivo)

# Guardar los datos y las predicciones de prueba
datos["conjunto"] = "Entrenamiento"
datos.loc[es_prueba, "conjunto"] = "Prueba"
datos.to_csv(ruta / "datos/datos_modelo.csv", index=False, encoding="utf-8-sig")
salida = datos.loc[es_prueba, variables + ["PA_ASISTENCIA", "hogar"]].copy()
salida["prediccion"] = predicciones
salida.to_csv(ruta / "datos/predicciones_prueba.csv", index=False, encoding="utf-8-sig")

# Guardar los resultados para la página
resultados = {
    "personas_modelo": len(datos),
    "entrenamiento": len(y_train),
    "prueba": len(y_test),
    "hogares_entrenamiento": len(hogares_entrenamiento),
    "hogares_prueba": len(hogares_prueba),
    "exactitud": exactitud,
    "exactitud_base": exactitud_base,
    "aciertos": int((y_test == predicciones).sum()),
    "matriz": matriz.tolist(),
    "reporte": reporte,
    "clases": list(clases.values()),
    "profundidad": int(modelo.get_depth()),
    "hojas": int(modelo.get_n_leaves())
}
with open(ruta / "datos/resultados.json", "w", encoding="utf-8") as archivo:
    json.dump(resultados, archivo, ensure_ascii=False, indent=2)
print("Modelo, métricas, predicciones, árbol y matriz guardados.")

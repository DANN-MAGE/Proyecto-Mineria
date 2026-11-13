# Gráficas de la población de Barranquilla

# Importar librerías
from pathlib import Path
import os
import pickle
import pandas as pd

# Usar las carpetas del proyecto
ruta = Path(__file__).resolve().parent
os.environ["MPLCONFIGDIR"] = str(ruta / ".venv/matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

imagenes = ruta / "imagenes"
imagenes.mkdir(exist_ok=True)

# Leer los datos y los grupos de edad
df = pd.read_csv(ruta / "datos/poblacion_limpia.csv")
datos = pd.read_csv(ruta / "datos/datos_modelo.csv")
with open(ruta / "modelo.pkl", "rb") as archivo:
    edades = pickle.load(archivo)["edades"]

# Crear una figura con cuatro gráficas
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})
figura, ejes = plt.subplots(2, 2, figsize=(13, 9))

# Personas por grupo de edad
nombres_edades = ["0–4", "5–9", "10–14", "15–19", "20–24", "25–44", "45–64", "65+"]
rangos_codigos = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 9), (10, 13), (14, 21)]
conteo_edad = []
for minimo, maximo in rangos_codigos:
    cantidad = df["P_EDADR"].between(minimo, maximo).sum()
    conteo_edad.append(int(cantidad))

ejes[0, 0].bar(nombres_edades, conteo_edad, color="#187b7b")
ejes[0, 0].set_title("Población de Barranquilla por edad")
ejes[0, 0].set_xlabel("Años (grupos de diferente amplitud)")
ejes[0, 0].set_ylabel("Personas censadas")

# Cantidad de hombres y mujeres
conteo_sexo = df["P_SEXO"].value_counts().sort_index()
ejes[0, 1].bar(
    ["Hombres", "Mujeres"],
    conteo_sexo.reindex([1, 2], fill_value=0),
    color=["#355d73", "#187b7b"]
)
ejes[0, 1].set_title("Población de Barranquilla por sexo")
ejes[0, 1].set_ylabel("Personas censadas")

# Asistencia escolar, incluyendo respuestas vacías
jovenes = df[df["P_EDADR"].isin([2, 3, 4, 5])]
asistencia = [
    int((jovenes["PA_ASISTENCIA"] == 1).sum()),
    int((jovenes["PA_ASISTENCIA"] == 2).sum()),
    int((jovenes["PA_ASISTENCIA"] == 9).sum()),
    int(
        (
            (jovenes["PA_ASISTENCIA"] == 4)
            | jovenes["PA_ASISTENCIA"].isna()
        ).sum()
    )
]
ejes[1, 0].bar(
    ["Sí", "No", "No informa", "No aplica / vacío"],
    asistencia,
    color=["#187b7b", "#c17949", "#8c9595", "#bbc2bd"]
)
ejes[1, 0].set_title("Asistencia educativa en personas de 5–24 años")
ejes[1, 0].set_ylabel("Personas censadas")

# Porcentaje de asistencia por edad
porcentaje_si = []
for codigo in edades:
    grupo = datos[datos["P_EDADR"] == codigo]
    asistentes = grupo[grupo["PA_ASISTENCIA"] == 1]
    if len(grupo) > 0:
        porcentaje = 100 * len(asistentes) / len(grupo)
    else:
        porcentaje = float("nan")  # Dejar vacío si el grupo no tiene personas
    porcentaje_si.append(porcentaje)

ejes[1, 1].bar(list(edades.values()), porcentaje_si, color="#187b7b")
ejes[1, 1].set_ylim(0, 100)
ejes[1, 1].set_title("Asistencia por edad en los registros del modelo")
ejes[1, 1].set_ylabel("Porcentaje que respondió sí (%)")
figura.suptitle("DANE · Censo Nacional de Población y Vivienda 2018", fontsize=17)
plt.tight_layout()
plt.savefig(imagenes / "graficas.png", dpi=160)
plt.close()
print("Gráficas de población guardadas.")

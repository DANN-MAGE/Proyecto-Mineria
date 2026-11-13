# Minería de datos: asistencia escolar en Barranquilla

Este proyecto clasifica si una persona de **5 a 24 años** asistía o no a una institución educativa, según los patrones del **Censo 2018 del DANE**. Usa un árbol de decisión pequeño y una página local con Flask.

El archivo `arbol_ejemplo.py` se usó como referencia. El árbol sigue sus pasos: cargar datos, preparar entradas y etiquetas, crear `DecisionTreeClassifier`, entrenar con `.fit()`, predecir con `.predict()` y dibujar con `tree.plot_tree()`.

## Cómo se parece al ejemplo de clase

| En el ejemplo del viento | En este proyecto |
| --- | --- |
| `pd.read_csv()` carga las velocidades | `pd.read_csv()` carga el censo limpio |
| `features` contiene las entradas | `X` contiene edad, sexo y columnas de parentesco |
| `labels` se crea con rangos de viento | `y` toma las respuestas reales de `PA_ASISTENCIA` |
| `DecisionTreeClassifier()` crea el árbol | La misma instrucción, limitada a tres niveles |
| `.fit()` entrena | `.fit()` entrena con los hogares de entrenamiento |
| `.predict()` clasifica nuevos valores | `.predict()` clasifica las personas de prueba y el formulario |
| Un `for` muestra las predicciones | Un `for` muestra respuestas reales y predicciones |
| `tree.plot_tree()` dibuja | La misma instrucción guarda la imagen para la web |

No hace falta inventar categorías con condiciones: el censo ya trae las dos respuestas. El formulario sí usa `for` e `if/else` para preparar una lista de entrada, como `nuevos_valores` en clase.

El código principal se lee de arriba hacia abajo. `arbol_decision.py` contiene la selección de personas, el entrenamiento, las predicciones, las métricas, el árbol, la matriz de confusión y el guardado de resultados. `graficas.py` contiene solo las gráficas de población. Sustituye al anterior `graficas_resultados.py`, que ya no se necesita. No hay clases propias ni otro algoritmo de aprendizaje.

Hay pasos adicionales necesarios para este trabajo: separar entrenamiento y prueba, evaluar los errores, representar el parentesco con 0/1 y guardar el modelo. `Path` permite encontrar los archivos desde cualquier directorio; `pickle` guarda el árbol y `json` guarda los resúmenes que muestra Flask. Se conserva `MPLCONFIGDIR` para que Matplotlib escriba su caché dentro del proyecto, y `Agg` para guardar imágenes sin abrir ventanas. En `app.py`, `@app.route` conecta una dirección con una función de Flask.

## Abrir la página en este computador

Abre la carpeta `Proyecto-Mineria` en Visual Studio Code. En su terminal de PowerShell ejecuta:

```powershell
cd "C:\Users\Xenno\OneDrive\Desktop\Proyecto-Mineria"
.\.venv\Scripts\python.exe app.py
```

Abre **http://127.0.0.1:5000** en el navegador. Para detener la página, presiona `Ctrl+C` en la terminal.

Los datos, las imágenes y el modelo ya están generados. No necesitas volver a entrenar para abrir la página. No hace falta activar el entorno ni cambiar la política de ejecución de PowerShell.

## Preparar una copia descargada de GitHub

Abre la carpeta descargada en una terminal. Necesitas Python 3.12 e internet para descargar el archivo del DANE la primera vez.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe descargar_datos.py
.\.venv\Scripts\python.exe limpieza_datos.py
.\.venv\Scripts\python.exe arbol_decision.py
.\.venv\Scripts\python.exe graficas.py
.\.venv\Scripts\python.exe verificar_proyecto.py
.\.venv\Scripts\python.exe app.py
```

Después abre **http://127.0.0.1:5000**. Ejecuta los comandos en ese orden, esperando a que termine cada uno.

El repositorio incluye el código, las imágenes, el modelo, las predicciones de prueba y los resúmenes. El ZIP del DANE y los CSV de población y selección del modelo se generan con los comandos anteriores; no se suben porque son archivos grandes que pueden recuperarse desde la fuente. Tampoco se suben el entorno de Python ni las cachés. Los archivos que ya tienes en tu computador se conservan.

`arbol_ejemplo.py` se usó como referencia, pero actualmente no está en la carpeta. La comprobación de su integridad solo se ejecuta cuando ese archivo está presente.

## Fuente única y descarga

- [Catálogo del Censo 2018 del DANE](https://microdatos.dane.gov.co/catalog/643/get_microdata).
- Archivo oficial: **08_Atlantico.zip**.
- [Descarga directa del mismo archivo](https://microdatos.dane.gov.co/index.php/catalog/643/download/12144).
- Dentro del ZIP está `08Atlantico/08_Atlantico_CSV.zip` y dentro de este, **CNPV2018_5PER_A2_08.CSV**, correspondiente a PERSONAS.

No se combinan fuentes ni tablas de otras entidades. No se usan las proyecciones de población ni el análisis de envejecimiento del enfoque anterior.

En este CSV, `U_DPTO` contiene `08` y `U_MPIO` contiene `001`. Su combinación es el código **08001** de Barranquilla. Se filtran ambas columnas, leídas como texto para conservar los ceros.

El archivo de Atlántico tiene **2.342.265 personas**. El original filtrado de Barranquilla tiene **1.120.103 filas de datos**, sin contar el encabezado, y **48 columnas originales**. Cada fila es una persona anonimizada; no se inventaron ni multiplicaron registros.

`datos/fuente.json` guarda los enlaces, los conteos y la huella SHA-256 del ZIP para identificar la fuente utilizada. El ZIP oficial se conserva en `datos`. El CSV descomprimido de todo Atlántico es temporal: se elimina después de guardar correctamente los registros de Barranquilla y la procedencia. Puede recuperarse desde el mismo ZIP.

## Qué se hizo durante la limpieza

`limpieza_datos.py` selecciona 11 columnas, muestra las primeras filas, los tipos, los nulos y los duplicados. Convierte las variables demográficas a números y conserva los identificadores como texto.

- Originales: **1.120.103** personas.
- CSV limpio: **1.120.103** personas.
- Duplicados exactos eliminados: **0**.
- Códigos fuera del diccionario en las variables seleccionadas: **0**.
- Vacíos: **4.613** en `P_NROHOG`, **4.613** en `P_PARENTESCOR` y **83.793** en `PA_ASISTENCIA`. Las demás columnas seleccionadas no tienen nulos.

Los vacíos se conservan. No se convierten en una respuesta negativa. Los vacíos de hogar y parentesco pueden corresponder a personas en lugares especiales de alojamiento. Dos personas con el mismo perfil demográfico no se consideran duplicadas: se revisan sus identificadores.

El archivo limpio conserva todas las edades, las respuestas `No informa` y los valores no aplicables. La exclusión para entrenar se hace aparte:

| Paso | Personas |
| --- | ---: |
| Personas de 5–24 años | 360.060 |
| Respuesta «Sí» | 244.411 |
| Respuesta «No» | 109.290 |
| «No informa», código 9 | 4.843 |
| Respuesta vacía | 1.516 |
| «No aplica», código 4, dentro de 5–24 años | 0 |
| Total utilizable para el modelo | **353.701** |

Las **6.359** personas sin respuesta 1 o 2 no participan en entrenamiento ni evaluación. No hubo exclusiones adicionales por entradas inválidas o identificación de hogar entre las personas con respuesta válida.

## Variables y códigos

El objetivo es **PA_ASISTENCIA**: `1 = Sí asistía` y `2 = No asistía`. No es una entrada del árbol.

| Entrada | Significado |
| --- | --- |
| `P_EDADR` | 2: 5–9 años; 3: 10–14; 4: 15–19; 5: 20–24 |
| `P_SEXO` | 1: hombre; 2: mujer |
| `P_PARENTESCOR` | 1: jefe(a); 2: pareja; 3: hijo(a) o hijastro(a); 4: otro pariente; 5: otro no pariente |

Consulta los diccionarios originales del DANE: [edad](https://microdatos.dane.gov.co/index.php/catalog/643/variable/F11/V576?name=P_EDADR), [sexo](https://microdatos.dane.gov.co/index.php/catalog/643/variable/F11/V575?name=P_SEXO), [parentesco](https://microdatos.dane.gov.co/index.php/catalog/643/variable/F11/V577?name=P_PARENTESCOR) y [asistencia](https://microdatos.dane.gov.co/index.php/catalog/643/variable/F11/V587?name=PA_ASISTENCIA).

Los códigos se comprobaron con estos diccionarios. En asistencia, `4` significa «No aplica» y `9`, «No informa»; en parentesco, `6` significa «No aplica». Esos códigos y los vacíos se excluyen de la selección del modelo, sin borrarlos del CSV poblacional.

`P_EDADR` es un grupo de cinco años, no la edad exacta. No se transforma el grupo en una edad inventada. Un ciclo `for` prepara cinco columnas para el parentesco: cada una vale 1 si el código coincide y 0 si no coincide. Por ejemplo, una persona con parentesco 3 tiene las columnas de parentesco `[0, 0, 1, 0, 0]`. Así no se inventa un orden entre parentescos. Sexo y grupo de edad se mantienen como códigos.

No se usan nivel educativo, alfabetismo, actividad laboral ni identificadores como entradas. Esto evita incluir variables que puedan revelar directamente la asistencia.

## Cómo se entrenó el árbol

Primero se seleccionan las personas con edades y respuestas válidas. Luego se forman identificadores de hogar con los códigos anónimos de encuesta, vivienda y hogar.

`train_test_split()` separa al azar el **80% de los hogares** para entrenamiento y el **20%** para prueba, con `random_state=42`. Todas las personas de un hogar quedan juntas. Por eso la proporción de personas es aproximadamente 80/20, no necesariamente exacta.

- Entrenamiento: **283.042 personas de 153.139 hogares**.
- Prueba: **70.659 personas de 38.285 hogares**.
- Ningún hogar aparece en ambos conjuntos.
- Árbol: `DecisionTreeClassifier(max_depth=3, min_samples_leaf=100, random_state=42)`.
- Resultado: **3 niveles de preguntas y 8 hojas**.

El árbol aprende solo con entrenamiento. Se guarda ese mismo modelo en `modelo.pkl`; no se vuelve a entrenar con las personas de prueba. Flask carga ese archivo y usa las mismas columnas que el entrenamiento.

`modelo.fit(X_train, y_train)` aprende preguntas usando las características y respuestas conocidas del entrenamiento. `modelo.predict(X_test)` aplica esas preguntas a las personas reservadas para prueba, sin recibir sus respuestas reales. Después se comparan las predicciones con `y_test`.

Para leer el dibujo, empieza arriba y sigue cada pregunta: si se cumple, ve a la izquierda; si no, a la derecha. Por ejemplo, `Grupo de edad <= 3.5` separa los códigos 2 y 3 (5–14 años) de los códigos 4 y 5 (15–24 años). Una pregunta de parentesco `<= 0.5` separa a quienes no pertenecen a esa categoría (0) de quienes sí (1). Al llegar a una hoja, `class` indica la respuesta del modelo. En la imagen generada, `samples` cuenta las personas de entrenamiento en ese nodo y `value` muestra las cantidades de «Sí» y «No», en ese orden.

## Resultados obtenidos

La exactitud fue **78,85%**, con **55.716 aciertos de 70.659 personas**. Responder siempre «Sí asistía», la clase más frecuente del entrenamiento, obtiene **68,67%** en la misma prueba.

`accuracy_score()` calcula **aciertos / personas de prueba**. Al multiplicar por 100 obtenemos el porcentaje: `55.716 / 70.659 × 100 = 78,85%`. Esto describe el rendimiento en esta prueba, no una garantía para cada persona.

| Respuesta real / Predicción | Sí asistía | No asistía |
| --- | ---: | ---: |
| Sí asistía | 42.351 | 6.172 |
| No asistía | 8.771 | 13.365 |

La diagonal muestra aciertos. Por ejemplo, **8.771** personas que respondieron «No» fueron clasificadas como «Sí». El árbol identifica el **87,28%** de quienes sí asistían y el **60,38%** de quienes no asistían: la exactitud general no cuenta toda la historia.

Las métricas completas están en `datos/resultados.json`. Todas las predicciones de prueba están en `datos/predicciones_prueba.csv`. `datos/datos_modelo.csv` identifica las personas y el conjunto que les correspondió.

Se conserva `classification_report()` porque la web usa sus resultados por clase: precisión indica cuántas predicciones de una categoría acertaron; sensibilidad (`recall`) indica cuántas personas de esa categoría fueron identificadas. Se retiraron del JSON las importancias y distribuciones que ningún archivo consultaba, y las listas de variables duplicadas que ya están en `modelo.pkl`.

## Gráficas y página web

`imagenes/graficas.png` muestra población por edad, población por sexo, respuestas de asistencia en 5–24 años y porcentaje de asistencia por grupo de edad. Los vacíos y «No informa» se presentan por separado. Los grupos de la gráfica general de edad tienen amplitudes diferentes, indicadas en el eje.

`imagenes/arbol.png` muestra las preguntas aprendidas y `imagenes/matriz_confusion.png` muestra los aciertos y errores. Solo hay información de **2018**, por eso no se inventa una gráfica anual.

La web incluye inicio, fuente, limpieza, análisis poblacional, árbol, formulario y resultados. El formulario tiene tres listas de selección. Al pulsar **Predecir**, Flask prepara la entrada y llama a `modelo.predict()`. La respuesta no está predefinida.

El HTML tiene separados los bloques, las tablas y los ciclos que muestran datos. El CSS tiene una propiedad por línea. No se usan JavaScript, React ni librerías adicionales para la página.

## Ejecutar nuevamente todo el proceso

Desde la terminal de Visual Studio Code, ubicada en `Proyecto-Mineria`:

```powershell
.\.venv\Scripts\python.exe descargar_datos.py
.\.venv\Scripts\python.exe limpieza_datos.py
.\.venv\Scripts\python.exe arbol_decision.py
.\.venv\Scripts\python.exe graficas.py
.\.venv\Scripts\python.exe verificar_proyecto.py
.\.venv\Scripts\python.exe app.py
```

Ejecuta un comando después de que termine el anterior. `arbol_decision.py` actualiza el modelo, el reporte, las predicciones, el árbol y la matriz. Después ejecuta `graficas.py` para actualizar las gráficas de población; este archivo no vuelve a entrenar ni recalcula las métricas. La descarga solo necesita internet si falta `datos/08_Atlantico.zip`. Si falla el enlace, revisa el catálogo oficial antes de cambiar la fuente. Detén Flask y vuelve a abrirlo si regeneras el modelo.

En otro computador con **Python 3.12 instalado**, crea su propio entorno antes de ejecutar los comandos anteriores:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Archivos que debes estudiar y entregar

| Archivo o carpeta | Para qué sirve |
| --- | --- |
| `arbol_ejemplo.py` (si se agrega) | Referencia original de clase; no es necesario para ejecutar la página |
| `descargar_datos.py` | Descargar, descomprimir y filtrar el archivo oficial |
| `limpieza_datos.py` | Revisar y preparar las columnas necesarias |
| `arbol_decision.py` | Seleccionar, entrenar, evaluar y guardar el árbol, la matriz y los resultados |
| `graficas.py` | Dibujar la distribución de edades, sexo y asistencia |
| `app.py` | Conectar el modelo con Flask |
| `templates/index.html` | Contenido y formulario de la página |
| `static/style.css` | Apariencia y adaptación a pantallas pequeñas |
| `datos/` | Fuente, CSV, resúmenes y predicciones |
| `imagenes/` | Gráficas generadas |
| `modelo.pkl` | Árbol entrenado que usa la web |
| `requirements.txt` | Librerías y versiones utilizadas |
| `verificar_proyecto.py` | Comprobaciones reproducibles |
| `README.md` | Explicación y comandos |

Las carpetas **`.python`** y **`.venv`** son del entorno de ejecución; no son código del trabajo ni necesitas estudiarlas o entregarlas. `.python` contiene Python local y `.venv` contiene las librerías. No las borres en este computador mientras quieras seguir usando el entorno preparado.

Se retiraron la caché de instalación `.uv-cache`, los archivos `__pycache__`, los perfiles temporales del navegador y sus registros de errores. Si las cachés vuelven a generarse, puedes omitirlas al entregar. No se eliminaron los CSV de Barranquilla, el ZIP oficial, el modelo ni sus resultados.

`.vscode/settings.json` selecciona el Python del entorno y oculta sus carpetas técnicas en el explorador de VS Code. Los programas principales quedan en la raíz; `datos`, `imagenes`, `templates` y `static` agrupan los archivos según su función.

## Comprobaciones realizadas

Se ejecutaron descarga/extracción, limpieza y entrenamiento. Se comprobaron los conteos, la conservación de respuestas, la separación de hogares, las predicciones guardadas, las métricas y la integridad del ejemplo original.

Después de esta simplificación se ejecutaron nuevamente `arbol_decision.py`, `graficas.py` y `verificar_proyecto.py`. El entrenamiento también funcionó iniciándolo desde la carpeta `datos`. Todas las predicciones de prueba y las métricas conservadas coinciden exactamente con las anteriores. Se verificaron la huella del ZIP y las 48 columnas de las 1.120.103 filas originales contra el filtro de Barranquilla del archivo PERSONAS del ZIP, sin modificar los datos. No fue necesario repetir la limpieza.

Se probaron las **40 combinaciones** del formulario con el cliente de Flask, las entradas inválidas, las imágenes y la descarga CSV. Se inició el servidor y respondió **HTTP 200** en `http://127.0.0.1:5000`. Las gráficas se revisaron visualmente. La captura automática de la página con Edge no pudo completarse por restricciones del entorno; la revisión visual final de la web debe hacerse al abrirla en el navegador.

## Explicación breve para la sustentación

«Tomé el archivo PERSONAS del Censo 2018 del DANE y filtré Barranquilla. Revisé nulos y duplicados sin inventar respuestas. Seleccioné personas de 5 a 24 años que respondieron sí o no a asistencia escolar. Separé los hogares para entrenar y probar sin repetirlos. El árbol usa edad, sexo y parentesco, tiene tres niveles y obtuvo 78,85% de exactitud. La página permite probar sus predicciones históricas.»

## Limitaciones

El árbol describe asociaciones, no causas. Sus resultados corresponden a **2018**, no a la asistencia actual de una persona. No está validado para otras ciudades, edades o años. La exclusión de respuestas faltantes limita su representatividad. Separar hogares reduce la similitud entre conjuntos, pero no garantiza independencia entre vecinos. Es un ejercicio académico; las tres características no permiten conocer con certeza la respuesta individual.

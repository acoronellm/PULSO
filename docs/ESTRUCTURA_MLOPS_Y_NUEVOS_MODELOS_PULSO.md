# Estructura MLOps de PULSO y guía para incorporar nuevos modelos

## 1. Objetivo

Este documento describe la estructura actual del componente MLOps de PULSO y establece cómo deben incorporarse nuevos modelos de Machine Learning sin perder reproducibilidad, comparabilidad ni trazabilidad.

El objetivo principal es que cada modelo pueda responder preguntas como:

- ¿Qué datos utilizó?
- ¿Qué variables utilizó?
- ¿Qué versión del código lo generó?
- ¿Qué hiperparámetros utilizó?
- ¿Qué métricas obtuvo?
- ¿Qué preprocesamiento recibió?
- ¿Qué ejecución de MLflow corresponde a ese modelo?
- ¿Puede reproducirse?

## 2. Estructura general del proyecto

La organización esperada es:

```text
PULSO/
│
├── data/
│   ├── raw/
│   │   └── cardio_train.csv
│   └── processed/
│       └── cardio_clean_v1.csv
│
├── notebooks/
│   ├── eda/
│   │   ├── [notebook EDA 1]
│   │   ├── [notebook EDA 2]
│   │   └── [notebook EDA 3]
│   └── modeling/
│       ├── regresion_logistica.ipynb
│       └── arbol_decision.ipynb
│
├── ml/
│   ├── __init__.py
│   ├── prepare.py
│   ├── common.py
│   ├── train.py
│   ├── evaluate.py
│   └── configs/
│       ├── logistic_regression.yaml
│       └── decision_tree.yaml
│
├── tests/
│   └── test_training.py
│
├── .github/
│   └── workflows/
│       └── ml-training-ci.yml
│
├── docs/
│   ├── data_preparation.md
│   ├── ml_training.md
│   └── [esta documentación]
│
├── requirements-ml.txt
├── .gitignore
└── README.md
```

## 3. Responsabilidad de cada componente

### `data/raw/`

Contiene el dataset original y debe mantenerse sin modificar para conservar trazabilidad.

### `data/processed/`

Contiene el dataset depurado generado por el proceso reproducible.

Actualmente el dataset conserva las columnas `cholesterol` y `gluc`, aunque no se utilizan en los modelos iniciales.

### `notebooks/eda/`

Contiene los notebooks utilizados para comprender el dataset, analizar distribuciones, detectar problemas de calidad y justificar criterios de depuración.

Los notebooks de EDA son evidencia del proceso exploratorio, no el mecanismo principal de producción de datos.

### `notebooks/modeling/`

Contiene notebooks experimentales de modelos.

Actualmente:

- Regresión logística.
- Árbol de decisión.

Sirven para explorar algoritmos, probar configuraciones, visualizar resultados y analizar interpretabilidad.

Las ejecuciones reproducibles deben realizarse mediante el pipeline de `ml/`.

## 4. `ml/prepare.py`

Es responsable de convertir el dataset original en el dataset depurado.

Flujo:

```text
CSV original
    ↓
Validación de rangos
    ↓
Filtrado de registros
    ↓
Creación de age_years
    ↓
Creación de bmi
    ↓
CSV depurado
```

Actualmente se aplican criterios como:

- `height`: 120–220.
- `weight`: 30–200.
- `ap_hi`: 70–250.
- `ap_lo`: 40–150.
- `ap_hi > ap_lo`.

También se crean:

```text
age_years = age / 365.25
```

y:

```text
bmi = weight / ((height / 100)²)
```

Los scripts de entrenamiento no deben volver a repetir esta depuración.

## 5. `ml/common.py`

Centraliza los componentes comunes a los modelos.

### Variable objetivo

```text
cardio
```

### Variables utilizadas

```text
gender
height
weight
ap_hi
ap_lo
smoke
alco
active
age_years
bmi
```

### Variables excluidas

```text
id
age
cholesterol
gluc
```

Las columnas `cholesterol` y `gluc` se excluyen del entrenamiento porque su codificación categórica todavía no está suficientemente documentada.

### Particiones

La división actual es:

```text
70 % entrenamiento
15 % validación
15 % prueba
```

Con:

```text
random_state = 42
```

y estratificación por la variable objetivo.

El conjunto de prueba debe mantenerse reservado hasta la evaluación final del candidato.

## 6. Preprocesamiento específico por algoritmo

### Regresión logística

Actualmente:

- Variables continuas → `StandardScaler`.
- `gender` → `OneHotEncoder`.
- Variables binarias → sin transformación.

### Árbol de decisión

Actualmente:

- Variables continuas → sin escalado.
- `gender` → `OneHotEncoder`.
- Variables binarias → sin transformación.

No todos los modelos deben recibir exactamente el mismo preprocesamiento.

## 7. `ml/configs/`

Cada modelo debe tener una configuración explícita.

Ejemplo de regresión logística:

```yaml
model_type: logistic_regression
model_params:
  max_iter: 1000
  random_state: 42
threshold: 0.5
```

Ejemplo de árbol de decisión:

```yaml
model_type: decision_tree
model_params:
  max_depth: 5
  min_samples_leaf: 50
  random_state: 42
threshold: 0.5
```

Esto permite separar el código del pipeline de la configuración experimental.

## 8. `ml/train.py`

Es el punto principal de entrenamiento.

Flujo:

```text
Leer configuración YAML
        ↓
Cargar CSV depurado
        ↓
Seleccionar X e y
        ↓
Crear train / validation / test
        ↓
Construir pipeline específico
        ↓
Entrenar con train
        ↓
Evaluar con validation
        ↓
Registrar ejecución en MLflow
```

El conjunto de prueba no se utiliza en esta etapa.

Cada ejecución registra:

- Tipo de modelo.
- Hiperparámetros.
- Umbral.
- Random state.
- Número de registros de entrenamiento.
- Número de registros de validación.
- Hash SHA-256 del dataset.
- Commit de Git.
- Métricas.
- Artefactos.

## 9. `ml/evaluate.py`

Centraliza las métricas comunes.

Actualmente calcula:

- Accuracy.
- Precision.
- Recall.
- Specificity.
- F1-score.
- ROC-AUC.
- Brier score.
- TN.
- FP.
- FN.
- TP.

Más adelante se recomienda agregar:

- Curva de calibración.
- Métricas por subgrupos.
- Medidas de variabilidad o intervalos de confianza cuando corresponda.

## 10. MLflow

MLflow funciona como registro de experimentos.

Cada ejecución debe representar un experimento identificable.

Ejemplo:

```text
Run 001
Modelo: Logistic Regression
C: 1.0
Threshold: 0.5
ROC-AUC: ...
Brier: ...
Dataset hash: ...
Git commit: ...
```

MLflow evita depender de memoria, capturas de pantalla o celdas ejecutadas manualmente.

## 11. GitHub y MLflow cumplen funciones distintas

### GitHub

Versiona:

- Código.
- Configuraciones.
- Notebooks.
- Documentación.
- Workflows.
- Pruebas.

### MLflow

Registra:

- Ejecuciones.
- Parámetros.
- Métricas.
- Artefactos.
- Modelos entrenados.
- Resultados experimentales.

GitHub responde:

```text
¿Qué cambió en el código?
```

MLflow responde:

```text
¿Qué ocurrió cuando se ejecutó ese código?
```

# 12. Cómo incorporar un nuevo modelo

Supongamos que el siguiente modelo será Random Forest.

## Paso 1. Explorar el algoritmo en un notebook

Crear:

```text
notebooks/modeling/random_forest.ipynb
```

El notebook puede utilizarse para comprender el algoritmo, probar parámetros, visualizar resultados y revisar importancia de variables.

## Paso 2. Mantener las mismas condiciones de comparación

Para una comparación válida, el nuevo modelo debe utilizar inicialmente:

- El mismo dataset depurado.
- La misma variable objetivo.
- Las mismas variables de entrada.
- Las mismas particiones.
- La misma semilla.
- Las mismas métricas.

Si se cambia cualquiera de estas condiciones, debe registrarse como un experimento diferente.

## Paso 3. Determinar el preprocesamiento específico

Preguntar:

```text
¿Este algoritmo necesita escalado?
¿Necesita codificación categórica?
¿Admite valores faltantes?
¿Requiere algún preprocesamiento especial?
```

Por ejemplo, Random Forest normalmente no requiere `StandardScaler`.

## Paso 4. Agregar el algoritmo a `make_pipeline`

En `ml/common.py` se agregaría conceptualmente:

```python
elif kind == "random_forest":
    ...
```

En esta sección se debe:

1. Importar el estimador.
2. Definir el preprocesamiento.
3. Crear el modelo usando los parámetros recibidos desde YAML.

Los hiperparámetros experimentales deben permanecer en la configuración cuando sea posible.

## Paso 5. Crear su archivo YAML

Ejemplo conceptual:

```text
ml/configs/random_forest.yaml
```

Contenido ilustrativo:

```yaml
model_type: random_forest
model_params:
  n_estimators: 200
  max_depth: 8
  random_state: 42
threshold: 0.5
```

Estos valores son ejemplos; los parámetros reales deben determinarse mediante experimentación.

## Paso 6. Revisar los artefactos específicos

`train.py` actualmente genera:

- Regresión logística → `coefficients.csv`.
- Árbol de decisión → `feature_importances.csv` y visualización del árbol.

Para Random Forest tendría sentido generar `feature_importances.csv`, pero no necesariamente representar todos los árboles.

## Paso 7. Agregar una prueba automatizada

En:

```text
tests/test_training.py
```

debe incorporarse el nuevo modelo al conjunto de algoritmos probados.

La prueba debe verificar al menos que:

- El pipeline puede construirse.
- El modelo puede entrenarse.
- Puede producir probabilidades.
- `evaluate()` puede calcular las métricas.

## Paso 8. Ejecutar pytest

```powershell
python -m pytest -q tests
```

Todos los tests deben pasar.

## Paso 9. Ejecutar el nuevo modelo

Ejemplo:

```powershell
python -m ml.train --config ml/configs/random_forest.yaml
```

La ejecución quedará registrada en MLflow.

## Paso 10. Comparar en MLflow

Comparar el nuevo modelo contra los anteriores.

No seleccionar un modelo únicamente por accuracy.

Para PULSO deben considerarse conjuntamente:

- ROC-AUC.
- Sensibilidad.
- Especificidad.
- Precision.
- F1.
- Brier score.
- Calibración.
- Estabilidad.
- Interpretabilidad.
- Costo computacional.

# 13. Ajuste de hiperparámetros

Una vez que un algoritmo base funciona, pueden probarse diferentes configuraciones.

Ejemplo:

```text
Run 1:
max_depth = 5

Run 2:
max_depth = 8

Run 3:
max_depth = 12
```

Cada configuración debe ser una ejecución separada de MLflow.

La selección debe hacerse utilizando entrenamiento y validación, o validación cruzada sobre entrenamiento.

No debe utilizarse repetidamente el conjunto de prueba para elegir hiperparámetros.

## 14. Umbral de clasificación

Actualmente:

```text
threshold = 0.5
```

El umbral debe considerarse como parte de la configuración del experimento.

Puede cambiar entre modelos si se selecciona utilizando validación.

Cambiar el threshold no equivale a calibrar probabilidades.

## 15. Calibración

PULSO pretende presentar probabilidades.

Por esta razón, antes de seleccionar el modelo final deben analizarse:

- Brier score.
- Curvas de calibración.
- Diferencia entre probabilidad predicha y frecuencia observada.

Un modelo puede discriminar bien y estar mal calibrado.

## 16. Evaluación final con test

Durante el desarrollo:

```text
TRAIN
↓
Entrenamiento

VALIDATION
↓
Comparación y selección
```

El conjunto de prueba debe permanecer reservado.

Cuando se selecciona una configuración candidata:

```text
Modelo seleccionado
        ↓
Evaluación final
        ↓
TEST
```

Después de consultar test, no debería continuarse ajustando repetidamente el modelo usando sus resultados como guía.

## 17. Versionamiento del modelo candidato

Cuando exista un modelo candidato deben conservarse juntos:

- Modelo serializado.
- Preprocesamiento.
- Lista y orden de variables.
- Hiperparámetros.
- Threshold.
- Métricas.
- Dataset hash.
- Commit de Git.
- Versiones de dependencias.
- Fecha.
- Limitaciones.

Ejemplo conceptual:

```text
pulso-cardio-v1.0.0
```

Evitar nombres ambiguos como:

```text
modelo_final_final2.pkl
```

## 18. Integración futura con SHAP

SHAP debe aplicarse sobre el modelo seleccionado.

La versión de SHAP y la versión del modelo deben permanecer relacionadas.

Las variables mostradas por SHAP deben corresponder exactamente con las que utiliza el pipeline.

## 19. Integración futura con simulaciones

Las simulaciones deben utilizar:

```text
mismo modelo
+
mismo preprocesamiento
+
mismo orden de variables
```

El usuario modificará variables permitidas y el pipeline volverá a ejecutar la predicción.

## 20. Qué no hacer

Evitar:

- Entrenar directamente desde el CSV original.
- Repetir la depuración dentro de cada notebook.
- Crear particiones diferentes para cada algoritmo sin justificación.
- Usar test para seleccionar el mejor modelo.
- Guardar únicamente capturas de métricas.
- Sobrescribir un modelo sin dejar trazabilidad.
- Incluir una nueva característica sin documentarlo.

# 21. Flujo completo MLOps de PULSO

```text
DATASET ORIGINAL
        ↓
EDA
        ↓
prepare.py
        ↓
DATASET DEPURADO VERSIONADO
        ↓
common.py
        ↓
TRAIN / VALIDATION / TEST
        ↓
        ├── Logistic Regression
        ├── Decision Tree
        ├── Random Forest
        └── futuros modelos
        ↓
evaluate.py
        ↓
MLFLOW
        ↓
Comparación de experimentos
        ↓
Ajuste de hiperparámetros
        ↓
Análisis de calibración
        ↓
Selección de candidato
        ↓
EVALUACIÓN FINAL EN TEST
        ↓
VERSIONAMIENTO DEL MODELO
        ↓
SHAP
        ↓
SIMULACIÓN
        ↓
FASTAPI
        ↓
PULSO WEB
```

# 22. Proceso recomendado para los próximos modelos

Para cada algoritmo nuevo:

1. Crear notebook exploratorio.
2. Utilizar el CSV depurado.
3. Mantener inicialmente las mismas variables.
4. Mantener las mismas particiones.
5. Definir el preprocesamiento necesario.
6. Incorporar el estimador a `make_pipeline`.
7. Crear un YAML.
8. Añadir una prueba.
9. Ejecutar `pytest`.
10. Entrenar mediante `ml.train`.
11. Registrar en MLflow.
12. Comparar con los modelos existentes.
13. Ajustar hiperparámetros utilizando validación.
14. Analizar calibración.
15. Solo después seleccionar un candidato.
16. Evaluar finalmente con test.
17. Versionar el modelo aprobado.

## 23. Estado actual

Actualmente PULSO cuenta con:

- Dataset original versionado.
- Dataset depurado.
- EDA en tres notebooks.
- Script reproducible de depuración.
- Notebook de regresión logística.
- Notebook de árbol de decisión.
- Pipeline compartido de entrenamiento.
- Configuración independiente de ambos modelos.
- Evaluación compartida.
- Pruebas automatizadas.
- Integración con MLflow.
- Workflow de GitHub Actions para el componente ML.

Los siguientes pasos naturales son:

1. Ejecutar ambos modelos con el CSV depurado real.
2. Confirmar que las métricas coinciden razonablemente con los notebooks originales.
3. Registrar ambos experimentos en MLflow.
4. Incorporar nuevos algoritmos.
5. Realizar ajuste controlado de hiperparámetros.
6. Incorporar análisis de calibración.
7. Seleccionar un candidato.
8. Evaluar el candidato en test.
9. Versionar el modelo.
10. Integrar SHAP y posteriormente la API.

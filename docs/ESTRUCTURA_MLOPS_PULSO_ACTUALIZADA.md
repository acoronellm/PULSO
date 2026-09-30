# Estructura MLOps de PULSO y guía para tuning, threshold y nuevos modelos

## 1. Objetivo

Este documento describe la estructura actual del componente MLOps de PULSO y cómo continuar incorporando modelos, tuning de hiperparámetros, selección de threshold, pruebas automatizadas y seguimiento de experimentos sin perder reproducibilidad, comparabilidad ni trazabilidad.

El objetivo es que para cada modelo se pueda responder:

- ¿Qué dataset utilizó?
- ¿Qué versión del dataset utilizó?
- ¿Qué variables utilizó?
- ¿Qué variables quedaron excluidas?
- ¿Qué versión del código lo generó?
- ¿Qué hiperparámetros utilizó?
- ¿Cómo se seleccionaron esos hiperparámetros?
- ¿Qué threshold utiliza?
- ¿Cómo se seleccionó el threshold?
- ¿Qué métricas obtuvo?
- ¿Qué preprocesamiento recibió?
- ¿Qué ejecución de MLflow corresponde al experimento?
- ¿Puede reproducirse?

---

## 2. Estado actual del flujo MLOps

Actualmente el flujo contempla:

- Dataset original.
- Dataset depurado reproducible.
- Regresión logística.
- Árbol de decisión.
- Random Forest.
- XGBoost.
- Configuraciones independientes por modelo.
- Pipeline de entrenamiento común.
- Evaluación común.
- MLflow para tracking.
- Pruebas automatizadas.
- GitHub Actions para CI.
- `GridSearchCV` para tuning.
- Selección reproducible de threshold.
- Espacios de búsqueda YAML.
- Configuraciones de candidatos tuned.
- Barra de progreso y ETA aproximada durante tuning.

Las columnas `cholesterol` y `gluc` permanecen en el CSV depurado, pero actualmente continúan excluidas del feature set utilizado por los modelos.

---

## 3. Estructura general recomendada

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
│   └── modeling/
│       ├── logistic_regression.ipynb
│       ├── decision_tree.ipynb
│       ├── random_forest.ipynb
│       └── xgboost.ipynb
│
├── ml/
│   ├── __init__.py
│   ├── prepare.py
│   ├── common.py
│   ├── evaluate.py
│   ├── train.py
│   ├── tune.py
│   ├── threshold.py
│   ├── select_threshold.py
│   │
│   └── configs/
│       ├── logistic_regression.yaml
│       ├── decision_tree.yaml
│       ├── random_forest.yaml
│       ├── xgboost.yaml
│       │
│       ├── search_spaces/
│       │   ├── logistic_regression.yaml
│       │   ├── decision_tree.yaml
│       │   ├── random_forest.yaml
│       │   └── xgboost.yaml
│       │
│       └── candidates/
│           ├── logistic_regression_tuned.yaml
│           ├── decision_tree_tuned.yaml
│           ├── random_forest_tuned.yaml
│           └── xgboost_tuned.yaml
│
├── tests/
│   └── test_training.py
│
├── artifacts/
│   └── tuning/
│
├── .github/
│   └── workflows/
│       └── ml-training-ci.yml
│
├── requirements-ml.txt
├── .gitignore
└── README.md
```

`artifacts/`, `mlflow.db`, `mlruns/` y `mlartifacts/` deben mantenerse fuera de Git cuando correspondan a resultados locales.

---

## 4. Dataset y preparación

### `data/raw/`

Contiene el dataset original.

No debe modificarse manualmente.

### `data/processed/`

Contiene el dataset depurado generado por el proceso reproducible.

Archivo esperado:

```text
data/processed/cardio_clean_v1.csv
```

### `ml/prepare.py`

Es el único componente responsable de reproducir el dataset depurado.

Actualmente incluye criterios como:

- `height` entre 120 y 220.
- `weight` entre 30 y 200.
- `ap_hi` entre 70 y 250.
- `ap_lo` entre 40 y 150.
- `ap_hi > ap_lo`.

También genera:

```text
age_years = age / 365.25
```

y:

```text
bmi = weight / ((height / 100)²)
```

Los módulos de entrenamiento, tuning y threshold no deben repetir esta limpieza.

---

## 5. Contrato de variables

### Target

```text
cardio
```

### Features actuales

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

`cholesterol` y `gluc` se conservan para trazabilidad y posible experimentación futura, pero no deben incorporarse al feature set oficial mientras no se apruebe explícitamente ese cambio.

---

## 6. Particiones

La división compartida es:

```text
70 % Train
15 % Validation
15 % Test
```

Con:

```text
random_state = 42
```

y estratificación por `cardio`.

La función común de división debe mantenerse en `ml/common.py`.

### Función de cada partición

```text
Train
→ entrenamiento
→ GridSearchCV
→ validación cruzada interna

Validation
→ comparación posterior
→ selección de threshold

Test
→ evaluación final del candidato seleccionado
```

Test no participa en tuning ni selección de threshold.

---

## 7. Modelos integrados

Actualmente el pipeline común soporta:

```text
logistic_regression
decision_tree
random_forest
xgboost
```

Cada algoritmo utiliza el preprocesamiento que corresponda.

### Regresión logística

- Escalado de variables continuas.
- Codificación de `gender`.
- Binarias en passthrough.

### Decision Tree

- Sin escalado de continuas.
- Codificación compatible con el pipeline.
- Binarias en passthrough.

### Random Forest

- Preprocesamiento basado en árboles.
- No requiere `StandardScaler`.

### XGBoost

- Preprocesamiento basado en árboles.
- No requiere `StandardScaler`.

No se debe obligar a todos los algoritmos a utilizar el mismo preprocesamiento si el algoritmo no lo necesita.

---

## 8. Configuraciones baseline

Los archivos:

```text
ml/configs/logistic_regression.yaml
ml/configs/decision_tree.yaml
ml/configs/random_forest.yaml
ml/configs/xgboost.yaml
```

representan configuraciones concretas.

Ejemplo conceptual:

```yaml
model_type: random_forest

model_params:
  n_estimators: 200
  random_state: 42
  n_jobs: -1

threshold: 0.5
```

Estos archivos no deben confundirse con los espacios de búsqueda.

---

## 9. `ml/train.py`

`train.py` entrena una configuración concreta.

Flujo:

```text
Leer YAML
    ↓
Cargar dataset depurado
    ↓
Aplicar feature contract
    ↓
Crear Train / Validation / Test
    ↓
Construir pipeline
    ↓
Entrenar sobre Train
    ↓
Evaluar sobre Validation
    ↓
Registrar en MLflow
```

Test continúa reservado.

---

## 10. `ml/evaluate.py`

Centraliza las métricas.

Actualmente debe calcular al menos:

- Accuracy.
- Precision.
- Recall.
- Specificity.
- F1.
- ROC-AUC.
- Brier score.
- TN.
- FP.
- FN.
- TP.

El Brier score es importante porque PULSO trabaja con probabilidades.

---

# 11. Tuning con GridSearchCV

## 11.1 Objetivo

`GridSearchCV` busca hiperparámetros dentro de Train.

No utiliza Validation ni Test.

Flujo:

```text
Train
  ↓
GridSearchCV
  ↓
CV interna
  ↓
Mejores hiperparámetros
```

Actualmente:

```text
scoring = roc_auc
cv = 5
```

salvo que un YAML indique otra configuración.

---

## 11.2 Espacios de búsqueda

Los search spaces se almacenan en:

```text
ml/configs/search_spaces/
```

Ejemplo conceptual:

```yaml
model_type: random_forest

scoring: roc_auc
cv: 5

param_grid:
  model__n_estimators:
    - 200
    - 400

  model__max_depth:
    - 5
    - 10
    - null
```

La sintaxis:

```text
model__parametro
```

es necesaria porque el estimador se encuentra dentro del `Pipeline` bajo el paso llamado `model`.

---

## 11.3 `ml/tune.py`

Responsabilidades:

1. Cargar el YAML del espacio de búsqueda.
2. Cargar el YAML baseline.
3. Cargar el CSV depurado.
4. Crear las particiones.
5. Usar exclusivamente Train.
6. Ejecutar `GridSearchCV`.
7. Registrar resultados en MLflow.
8. Guardar `cv_results_`.
9. Mostrar progreso y ETA aproximada.

No debe usar Validation para seleccionar hiperparámetros.

---

## 11.4 Progreso del tuning

`tune.py` utiliza `ParameterGrid` para calcular:

```text
n_candidates
total_fits = n_candidates × cv
```

y una barra `tqdm` conectada a `joblib`.

Ejemplo esperado:

```text
GridSearch random_forest: 42%|██████████▌ | 304/720 [05:41<07:48, 1.13s/fit]
```

Esto permite visualizar:

- porcentaje;
- fits completados;
- fits totales;
- tiempo transcurrido;
- ETA aproximada;
- velocidad.

La ETA es orientativa. Algunos hiperparámetros tardan más que otros.

---

## 11.5 Información registrada en MLflow

Cada tuning debe registrar:

```text
model_type
search_method
scoring
cv
dataset_sha256
n_candidates
total_fits
best_cv_score
best_params
gridsearch_elapsed_seconds
mean_fit_time_seconds
```

Además debe guardar:

```text
cv_results.csv
```

como artefacto.

---

# 12. Configuración candidate

El resultado de GridSearchCV no debe sobrescribir inmediatamente el baseline.

Se debe conservar:

```text
baseline
vs
candidate tuned
```

Ejemplo:

```text
ml/configs/candidates/random_forest_tuned.yaml
```

El candidate contiene los mejores hiperparámetros encontrados.

Inicialmente puede mantener:

```yaml
threshold: 0.5
```

hasta ejecutar la etapa específica de threshold.

---

# 13. Selección de threshold

## 13.1 Separación respecto al tuning

Tuning y threshold responden preguntas distintas.

```text
GridSearchCV
→ ¿qué hiperparámetros funcionan mejor?

Threshold selection
→ ¿en qué probabilidad se convierte la salida en clase 1?
```

Orden correcto:

```text
GridSearchCV
    ↓
modelo tuned
    ↓
Validation probabilities
    ↓
threshold search
```

---

## 13.2 `ml/threshold.py`

Contiene la lógica común de búsqueda.

La regla actual es:

```text
Threshold mínimo: 0.20
Threshold máximo: 0.60
Step: 0.01

Restricción:
Recall >= 0.80

Entre los elegibles:
1. maximizar Precision
2. usar F1 como desempate
```

La función no debe conocer Train, Validation o Test.

Solo debe recibir:

```text
y_true
probabilities
```

y devolver:

```text
selected
results
```

---

## 13.3 `ml/select_threshold.py`

Responsabilidades:

1. Cargar candidate YAML.
2. Cargar CSV depurado.
3. Crear las mismas particiones.
4. Entrenar candidate sobre Train.
5. Obtener `predict_proba` sobre Validation.
6. Ejecutar `search_threshold`.
7. Mostrar el threshold seleccionado.
8. Registrar el resultado cuando corresponda.

No debe consultar Test.

---

## 13.4 Ejemplo de ejecución

```powershell
python -m ml.select_threshold --config ml/configs/candidates/logistic_regression_tuned.yaml
```

Resultado esperado:

```text
Threshold seleccionado:

threshold      ...
accuracy       ...
precision      ...
recall         ...
specificity    ...
f1             ...
```

Debe verificarse:

```text
recall >= 0.80
```

si existe al menos un threshold elegible dentro del rango definido.

---

# 14. Pruebas automatizadas

`tests/test_training.py` debe cubrir el pipeline sin ejecutar búsquedas pesadas.

Actualmente las pruebas deben comprobar:

### Contrato de features

- `cholesterol` fuera de X.
- `gluc` fuera de X.
- `id` fuera de X.
- `age` fuera de X.

### Particiones

- 70/15/15.
- Sin superposición.
- Reproducibles.

### Modelos

Debe probar:

- Logistic Regression.
- Decision Tree.
- Random Forest.
- XGBoost.

Se corrigió el caso anterior donde Random Forest no estaba siendo probado correctamente.

### Evaluación

Debe comprobar que existan las métricas comunes y que:

```text
0 <= ROC-AUC <= 1
0 <= Brier <= 1
```

### GridSearchCV

Debe utilizar un grid mínimo, por ejemplo:

```python
{
    "model__max_depth": [3, 5]
}
```

El objetivo del test es verificar funcionamiento, no optimizar un modelo real.

### Threshold

Debe comprobar:

- que el threshold seleccionado cumple el recall mínimo;
- que se encuentra dentro del rango esperado;
- que se generan resultados;
- que se produce un error controlado si ningún threshold cumple la restricción.

---

# 15. GitHub Actions

CI debe ejecutar:

```powershell
python -m pytest -q tests
```

No debe ejecutar GridSearchCV completo.

Razón:

```text
CI
→ verificación funcional

Tuning real
→ experimento de ML
```

Los grids completos pueden representar cientos o miles de fits y no deben ejecutarse en cada PR.

---

# 16. MLflow y GitHub

## GitHub

Versiona:

- código;
- configuraciones;
- notebooks;
- tests;
- documentación;
- workflows.

## MLflow

Registra:

- ejecuciones;
- parámetros;
- mejores hiperparámetros;
- métricas;
- tiempo de búsqueda;
- dataset hash;
- artefactos;
- resultados de tuning.

GitHub responde:

```text
¿Qué cambió?
```

MLflow responde:

```text
¿Qué ocurrió cuando ejecutamos esa versión?
```

---

# 17. Flujo MLOps actualizado

```text
DATASET ORIGINAL
        ↓
prepare.py
        ↓
DATASET DEPURADO
        ↓
FEATURE CONTRACT
        ↓
TRAIN / VALIDATION / TEST
        ↓
────────────────────────
TRAIN
────────────────────────
        ↓
Baseline
        ↓
GridSearchCV
        ↓
Best Params
        ↓
Candidate YAML
        ↓
────────────────────────
VALIDATION
────────────────────────
        ↓
predict_proba
        ↓
Threshold Search
        ↓
Recall >= 0.80
        ↓
Max Precision
        ↓
F1 tie-break
        ↓
Candidate final
        ↓
Calibración
        ↓
Comparación entre modelos
        ↓
Selección de un candidato
        ↓
────────────────────────
TEST
────────────────────────
        ↓
Evaluación final
        ↓
Versionamiento
        ↓
SHAP
        ↓
Simulaciones
        ↓
FastAPI
        ↓
PULSO Web
```

---

# 18. Cómo integrar un modelo nuevo a partir de ahora

Para un modelo nuevo:

1. Crear notebook exploratorio.
2. Usar el CSV depurado.
3. Mantener el feature contract oficial.
4. Mantener las mismas particiones.
5. Implementar el estimador en `make_pipeline`.
6. Crear config baseline.
7. Agregar test sintético del modelo.
8. Ejecutar `pytest`.
9. Entrenar baseline.
10. Crear search space.
11. Ejecutar `ml.tune`.
12. Crear candidate tuned.
13. Ejecutar `ml.select_threshold`.
14. Registrar resultados en MLflow.
15. Comparar contra otros candidatos.
16. Analizar calibración.
17. Elegir candidato.
18. Solo entonces utilizar Test.
19. Versionar.
20. Integrar SHAP/API.

---

# 19. Comandos principales

### Baseline

```powershell
python -m ml.train --config ml/configs/logistic_regression.yaml
```

### Tuning

```powershell
python -m ml.tune --search-config ml/configs/search_spaces/logistic_regression.yaml --base-config ml/configs/logistic_regression.yaml
```

### Threshold

```powershell
python -m ml.select_threshold --config ml/configs/candidates/logistic_regression_tuned.yaml
```

### Tests

```powershell
python -m pytest -q tests
```

### MLflow

```powershell
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

---

# 20. Estado de Test

Durante tuning y threshold:

```text
TEST USED = FALSE
```

Test debe permanecer reservado hasta que el equipo haya seleccionado el candidato que va a recibir la evaluación final.

---

# 21. Siguientes mejoras recomendadas

Después de estabilizar tuning + threshold:

1. Generar candidate YAML automáticamente desde `best_params_`.
2. Registrar threshold search completo como artefacto.
3. Agregar curva de calibración.
4. Comparar probabilidades calibradas/no calibradas.
5. Implementar evaluación final de Test como comando separado.
6. Versionar el modelo aprobado.
7. Integrar SHAP.
8. Integrar simulaciones.
9. Exponer el modelo mediante FastAPI.

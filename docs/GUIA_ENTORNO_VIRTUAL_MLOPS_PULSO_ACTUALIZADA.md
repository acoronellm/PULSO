# Guía de entorno virtual para PULSO: pruebas, tuning y threshold

## 1. Objetivo

Este documento explica cómo crear, configurar, activar y reutilizar el entorno virtual de Python de PULSO para:

- ejecutar pruebas automatizadas;
- entrenar modelos baseline;
- ejecutar GridSearchCV;
- visualizar el progreso del tuning;
- seleccionar threshold;
- consultar experimentos en MLflow.

Se utiliza un entorno virtual Python llamado:

```text
.venv
```

No es una máquina virtual completa. Es un entorno aislado de dependencias para PULSO.

---

## 2. Requisitos previos

Verificar:

```powershell
python --version
```

```powershell
git --version
```

Trabajar desde la raíz:

```text
PULSO/
├── data/
├── ml/
├── tests/
├── requirements-ml.txt
└── README.md
```

---

# 3. Primera instalación

## 3.1 Crear `.venv`

Desde la raíz:

```powershell
python -m venv .venv
```

---

## 3.2 Activar

En PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Debe aparecer:

```text
(.venv) PS C:\...\PULSO>
```

---

## 3.3 Instalar dependencias

```powershell
python -m pip install -r requirements-ml.txt
```

El entorno debe incluir, entre otras:

- pandas;
- NumPy;
- scikit-learn;
- MLflow;
- PyYAML;
- joblib;
- matplotlib;
- pytest;
- XGBoost;
- tqdm.

`tqdm` se utiliza para mostrar progreso y ETA aproximada durante GridSearchCV.

Si todavía no está en `requirements-ml.txt`, agregar:

```text
tqdm>=4.66,<5
```

y ejecutar de nuevo:

```powershell
python -m pip install -r requirements-ml.txt
```

---

# 4. Si PowerShell bloquea la activación

Puede utilizarse directamente el Python del entorno:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

O:

```powershell
.\.venv\Scripts\python.exe -m ml.tune --help
```

---

# 5. Verificar el entorno antes de trabajar

Con `.venv` activo:

```powershell
python --version
```

```powershell
python -m pip --version
```

Opcionalmente:

```powershell
python -c "import sklearn, mlflow, xgboost, tqdm; print('Dependencias ML OK')"
```

---

# 6. Verificar que los módulos nuevos carguen

Ejecutar:

```powershell
python -c "from ml.threshold import search_threshold; print('threshold OK')"
```

```powershell
python -c "from ml.tune import run_tuning; print('tune OK')"
```

```powershell
python -c "from ml.select_threshold import run_threshold_selection; print('select_threshold OK')"
```

Si los tres terminan sin traceback, las importaciones principales están correctas.

---

# 7. Ejecutar pruebas automatizadas

```powershell
python -m pytest -q tests
```

Las pruebas deben cubrir:

- contrato de features;
- exclusión de `cholesterol` y `gluc`;
- particiones 70/15/15;
- reproducibilidad;
- Logistic Regression;
- Decision Tree;
- Random Forest;
- XGBoost;
- métricas;
- GridSearchCV mínimo;
- threshold;
- error controlado si ningún threshold cumple el recall.

Importante:

```text
pytest usa datos sintéticos
```

No valida el rendimiento real del modelo.

---

# 8. Qué hacer si pytest dice `no tests ran`

Verificar:

```powershell
pwd
```

```powershell
dir
```

```powershell
dir tests
```

Debe existir:

```text
tests/test_training.py
```

También verificar:

```powershell
git branch --show-current
```

porque puede haberse cambiado a una rama donde el archivo todavía no exista.

---

# 9. Entrenamiento baseline

Ejemplo Logistic Regression:

```powershell
python -m ml.train --config ml/configs/logistic_regression.yaml
```

Decision Tree:

```powershell
python -m ml.train --config ml/configs/decision_tree.yaml
```

Random Forest:

```powershell
python -m ml.train --config ml/configs/random_forest.yaml
```

XGBoost:

```powershell
python -m ml.train --config ml/configs/xgboost.yaml
```

Estos comandos utilizan por defecto:

```text
data/processed/cardio_clean_v1.csv
```

---

# 10. Ejecutar GridSearchCV

## 10.1 Logistic Regression

```powershell
python -m ml.tune --search-config ml/configs/search_spaces/logistic_regression.yaml --base-config ml/configs/logistic_regression.yaml
```

## 10.2 Decision Tree

```powershell
python -m ml.tune --search-config ml/configs/search_spaces/decision_tree.yaml --base-config ml/configs/decision_tree.yaml
```

## 10.3 Random Forest

```powershell
python -m ml.tune --search-config ml/configs/search_spaces/random_forest.yaml --base-config ml/configs/random_forest.yaml
```

## 10.4 XGBoost

```powershell
python -m ml.tune --search-config ml/configs/search_spaces/xgboost.yaml --base-config ml/configs/xgboost.yaml
```

---

# 11. Qué ocurre durante GridSearchCV

Antes de iniciar debe mostrarse algo similar a:

```text
=== GridSearchCV ===
Modelo: random_forest
Configuraciones: 144
Folds: 5
Entrenamientos totales: 720
====================
```

Después aparece la barra de progreso:

```text
GridSearch random_forest: 42%|██████████▌ | 304/720 [05:41<07:48, 1.13s/fit]
```

Interpretación:

```text
42 %
→ porcentaje completado

304/720
→ fits terminados / fits totales

05:41
→ tiempo transcurrido

<07:48
→ ETA aproximada

1.13s/fit
→ velocidad aproximada
```

La ETA puede cambiar porque algunas combinaciones tardan más que otras.

---

# 12. Qué hacer cuando termina GridSearchCV

Al finalizar debe aparecer:

```text
GridSearchCV completado.
Tiempo total: ...
Tiempo promedio por fit: ...

Mejores parámetros:
...

Best CV ROC-AUC: ...
```

También debe existir un archivo similar a:

```text
artifacts/tuning/logistic_regression_cv_results.csv
```

y una ejecución en:

```text
PULSO-model-tuning
```

dentro de MLflow.

---

# 13. Crear candidate YAML

Después del tuning, crear:

```text
ml/configs/candidates/
```

Ejemplo:

```text
ml/configs/candidates/logistic_regression_tuned.yaml
```

El archivo debe contener los mejores parámetros obtenidos.

Ejemplo conceptual:

```yaml
model_type: logistic_regression

model_params:
  C: 1
  class_weight: null
  solver: liblinear
  l1_ratio: 1.0
  max_iter: 1000
  random_state: 42

threshold: 0.5
```

Usar exactamente los parámetros producidos por el GridSearch actual.

No copiar resultados antiguos de notebooks si el feature set o las dependencias son diferentes.

---

# 14. Seleccionar threshold

Ejecutar:

```powershell
python -m ml.select_threshold --config ml/configs/candidates/logistic_regression_tuned.yaml
```

El script:

1. carga el candidate;
2. carga el CSV depurado;
3. crea Train/Validation/Test;
4. entrena sobre Train;
5. calcula probabilidades sobre Validation;
6. busca el threshold;
7. imprime el seleccionado.

No usa Test.

---

# 15. Regla actual de threshold

```text
Rango:
0.20 a 0.60

Step:
0.01

Restricción:
Recall >= 0.80

Objetivo:
máxima Precision

Desempate:
mayor F1
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

Verificar:

```text
recall >= 0.80
```

---

# 16. Error `FileNotFoundError` en candidate

Si aparece:

```text
FileNotFoundError:
ml/configs/candidates/<modelo>_tuned.yaml
```

significa que el candidate todavía no existe.

Verificar:

```powershell
dir ml\configs\candidates
```

y crear el YAML correspondiente con los mejores parámetros.

---

# 17. Abrir MLflow

```powershell
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Abrir:

```text
http://127.0.0.1:5000
```

Experimentos esperados:

```text
PULSO-cardio-baselines
PULSO-model-tuning
```

Según la implementación, pueden existir otros experimentos adicionales.

---

# 18. Qué revisar en MLflow después del tuning

Verificar:

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

También revisar el artefacto:

```text
cv_results.csv
```

---

# 19. Orden recomendado para probar toda la integración

Utilizar este orden:

```text
1. Activar .venv
2. Verificar imports
3. Ejecutar pytest
4. Tuning Logistic Regression
5. Revisar MLflow
6. Crear Logistic candidate
7. Ejecutar threshold Logistic
8. Tuning Decision Tree
9. Crear Decision Tree candidate
10. Ejecutar threshold Decision Tree
11. Tuning Random Forest
12. Crear Random Forest candidate
13. Ejecutar threshold Random Forest
14. Tuning XGBoost
15. Crear XGBoost candidate
16. Ejecutar threshold XGBoost
17. Comparar candidatos
18. NO usar Test todavía
```

Empezar por Logistic Regression ayuda a validar la arquitectura con una búsqueda relativamente liviana.

---

# 20. Ejecución recomendada después de un `git pull`

Después de traer cambios:

```powershell
git pull
```

activar:

```powershell
.\.venv\Scripts\Activate.ps1
```

actualizar dependencias:

```powershell
python -m pip install -r requirements-ml.txt
```

y ejecutar:

```powershell
python -m pytest -q tests
```

---

# 21. No reinstalar todo cada vez

En una sesión normal:

```powershell
.\.venv\Scripts\Activate.ps1
```

y continuar.

No es necesario:

```powershell
python -m venv .venv
```

ni reinstalar dependencias todos los días.

Solo reinstalar/actualizar cuando:

- cambia `requirements-ml.txt`;
- se elimina `.venv`;
- se clona en otro equipo;
- se cambian versiones de librerías.

---

# 22. Detener MLflow

En su terminal:

```text
Ctrl + C
```

Esto no borra `mlflow.db`.

---

# 23. Salir del entorno

```powershell
deactivate
```

---

# 24. Archivos que no deben subirse

`.gitignore` debe cubrir:

```gitignore
.venv/
mlflow.db
mlflow.db-*
mlruns/
mlartifacts/
artifacts/
__pycache__/
.pytest_cache/
.env
.env.*
```

---

# 25. CI y GridSearchCV

GitHub Actions debe ejecutar:

```powershell
python -m pytest -q tests
```

No debe ejecutar tuning completo.

Las pruebas de GridSearchCV usan espacios mínimos y datos sintéticos.

Los grids completos se ejecutan localmente o en infraestructura de experimentación.

---

# 26. Flujo diario recomendado

```text
Abrir PULSO
    ↓
git pull si corresponde
    ↓
Activar .venv
    ↓
Instalar dependencias si cambiaron
    ↓
pytest
    ↓
Modificar código/config
    ↓
pytest
    ↓
Entrenar / tuning / threshold
    ↓
Revisar MLflow
    ↓
git status
    ↓
commit
    ↓
push
    ↓
Pull Request
    ↓
deactivate
```

---

# 27. Resumen de comandos

### Activar

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar/actualizar dependencias

```powershell
python -m pip install -r requirements-ml.txt
```

### Tests

```powershell
python -m pytest -q tests
```

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

### MLflow

```powershell
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

### Salir

```powershell
deactivate
```

---

# 28. Regla principal sobre Test

Mientras se trabaja en:

```text
GridSearchCV
threshold selection
comparación de candidatos
```

el conjunto Test debe permanecer sin utilizar.

Test se reserva para la evaluación final del candidato seleccionado.

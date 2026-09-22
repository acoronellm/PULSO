
# Entrenamiento reproducible de PULSO — propuesta de integración

## Alcance

Refactoriza los dos notebooks aportados. Excluye expresamente la sección `#Nuevo de pruebas` y su celda siguiente.

**No** incluye ni sustituye tu `ml/prepare.py` actual, ni los CSV, ni los notebooks originales.

**No** ejecuta el conjunto de prueba ni elige/publica un modelo final.

El registro es MLflow local por defecto.

## Antes de copiar

1. Trabaja en una rama nueva. Haz commit o stash de cualquier trabajo local previo.
2. Conserva tu `ml/prepare.py`, `data/`, `notebooks/` y `README.md` actuales; copia solamente los archivos nuevos.
3. Confirma la ruta real de tu CSV depurado. Por defecto, el comando espera `data/processed/cardio_clean_v1.csv`. Si tiene otro nombre, usa `--data ruta/al/archivo.csv`.
4. Comprueba que el CSV depurado contiene `gender,height,weight,ap_hi,ap_lo,smoke,alco,active,age_years,bmi,cardio`. Además puede conservar `id,age,cholesterol,gluc`.

## Archivos para incorporar

- `ml/__init__.py`, `ml/common.py`, `ml/train.py`, `ml/evaluate.py` y `ml/configs/*.yaml`.
- `tests/test_training.py` y `requirements-ml.txt`.
- `.github/workflows/ml-training-ci.yml`.
- Agrega las reglas de `.gitignore.mlops-example` a tu `.gitignore` existente, sin sobrescribirlo.

## Ejecución local desde la raíz del repositorio

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-ml.txt
python -m pytest -q tests

python -m ml.train --config ml/configs/logistic_regression.yaml --data data/processed/cardio_clean_v1.csv

python -m ml.train --config ml/configs/decision_tree.yaml --data data/processed/cardio_clean_v1.csv

python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Abre la URL local que muestra MLflow.

Cada comando de entrenamiento crea una ejecución con parámetros, métricas de validación, hash SHA-256 del CSV y artefactos del pipeline, CSV de coeficientes o importancias, matriz de confusión y curva ROC.

No subas `mlflow.db`, los artefactos locales ni datos sensibles a GitHub.

No cargues archivos joblib desconocidos: su deserialización puede ejecutar código.

## Qué se conserva y qué se añade

- Misma selección de 10 características, sin `id`, `age`, `cholesterol` ni `gluc`.
- Misma división estratificada 70/15/15, con semilla 42.
- Regresión logística: StandardScaler en variables continuas y OneHotEncoder en `gender`, con `max_iter=1000`.
- Árbol de decisión: variables continuas sin escalado, misma codificación de `gender`, `max_depth=5` y `min_samples_leaf=50`.
- Umbral inicial de 0,5.
- Se añaden especificidad, Brier score, registros de versión de datos, pruebas y artefactos.

La salida de `cardio=1` no se interpreta automáticamente como riesgo cardiovascular a diez años.

Si cambia el orden del CSV o la versión del dataset, no se garantiza conservar las mismas particiones.

Para reproducibilidad entre equipos, fija las versiones de las dependencias después de probarlas.

SQLite local no comparte los resultados entre integrantes. Se necesitará un servidor MLflow autorizado si el equipo requiere un registro central.

## Limitaciones

- No se modifica `prepare.py`.
- No se hace ajuste de hiperparámetros.
- No se realiza calibración ni evaluación final en test.
- No se implementa un registro de modelos aprobados.
- No se implementa el despliegue de producción.

La comparación numérica con los notebooks originales requiere ejecutar el pipeline con el CSV depurado exacto.

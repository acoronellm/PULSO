# C2 — Selección multialgoritmo por grupos de edad

Esta etapa **solo optimiza hiperparámetros**. No calibra probabilidades, no selecciona umbrales y **no accede a Test**. No modifica PULSO v1.

## Instalación

Copiar esta carpeta `c2` a `experiments/age_specialized_models/` desde la raíz de PULSO. Tener activo el entorno virtual existente con `scikit-learn`, `xgboost`, `tqdm`, `pandas` y `joblib`. Ejecutar siempre desde la raíz del repositorio.

## Entrenar un algoritmo y un rango a la vez

```powershell
python -m experiments.age_specialized_models.c2.entrenar_logistic_regression --grupo menor_50
python -m experiments.age_specialized_models.c2.entrenar_logistic_regression --grupo 50_59
python -m experiments.age_specialized_models.c2.entrenar_logistic_regression --grupo 60_64
python -m experiments.age_specialized_models.c2.entrenar_logistic_regression --grupo global
```

Cambiar `entrenar_logistic_regression` por:

- `entrenar_decision_tree`
- `entrenar_random_forest`
- `entrenar_gradient_boosting`
- `entrenar_xgboost`

Cada ejecución muestra una barra `tqdm` con ajustes completados / ajustes totales, porcentaje, velocidad y tiempo restante estimado; al terminar la búsqueda realiza un entrenamiento final con la mejor configuración.

## Resultados

`experiments/age_specialized_models/results/c2_v2/<algoritmo>/<grupo>/`:

- `cv_folds.csv`: resultados individuales de cada fold y candidato.
- `cv_candidatos.csv`: promedio y desviación del ROC-AUC entre folds.
- `resumen.json`: configuración elegida, tamaños y métricas exploratorias de Validation.
- `modelo_experimental.joblib`: artefacto para uso experimental solamente.

**No agregar los `.joblib` a Git.** Registrar en Git código, configuraciones y resúmenes pequeños. La comparativa y la selección de calibración/umbrales se harán en etapas posteriores, con controles para evitar sesgo por selección.

## Diseño

- Particiones originales de `ml.common.split_data`.
- Validación cruzada estratificada de 5 folds sobre **Train del grupo**.
- Espacios originales de `ml/configs/search_spaces` preservados como copia en `c2/search_spaces`. Regresión logística: búsqueda exhaustiva (30 candidatos); árbol, Random Forest y Gradient Boosting: muestreo reproducible de 50 combinaciones; XGBoost: 70. Se incluye explícitamente el candidato histórico de `c2/candidates` cuando no aparece en el muestreo; por ello puede haber un candidato adicional.
- Criterio de hiperparámetros: ROC-AUC medio en CV.
- Una ejecución = un algoritmo + un grupo (no hay entrenamiento monolítico).
- `global` sirve de comparación justa contra modelos especializados, con la misma familia de algoritmos.
- La columna `validation_*_exploratorio` **no** es un resultado final independiente después de escoger modelos usando Validation.

## MLOps integrado

Cada ejecución registra un run MLflow en `PULSO-C2-Age-Model-Selection` (por defecto `sqlite:///mlflow.db`, configurable mediante `MLFLOW_TRACKING_URI`), con hiperparámetros, media/desviación de ROC-AUC CV, métricas exploratorias Validation, commit, hashes SHA-256 del dataset y del artefacto, y artefactos de entrenamiento. El modelo guardado se recarga y se comprueba que reproduce probabilidades antes del registro.

El protocolo nuevo `C2_v2_original_spaces_fivefold` se guarda en `results/c2_v2`, sin sobrescribir el piloto C2 original. El programa no sobrescribe resultados anteriores para el mismo algoritmo y grupo.

`manifest.json` guarda `mlflow_run_id`, commit, hashes y los hashes de los índices de Train/Validation seleccionados. `resumen.json` contiene métricas y configuración. **Si MLflow falla, el entrenamiento no queda registrado como correcto en la trazabilidad**, aunque puede haber artefactos locales producidos. Revisar el error y reejecutar antes de aceptar los resultados.

Los artefactos `.joblib` no deben incorporarse a Git. Los resultados de ejecución y la base SQLite son locales a menos que se configure un servidor compartido. No subir `mlflow.db` ni secretos.

Pruebas de contrato en `tests/test_c2_experiments.py` y plan de incorporación al CI existente en `CI_INTEGRATION.md`. No hay pruebas de entrenamiento real ni nuevos jobs de GitHub Actions incluidos en este paquete.

## Procedencia de los espacios

Los archivos en `c2/search_spaces/` y `c2/candidates/` son copias de los YAML originales entregados para PULSO v1. El motor registra sus SHA-256 en el reporte y MLflow. La búsqueda utiliza implementaciones secuenciales de evaluación de candidatos con `StratifiedKFold` (equivalentes en selección a GridSearchCV o RandomizedSearchCV para el espacio y los candidatos elegidos); esto preserva la barra `tqdm` por fold y evita paralelismo anidado. **No se llama directamente a `GridSearchCV` o `RandomizedSearchCV`**.

Los mejores candidatos se deciden por ROC-AUC de CV en Train. No se deben escoger ganadores usando repetidamente la métrica de Validation. Para una selección comparativa final de algoritmos es necesario un protocolo de evaluación independiente.

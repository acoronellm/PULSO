# PULSO — C3: calibración de candidatos por rango de edad

C3 **no optimiza umbrales** y **no utiliza Test**. Retoma las configuraciones ganadoras del experimento C2 v2 para XGBoost y Gradient Boosting en los tres grupos etarios. Reconstruye los pipelines con `ml.common.make_pipeline` en vez de usar sus predicciones sobre Train, que no serían fuera de muestra.

## Protocolo

Para cada combinación modelo-grupo, compara `none`, `sigmoid` e `isotonic`. Utiliza **3 folds externos** para generar métricas en registros no vistos por el modelo entrenado para cada fold. En los casos calibrados, usa **3 folds internos** dentro del entrenamiento externo mediante `CalibratedClassifierCV(ensemble=False)`. Selecciona la opción de menor Brier medio de los tres folds externos. Esta comparación y selección utiliza exclusivamente Train, de acuerdo con `split_data` de PULSO.

**Limitación importante:** seleccionar la mejor opción usando los mismos resultados CV introduce optimismo en la estimación reportada para el método ganador; la cifra no es una evaluación externa independiente. Las métricas de C3 son para **selección exploratoria**, no para afirmar superioridad clínica. La posterior selección de umbrales deberá mantener separados los registros de elección y de evaluación, y cualquier afirmación confirmatoria requerirá datos nuevos no utilizados para diseñar los grupos.

## Ejecución

Desde la raíz de PULSO con `.venv`:

```powershell
python -m experiments.age_specialized_models.c3.calibrar_xgboost --grupo menor_50
python -m experiments.age_specialized_models.c3.calibrar_gradient_boosting --grupo menor_50
```

Repetir `--grupo 50_59` y `--grupo 60_64`. Son **seis ejecuciones independientes**, cada una con barra de progreso de 9 folds externos (la calibración de cada fold ajusta a su vez folds internos). No se reentrena ni modifica el modelo de producción.

Resultados: `experiments/age_specialized_models/results/c3_calibracion/<algoritmo>/<grupo>/`:
- `cv_calibracion_folds.csv`
- `cv_calibracion_resumen.csv`
- `manifest.json`
- `modelo_calibrado_experimental.joblib`

Se registran en MLflow como `PULSO-C3-Age-Calibration`. El modelo serializado es **experimental**. No versionar el `.joblib` en Git si la política del repositorio lo excluye.

## Dependencias y compatibilidad

Necesita scikit-learn con `CalibratedClassifierCV(estimator=...)`, el paquete C2 v2 y el dataset procesado original. El hash del dataset debe coincidir con C2. No sobrescribe ejecuciones previas. Ejecutar primero `python -m pytest -q tests/test_c3_calibration.py`.

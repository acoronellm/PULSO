# C5 — Comparación global y especialización por edad

## Propósito
Comparar, sobre los mismos registros de evaluación de Validation, (1) el referente global XGBoost con hiperparámetros v1 reentrenado **solo sobre Train**, (2) ese mismo modelo con cuatro políticas de umbral seleccionadas en la mitad de selección de Validation, (3) los seis modelos especializados C3, con sus umbrales previamente guardados.

**No se usa el modelo de producción ya entrenado con Train+Validation**, ni se lee Test. Los análisis siguen siendo exploratorios: Validation ya fue consultada repetidamente en B, B3 y C1–C4.

## Prerrequisitos
- Entorno virtual de PULSO con mlflow, xgboost, sklearn, joblib y dependencias del repositorio.
- `data/processed/cardio_clean_v1.csv`.
- Seis modelos y manifiestos en `results/c3_calibracion/<algoritmo>/<grupo>/`.
- Umbrales y protocolos en `results/c3_umbrales/<algoritmo>/<grupo>/`.
- Funciones existentes `ml.common` y `c3.umbrales.motor_umbrales`.

## Uso (raíz del repositorio)
```powershell
python -m pytest -v tests/test_c5_comparacion.py
python -m experiments.age_specialized_models.c5.comparar --solo-verificar
python -m experiments.age_specialized_models.c5.comparar
```

## Salida
`experiments/age_specialized_models/results/c5_comparacion/`:
- `metricas_comparadas.csv`: métricas globales y por edad para cada enfoque y política.
- `diferencias_pareadas_puntuales.csv`: diferencias de rendimiento especializado menos global (misma política y observaciones); **no son intervalos de confianza**.
- `predicciones_pareadas.csv`: predicción y etiqueta por registro; no se incluyen rasgos identificables.
- `umbrales_globales.csv`: umbrales aprendidos en selección de Validation.
- `protocolo.json`: trazabilidad y advertencias de interpretación.
- MLflow: `PULSO-C5-Global-vs-Age`.

El proceso evita sobrescribir resultados existentes. Para repetir, renombrar o respaldar la carpeta de salida.

## Discusión metodológica
- Usar la *misma política* para comparar global y especializado. La referencia global fija 0,38 se reporta aparte.
- El modelo global solo Train es un **referente experimental equivalente en hiperparámetros**, no el objeto oficial de producción.
- No seleccionar un ganador definitivo en esta Validation. Evitar presentar Test ya explorado como un conjunto ciego.
- Revisar explícitamente los resultados de discontinuidad C4.3 y los intervalos C4.1 antes de emitir recomendación de despliegue.

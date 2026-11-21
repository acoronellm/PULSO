# PULSO XGBoost v1

Versión 1 del modelo definitivo de PULSO.

## Configuración

- Modelo: XGBoost
- Calibración: none
- Threshold: 0.38
- Random state: 42
- Refit: Train + Validation
- Test reservado para evaluación final

## Archivos

- `final_model.yaml`: configuración congelada.
- `metadata.yaml`: trazabilidad del modelo, dataset y métricas.
- `pulso_xgboost.joblib`: copia oficial del modelo v1, versionada en Git.

El proceso de entrenamiento genera el artefacto en:

`artifacts/final/model/pulso_xgboost.joblib`

La copia oficial distribuida con el repositorio se encuentra en:

`models/pulso/v1/pulso_xgboost.joblib`

Ambos archivos corresponden al mismo modelo aprobado y deben conservar el SHA-256 registrado en `metadata.yaml`.

## Model Registry - PULSO

| Modelo | Versión | Estado | Threshold | ROC-AUC Test |
|---|---:|---|---:|---:|
| pulso_xgboost | v1 | final | 0.38 | 0.796757 |

La configuración, los metadatos y el artefacto oficial se almacenan en la carpeta de su respectiva versión.

## Distribución y ejecución

El artefacto oficial `pulso_xgboost.joblib` se incluye en el repositorio para facilitar la instalación y ejecución del ML Service.

Durante la construcción de Docker, `ml_service/Dockerfile` copia el modelo versionado a:

`/app/artifacts/final/model/pulso_xgboost.joblib`

El ML Service lo carga desde esa ubicación sin necesitar un volumen local con los artefactos de entrenamiento.

Para ejecutar el ML Service directamente desde Python, fuera de Docker, la ruta predeterminada continúa siendo:

`artifacts/final/model/pulso_xgboost.joblib`

La variable de entorno `PULSO_MODEL_PATH` permite seleccionar una ubicación alternativa.

## Integridad del modelo

El SHA-256 oficial es:

`142fc3debfd8a87f7bf037175a30071048ce82647357e979d2d717b7b7c434b1`

Cualquier modificación o sustitución del artefacto debe tratarse como un cambio de modelo y someterse a validación.

Los archivos Joblib solo deben cargarse desde fuentes confiables.

## Reconstrucción

El modelo puede reconstruirse mediante:

```bash
python -m ml.final_evaluate --config ml/configs/final_model.yaml
```

Este procedimiento ejecuta el entrenamiento final y genera un nuevo artefacto en `artifacts/final/model/`.

No sobrescribe automáticamente la copia oficial versionada en `models/pulso/v1/`.

La reconstrucción no garantiza por sí sola identidad binaria con el artefacto aprobado.

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
- El modelo serializado se genera en:
  `artifacts/final/model/pulso_xgboost.joblib`

# Model Registry - PULSO

| Modelo | Versión | Estado | Threshold | ROC-AUC Test |
|---|---:|---|---:|---:|
| pulso_xgboost | v1 | final | 0.38 | 0.796757 |

La configuración y metadata de cada versión se almacenan en su respectiva carpeta.

## Reconstrucción

```bash
python -m ml.final_evaluate --config ml/configs/final_model.yaml
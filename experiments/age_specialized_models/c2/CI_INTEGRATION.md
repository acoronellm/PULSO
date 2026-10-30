# Integración con CI existente

**No crear un workflow nuevo por algoritmo.** Según `GUIA_CI_CD_MLOPS_TESTING_PULSO`, corresponde extender el workflow existente `.github/workflows/ml-training-ci.yml`, después de verificar su configuración real, para ejecutar las pruebas C2:

```yaml
- name: Test contratos C2 (sin dataset real)
  run: python -m pytest -q tests/test_c2_experiments.py
```

La instalación existente de `requirements-ml.txt` debe incluir `mlflow`, `pytest`, `tqdm`, `xgboost` y las dependencias requeridas por `ml.common`. No ejecutar GridSearch completa en CI. Las búsquedas reales siguen siendo manuales/controladas en la rama experimental.

**Verificación local**: `python -m pytest -q tests/test_c2_experiments.py` y `python -m pytest -q tests`.

Este paquete no modifica el workflow original porque no se adjuntó el archivo real `.github/workflows/ml-training-ci.yml`; aplicar el snippet tras revisar su contenido, sin reemplazarlo.

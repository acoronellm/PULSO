# C3 — Umbrales especializados (PULSO)

Se evalúan cuatro políticas, **sin incluir el umbral fijo 0,38**: `recall80` (recall >= 0.80; mayor especificidad entre factibles), `balanced_accuracy`, `minimax`, `weighted_60_40`.

## Ejecución

Desde la raíz de PULSO:

```powershell
python -m pytest -q tests/test_c3_thresholds.py
python -m experiments.age_specialized_models.c3.umbrales.ejecutar_todos --dry-run
python -m experiments.age_specialized_models.c3.umbrales.ejecutar_todos
```

Alternativamente, cada combinación puede ejecutarse de manera independiente:

```powershell
python -m experiments.age_specialized_models.c3.umbrales.evaluar_xgboost --grupo menor_50
python -m experiments.age_specialized_models.c3.umbrales.evaluar_gradient_boosting --grupo 50_59
```

## Requisitos

Los seis modelos y manifiestos de `results/c3_calibracion/` deben existir. El script comprueba integridad del artefacto C3 mediante SHA-256, correspondencia del dataset y grupo. Se ejecuta con el entorno Python de PULSO, con scikit-learn, mlflow, pandas, numpy, joblib y tqdm.

Se utiliza **solo Validation**, subdividida de forma reproducible (semilla 42), estratificada por edad y clase, con selección y evaluación separadas. El conjunto Test no participa en el procedimiento. Se reutiliza el modelo C3, sin reentrenarlo. La probabilidad y métricas de calibración se calculan en evaluación; las políticas únicamente modifican la clasificación.

Artefactos: `results/c3_umbrales/<algoritmo>/<grupo>/` con `umbrales_seleccionados.csv`, `metricas_evaluacion.csv`, `curvas_seleccion.csv`, `protocolo.json`. Se registra un run por combinación en `PULSO-C3-Age-Thresholds`.

**Limitación:** Validation ya fue explorada en B, B3 y C1. Estas evaluaciones son exploratorias y no validación independiente confirmatoria. La selección posterior del algoritmo/política según estas mismas evaluaciones añade sesgo de selección. Los puntos de corte etarios pueden producir discontinuidades y deberán estudiarse antes de integrar un cambio en PULSO v1.

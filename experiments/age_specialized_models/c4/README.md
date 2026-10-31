# PULSO — C4: robustez de modelos por edad

Requiere artefactos existentes de C3 en `results/c3_calibracion` y `results/c3_umbrales`, además de `data/processed/cardio_clean_v1.csv`. No usa Test ni reentrena modelos.

Desde la raíz del repositorio:

```powershell
python -m pytest -q tests/test_c4_robustez.py
python -m experiments.age_specialized_models.c4.incertidumbre --bootstrap 1000
python -m experiments.age_specialized_models.c4.estabilidad --repeticiones 100
python -m experiments.age_specialized_models.c4.continuidad --ventana 1.0
```

Cada módulo escribe resultados independientes en `experiments/age_specialized_models/results/c4/{incertidumbre,estabilidad,continuidad}`. No sobrescribe carpetas existentes; elimina o renombra manualmente solo los resultados que desees repetir.

- **Incertidumbre**: IC Wilson del 95 % para recall y especificidad; bootstrap pareado (XGBoost menos Gradient Boosting) para sensibilidad, especificidad, BA y ROC-AUC. No son pruebas de superioridad confirmatoria; la muestra Validation ha sido explorada anteriormente.
- **Estabilidad**: 100 divisiones estratificadas de la misma Validation, reestimando umbrales con modelo fijo. No son muestras independientes y sus cuantiles no son IC poblacionales. No estima incertidumbre por reentrenamiento.
- **Continuidad**: perfiles cercanos a 50/60 años se evalúan antes/después de un corte usando distinto modelo, cambiando solo la edad a corte ±0,01 años. Los cambios son contrafactuales técnicos, no evolución clínica real. Las métricas registran tanto saltos probabilísticos como cambios de clasificación.

Los cuatro criterios son `recall80`, `balanced_accuracy`, `minimax`, `weighted_60_40`. No se incluye umbral fijo 0,38. La política `recall80` solo garantiza la condición en la muestra de selección cuando es factible; no en la evaluación.

## Consideraciones MLOps

Cada script guarda un `protocolo.json` con hash del dataset, commit Git, fecha, semilla y limitaciones. Los artefactos de origen C3 están validados mediante hashes en memoria. C4 registra una ejecución MLflow por análisis en `PULSO-C4-Age-Robustness`, incluyendo protocolos y CSV. Las pruebas de C4 todavía no están incorporadas al CI del repositorio. El informe final debe comparar con el modelo global sobre los **mismos registros** y con protocolo compatible. Test ya influyó en la definición de los rangos de edad, por lo que la conclusión actual es exploratoria.

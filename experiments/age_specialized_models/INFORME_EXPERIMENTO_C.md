# PULSO — Informe técnico del experimento C
**Versión:** 0.1 — cierre de C1 y C2; C3 y C4 pendientes  
**Fecha documental:** 30 de octubre de 2026  
**Rama experimental:** `experiment/ml-age-analysis`  
**Alcance:** análisis experimental de modelos de clasificación de la etiqueta `cardio` en el dataset PULSO; no equivale a validación clínica ni a estimación de eventos cardiovasculares futuros.

## 1. Propósito y preguntas de investigación
Investigar si modelos especializados por intervalos de edad superan a un XGBoost global de referencia. Se distinguen dos hipótesis: **C1**, el efecto aislado de entrenar XGBoost por edad con hiperparámetros comunes; **C2**, el rendimiento de cinco familias de algoritmos tras optimizar hiperparámetros dentro de cada grupo. La comparación no debe confundirse con un experimento controlado de eficacia clínica.

## 2. Dataset, particiones y alcance
- Dataset: `data/processed/cardio_clean_v1.csv` (68.610 registros depurados); variables predictoras: `gender`, `height`, `weight`, `ap_hi`, `ap_lo`, `smoke`, `alco`, `active`, `age_years`, `bmi`; etiqueta: `cardio`.
- División estratificada existente: Train **48.027**, Validation **10.291**, Test **10.292**. C1 y C2 utilizaron Train para entrenar; Test no se utilizó en sus ejecuciones según protocolos y manifiestos.
- Grupos: **menores de 50**, **50–59**, **60–64** años (el último se implementa como edad ≥60, pero el dataset disponible termina antes de los 65). No extrapolar a personas de 65 años o más.
- El diseño de los grupos se informó parcialmente con análisis previos sobre Test. Por tanto, la comparación futura no puede declararse completamente independiente de decisiones guiadas por Test.

## 3. C1 — XGBoost global frente a tres XGBoost especializados
**Diseño:** todos los modelos utilizan la configuración XGBoost v1 y la misma ingeniería de variables. El global se entrena sobre todo Train; los especializados, sobre el subconjunto etario respectivo. Validation se dividió en selección de umbrales (5.145 registros) y evaluación (5.146). Se estudiaron umbral 0,38, Balanced Accuracy y minimax.

| Grupo | n evaluación | ROC-AUC global | ROC-AUC especializado | Δ especializado − global | Brier global | Brier especializado |
|---|---:|---:|---:|---:|---:|---:|
| <50 | 1,611 | 0.8036 | 0.8028 | -0.0008 | 0.1596 | 0.1594 |
| 50–59 | 2,610 | 0.7574 | 0.7566 | -0.0007 | 0.1983 | 0.1985 |
| 60–64 | 925 | 0.6766 | 0.6745 | -0.0021 | 0.2078 | 0.2082 |
| Total | 5,146 | 0.7857 | 0.7854 | -0.0003 | 0.1879 | 0.1880 |

**Interpretación:** la especialización sin cambiar hiperparámetros no mejoró ROC-AUC en ninguno de los tres rangos. Brier mejoró marginalmente en menores de 50 y empeoró ligeramente en los otros grupos. Las diferencias son pequeñas; no permiten afirmar superioridad ni equivalencia estadística sin cuantificar la incertidumbre pareada.

**Artefactos:** `experiments/age_specialized_models/experimento_c.py` y `experiments/age_specialized_models/results/c1/` (CSV de probabilidades, métricas, umbrales, curvas y protocolo).

## 4. C2 — Selección multialgoritmo por edad
**Objetivo:** buscar una configuración competitiva dentro de cada grupo, sin imponer XGBoost como ganador. Se evaluaron regresión logística, árbol de decisión, Random Forest, Gradient Boosting y XGBoost: **5 × 3 = 15 entrenamientos**. Por decisión de alcance, **no se reentrenaron variantes globales en C2**; para la comparación final deberán emplearse referencias globales históricas bajo una evaluación común y señalar diferencias de presupuesto de tuning.

### 4.1 Protocolo de entrenamiento
- Validación cruzada estratificada de **5 folds en Train** y objetivo principal **ROC-AUC promedio**. Semilla declarada: 42.
- Búsqueda basada en los YAML originales del proyecto: regresión logística exhaustiva; las otras familias por muestreo de candidatos, garantizando incluir una configuración histórica.
- Entrenadores independientes por algoritmo y grupo, coordinados opcionalmente por `ejecutar_todos.py`, con barra de progreso y salida de cada ejecución.
- Cada entrenamiento produce `cv_candidatos.csv`, `cv_folds.csv`, `resumen.json`, `manifest.json` y un artefacto `.joblib` experimental; se registra en MLflow.
- C2 **todavía no calibra las probabilidades ni selecciona umbrales clínicamente orientados**; ambos pasos se reservan para C3.

### 4.2 Presupuesto de búsqueda
| Algoritmo | Candidatos por grupo | Folds | Ajustes CV por grupo |
|---|---:|---:|---:|
| `logistic_regression` | 30 | 5 | 150 |
| `decision_tree` | 51 | 5 | 255 |
| `random_forest` | 50 | 5 | 250 |
| `gradient_boosting` | 51 | 5 | 255 |
| `xgboost` | 71 | 5 | 355 |
| **Total (15 búsquedas)** | **759 candidatos evaluados** | | **3795 ajustes CV** |

### 4.3 Resultados de validación cruzada — ROC-AUC medio (desviación estándar)
| Algoritmo | Menores de 50 | 50–59 | 60–64 |
|---|---:|---:|---:|
| Logistic Regression | 0.8038 (±0.0086) | 0.7504 (±0.0062) | 0.7023 (±0.0139) |
| Decision Tree | 0.8038 (±0.0092) | 0.7448 (±0.0093) | 0.6889 (±0.0154) |
| Random Forest | 0.8092 (±0.0094) | 0.7521 (±0.0080) | 0.7037 (±0.0118) |
| Gradient Boosting | 0.8107 (±0.0084) | 0.7541 (±0.0078) | 0.7060 (±0.0120) |
| Xgboost | 0.8111 (±0.0088) | 0.7542 (±0.0076) | 0.7052 (±0.0119) |

**Mejor valor puntual por grupo:** XGBoost en menores de 50 (0,8111) y 50–59 (0,7542); Gradient Boosting en 60–64 (0,7060). Las ventajas frente al segundo clasificado son de aproximadamente 0,00046, 0,00010 y 0,00081, respectivamente; **no sustentan una declaración de superioridad estadística**. La dispersión entre folds no es un intervalo de confianza de la diferencia entre algoritmos.

### 4.4 Métricas exploratorias sobre Validation
Estas métricas aparecen en los `resumen.json` y **no deben usarse repetidamente para decidir ganadores**. Se incluyen solo como auditoría descriptiva.

| Algoritmo | ROC-AUC val <50 | ROC-AUC val 50–59 | ROC-AUC val 60–64 | Brier val <50 | Brier val 50–59 | Brier val 60–64 |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7907 | 0.7632 | 0.6943 | 0.1810 | 0.1994 | 0.2045 |
| Decision Tree | 0.7941 | 0.7576 | 0.6859 | 0.1663 | 0.1978 | 0.2059 |
| Random Forest | 0.7934 | 0.7638 | 0.7028 | 0.1668 | 0.1957 | 0.2022 |
| Gradient Boosting | 0.7986 | 0.7649 | 0.7017 | 0.1642 | 0.1953 | 0.2013 |
| Xgboost | 0.7985 | 0.7653 | 0.7026 | 0.1644 | 0.1951 | 0.2012 |

**Cautela:** el Brier Score refleja tanto calibración como discriminación; no permite, aisladamente, afirmar que un modelo esté bien calibrado. Tampoco se han medido aquí intervalos de confianza pareados ni desempeño independiente externo.

## 5. Trazabilidad y controles MLOps de C2
- **Control de versiones:** desarrollo en `experiment/ml-age-analysis`; los manifiestos incluyen `git_commit`. Los modelos experimentales no sustituyen a PULSO v1.
- **Procedencia de datos:** `dataset_sha256`, rutas, índices de Train/Validation y sus SHA-256; manifiestos señalan `uso_test: false`. Es una declaración auditable, no una prueba automática de ausencia de fugas en todas las dependencias.
- **Versionado experimental:** `protocolo_version: C2_v2_original_spaces_fivefold`, `search_method`, hashes del espacio y de la configuración histórica, número de candidatos y folds.
- **Tracking:** cada ejecución incluye `mlflow_run_id`; resultados registrados en la base local de MLflow. Conservar copia verificable de los artefactos en almacenamiento persistente antes de cualquier limpieza de archivos locales.
- **Artefactos:** SHA-256 de `modelo_experimental.joblib`, manifiestos, CSV de candidatos y folds, `resumen.json`; no se recomienda agregar `.joblib`, `mlflow.db` ni ZIP redundantes al historial Git convencional.
- **Pruebas:** el usuario verificó localmente **7 pruebas aprobadas** (`tests/test_c2_experiments.py`) tras corregir ubicación de configuraciones YAML. Esta confirmación local no demuestra por sí sola el estado de GitHub Actions.
- **Ejecución de lote:** el reporte de resultados contiene 15 entrenamientos completos. El flujo es secuencial, con logs y posibilidad de reanudación.

### 5.1 Riesgos y requisitos pendientes
1. Verificar en CI la integración de las nuevas pruebas y contrastar con `GUIA_CI_CD_MLOPS_TESTING_PULSO` antes de aprobar un PR. No afirmar que CI está integrado si no se ha modificado y observado el workflow.
2. Auditar independencia entre perfiles repetidos de Train, Validation y Test; la auditoría previa detectó coincidencias de perfiles que no prueban identidad de pacientes.
3. Congelar de forma explícita protocolo de selección/calibración y evitar elegir repetidamente entre alternativas según métricas de Validation ya consultadas.
4. Registrar versiones del entorno (`pip freeze` o lockfile), hardware si importa al tiempo de ejecución, y comprobar integridad/recarga de cada artefacto.
5. Evaluar discontinuidades de probabilidad y decisión en 50 y 60 años, así como coherencia de SHAP y simulación si se integra una arquitectura de modelos heterogéneos.

## 6. Interpretación y decisión provisional
**C1:** no ofrece evidencia de ganancia al especializar XGBoost manteniendo hiperparámetros comunes. **C2:** muestra que XGBoost y Gradient Boosting son candidatos competitivos en los tres grupos, pero el rendimiento decrece al aumentar la edad y sus diferencias son demasiado pequeñas para elegir ganadores definitivos. Se proponen para C3 ambas familias por grupo; Random Forest puede permanecer como alternativa de reserva, especialmente en 60–64.

**No realizar cambios en el modelo oficial PULSO v1.** El umbral 0,38, la calibración actual y las interfaces de producción permanecen intactas mientras no exista evidencia independiente suficiente y valoración médica.

## 7. C3 — Calibración y selección de umbrales (pendiente)
**Objetivo:** comparar configuraciones sin calibrar, sigmoide e isotónica para candidatos predefinidos, utilizando predicciones de entrenamiento fuera de muestra para escoger calibradores; después seleccionar umbrales con **recall ≥0,80** en una muestra de selección, maximizando especificidad sujeto a la restricción. Documentar cuando no exista umbral factible en la cuadrícula examinada.

**Protocolo a definir antes de ejecutar:** método de validación anidada o separación que evite usar los mismos registros para elegir calibrador, umbral y estimar rendimiento. Registrar ROC-AUC, PR-AUC, Brier, log-loss, calibración, sensibilidad, especificidad, FP/FN, IC y curvas. No usar Test para seleccionar modelos. El objetivo de 80 % es experimental y sujeto a criterio médico, no garantía clínica.

## 8. C4 — Comparación integral y robustez (pendiente)
Comparar la mejor solución especializada con una referencia global bajo exactamente el mismo protocolo de evaluación. Cuantificar diferencias pareadas e incertidumbre, repercusión de los saltos en límites etarios, degradación/calibración por grupo, complejidad operativa, mantenimiento y explicabilidad. Dado el uso previo de Test en decisiones de diseño, una afirmación confirmatoria exigirá una cohorte independiente adicional.

## 9. Índice de artefactos y reproducción
```text
experiments/age_specialized_models/
  experimento_c.py                 # C1
  results/c1/                    # CSV y protocolo C1
  c2/
    motor.py                      # selección y evaluación CV de C2
    entrenar_*.py                # cinco ejecutores individuales
    ejecutar_todos.py            # lote de 15 ejecuciones por grupo
    search_spaces/*.yaml         # espacios de búsqueda
    candidates/*_tuned.yaml      # configuraciones históricas
    README.md
    CI_INTEGRATION.md
  results/c2_v2/<algoritmo>/<grupo>/
    cv_candidatos.csv
    cv_folds.csv
    resumen.json
    manifest.json
    modelo_experimental.joblib   # mantener fuera de Git
tests/test_c2_experiments.py
```

**Comando de pruebas:** `python -m pytest -v tests/test_c2_experiments.py`  
**Ejemplo de entrenamiento:** `python -m experiments.age_specialized_models.c2.entrenar_xgboost --grupo menor_50`  
**Ejecución en lote:** `python -m experiments.age_specialized_models.c2.ejecutar_todos --dry-run`, luego sin `--dry-run`.

## 10. Fuentes internas de este informe
- `c1_comparacion_probabilidades.csv`, `c1_metricas_evaluacion.csv` y `c1_umbrales_seleccionados.csv`, facilitados durante C1.
- `c2_v2.zip`: los 15 `resumen.json` y `manifest.json`, CSV de validación cruzada y resumen de lote.
- Configuraciones y metodología previamente descritas del entrenamiento PULSO v1; archivos YAML del paquete C2 v2.

**Estado documental:** informe de avance, no resultado definitivo. Actualizar al cerrar C3 y C4 sin modificar retroactivamente las observaciones de C1/C2.

# PULSO — Informe técnico del experimento C
**Versión:** 1.0 — consolidación C1–C5  
**Fecha documental:** 31 de octubre de 2026  
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
**C1:** no ofrece evidencia de ganancia al especializar XGBoost manteniendo hiperparámetros comunes. **C2:** muestra que XGBoost y Gradient Boosting son candidatos competitivos en los tres grupos, pero el rendimiento decrece al aumentar la edad y sus diferencias son demasiado pequeñas para elegir ganadores definitivos. Se eligieron XGBoost y Gradient Boosting para la continuación en C3. Random Forest permaneció como alternativa secundaria, sin incorporarse a C3–C5.

**No realizar cambios en el modelo oficial PULSO v1.** El umbral 0,38, la calibración actual y las interfaces de producción permanecen intactas mientras no exista evidencia independiente suficiente y valoración médica.

## 7. C3 — Calibración independiente y selección de umbrales

### 7.1 Diseño y calibración

Se reutilizaron los modelos seleccionados en C2: XGBoost y Gradient Boosting para cada uno de los tres grupos, seis combinaciones en total. La comparación de calibración consideró ausencia de calibración, sigmoide e isotónica mediante validación cruzada dentro de Train. Las elecciones registradas fueron XGBoost sin calibración adicional en los tres grupos, Gradient Boosting con sigmoide en menores de 50 y en 50–59, y Gradient Boosting sin calibración en 60–64. La mejora de Brier atribuida a la sigmoide fue muy pequeña; no se debe interpretar como mejora clínica consolidada. Los seis artefactos experimentales se conservan con manifiestos y hashes en `c3_calibracion.zip`.

### 7.2 Políticas de umbral

Sobre la mitad de Validation destinada a selección se evaluó una rejilla de umbrales de 0,01 a 0,99, con cuatro políticas: **B**, recall ≥0,80 en selección y máxima especificidad entre opciones factibles; **C**, máxima Balanced Accuracy; **D**, máximo de `min(recall, especificidad)`; **E**, máxima `0,60·recall + 0,40·especificidad`. La otra mitad de Validation (5.146 filas) se reservó para evaluación. **No se incluyó una política de umbral fijo 0,38 en C3**; la coincidencia de algún umbral seleccionado con 0,38 es un resultado de la búsqueda.

Resultados por grupo para la política B (evaluación, no selección):

| Algoritmo | Grupo | Umbral | Recall | Especificidad |
|---|---|---:|---:|---:|
| xgboost | menor_50 | 0.23 | 80.78 % | 59.23 % |
| xgboost | 50_59 | 0.38 | 80.46 % | 51.47 % |
| xgboost | 60_64 | 0.57 | 80.56 % | 43.96 % |
| gradient_boosting | menor_50 | 0.23 | 79.60 % | 59.72 % |
| gradient_boosting | 50_59 | 0.38 | 79.72 % | 52.26 % |
| gradient_boosting | 60_64 | 0.58 | 78.74 % | 46.13 % |

La condición de recall ≥0,80 se impone en selección, **no garantiza** su cumplimiento posterior en evaluación: Gradient Boosting no alcanza 0,80 en las tres cohortes de la tabla. La comparación de las 24 combinaciones de política y modelo se conserva en los CSV originales de `c3_umbrales.zip`.

## 8. C4 — Robustez: incertidumbre, estabilidad y continuidad

### 8.1 Incertidumbre estadística

Se calcularon intervalos de Wilson para métricas y **12 comparaciones pareadas por bootstrap (1.000 remuestreos)** entre XGBoost y Gradient Boosting, por grupo y política. Los intervalos de diferencia de Balanced Accuracy incluyen cero en 11 de las 12 comparaciones; la excepción corresponde a la política E en 50–59. Los intervalos de diferencia de ROC-AUC incluyen cero para los tres grupos. Estos son análisis exploratorios, sin corrección por multiplicidad ni validación independiente.

### 8.2 Estabilidad de umbrales

Se ejecutaron **100 redistribuciones** del conjunto de desarrollo de umbrales para las 6 combinaciones modelo-edad y las 4 políticas; **2.400 evaluaciones**. Las probabilidades de los modelos se calcularon previamente y reutilizaron: no fue necesario reentrenar. Las amplitudes promedio percentil 5–95 de los umbrales fueron:

| Política | Amplitud media del umbral P95−P05 |
|---|---:|
| C balanced accuracy | 0.0984 |
| D minimax | 0.0117 |
| B recall ≥0,80 | 0.0151 |
| E ponderada 60/40 | 0.0901 |

B y D mostraron umbrales más estables; C y E, mayor variabilidad. Los percentiles de 100 redistribuciones de las **mismas observaciones** no son intervalos de confianza obtenidos de datos independientes.

### 8.3 Continuidad en 50 y 60 años

Se ejecutaron contrafactuales de perfiles cercanos a 50 y 60 años con cambio de edad de ±0,01 años y ventana ±1 año. Se registraron 16 resúmenes de frontera y **16.016 filas de detalle contrafactual** (repeticiones de perfiles entre algoritmos y políticas, no 16.016 personas distintas).

| Frontera | Algoritmo | Política | Proporción que cambia de clase | Salto absoluto promedio de probabilidad |
|---:|---|---|---:|---:|
| 50 | xgboost | recall80 | 14.47 % | 4.28 pp |
| 50 | xgboost | balanced_accuracy | 4.76 % | 4.28 pp |
| 50 | xgboost | minimax | 9.42 % | 4.28 pp |
| 50 | xgboost | weighted_60_40 | 11.46 % | 4.28 pp |
| 50 | gradient_boosting | recall80 | 14.17 % | 4.23 pp |
| 50 | gradient_boosting | balanced_accuracy | 3.30 % | 4.23 pp |
| 50 | gradient_boosting | minimax | 9.61 % | 4.23 pp |
| 50 | gradient_boosting | weighted_60_40 | 16.60 % | 4.23 pp |
| 60 | xgboost | recall80 | 54.94 % | 9.58 pp |
| 60 | xgboost | balanced_accuracy | 38.27 % | 9.58 pp |
| 60 | xgboost | minimax | 45.58 % | 9.58 pp |
| 60 | xgboost | weighted_60_40 | 58.02 % | 9.58 pp |
| 60 | gradient_boosting | recall80 | 58.64 % | 10.81 pp |
| 60 | gradient_boosting | balanced_accuracy | 38.58 % | 10.81 pp |
| 60 | gradient_boosting | minimax | 54.32 % | 10.81 pp |
| 60 | gradient_boosting | weighted_60_40 | 53.50 % | 10.81 pp |

La frontera de 60 años produce cambios de clasificación elevados en varias políticas. Para XGBoost con B se observó aproximadamente **54,9 %** de cambios; para Gradient Boosting con B, aproximadamente **58,6 %**. Se trata de una prueba contrafactual sobre el funcionamiento del clasificador, **no de evidencia de cambio fisiológico real**. El cambio de modelo y el cambio simultáneo de umbral contribuyen al fenómeno; el análisis conjunto no descompone causalmente cada contribución.

## 9. C5 — Comparación global frente a modelos especializados

### 9.1 Protocolo

Se reconstruyó una referencia **XGBoost global entrenada exclusivamente sobre Train (48.027 filas)** con la configuración v1, para evitar utilizar en Validation el modelo oficial entrenado sobre Train+Validation. Se seleccionaron los umbrales globales usando 5.145 registros de Validation y se evaluaron todas las alternativas sobre los **mismos 5.146 registros**. Se contrastaron 13 configuraciones de decisión: global de referencia 0,38; global con B–E; especializados XGBoost con B–E; especializados Gradient Boosting con B–E. Las 52 filas de métricas incluyen cuatro ámbitos (total y tres grupos) por configuración.

### 9.2 Resultados globales

| Configuración | Política | Recall | Especificidad | Balanced Accuracy | FP | FN |
|---|---|---:|---:|---:|---:|---:|
| global_train_only | referencia_038 | 80.36 % | 60.35 % | 70.35 % | 1031 | 500 |
| global_train_only | recall80 | 80.36 % | 60.35 % | 70.35 % | 1031 | 500 |
| global_train_only | balanced_accuracy | 69.72 % | 74.96 % | 72.34 % | 651 | 771 |
| global_train_only | minimax | 72.62 % | 70.77 % | 71.70 % | 760 | 697 |
| global_train_only | weighted_60_40 | 78.52 % | 62.46 % | 70.49 % | 976 | 547 |
| especializado_xgboost | recall80 | 80.56 % | 53.58 % | 67.07 % | 1207 | 495 |
| especializado_xgboost | balanced_accuracy | 63.55 % | 76.92 % | 70.24 % | 600 | 928 |
| especializado_xgboost | minimax | 68.97 % | 69.38 % | 69.18 % | 796 | 790 |
| especializado_xgboost | weighted_60_40 | 72.86 % | 60.46 % | 66.66 % | 1028 | 691 |
| especializado_gradient_boosting | recall80 | 79.46 % | 54.42 % | 66.94 % | 1185 | 523 |
| especializado_gradient_boosting | balanced_accuracy | 63.90 % | 77.19 % | 70.55 % | 593 | 919 |
| especializado_gradient_boosting | minimax | 69.05 % | 69.58 % | 69.31 % | 791 | 788 |
| especializado_gradient_boosting | weighted_60_40 | 72.23 % | 63.38 % | 67.81 % | 952 | 707 |

La Balanced Accuracy global más alta en estas observaciones corresponde al **modelo global, política C**. El modelo global supera en Balanced Accuracy a los enfoques especializados en las cuatro políticas. No implica superioridad confirmatoria tras la selección exploratoria reiterada.

### 9.3 Disparidad etaria con la política B global

| Grupo | Recall | Especificidad |
|---|---:|---:|
| menor_50 | 62.06 % | 86.44 % |
| 50_59 | 80.38 % | 52.98 % |
| 60_64 | 98.34 % | 6.81 % |

El recall del modelo global con B es desigual entre grupos, mientras que el XGBoost especializado con B registra aproximadamente 80 % en cada grupo. Esa homogeneidad se consigue al costo de más falsos positivos globalmente y mayores discontinuidades de clasificación. Por ello conviene **distinguir equidad de la sensibilidad, discriminación global y costo de falsos positivos** en la decisión médica.

### 9.4 Métricas independientes del umbral

Según los resultados de C5: ROC-AUC global ≈ **0,78571**; especializado XGBoost ≈ **0,78551**; especializado Gradient Boosting ≈ **0,78557**. Brier global ≈ **0,18790**; especializado XGBoost ≈ **0,18783**; especializado Gradient Boosting ≈ **0,18784**. Las diferencias puntuales son pequeñas, no evidencia de equivalencia estadística ni de superioridad clínica. C5 calcula diferencias pareadas puntuales, pero **no intervalos pareados global–especializado para todas las configuraciones**.

## 10. Síntesis de hallazgos y decisión provisional

1. **C1:** separar XGBoost por edades sin modificar hiperparámetros no mejoró ROC-AUC respecto de la referencia global.
2. **C2:** XGBoost y Gradient Boosting dominaron por diferencias puntuales pequeñas; las familias optimizadas no demostraron ventajas suficientemente grandes para justificar complejidad adicional.
3. **C3:** calibración produjo mejoras mínimas; las políticas de umbral generan un intercambio fuerte entre recall, especificidad y carga de falsos positivos.
4. **C4:** B y D resultaron más estables como umbrales; las transiciones entre grupos especialmente a los 60 años son un problema de consistencia de clasificación.
5. **C5:** los especialistas aproximaron el recall entre edades, pero no superaron la Balanced Accuracy global y conservaron ROC-AUC prácticamente igual al modelo único.

**Decisión técnica provisional: conservar el modelo global como arquitectura de referencia y no integrar los modelos especializados en PULSO v1.** La elección del umbral vigente **0,38** debe discutirse con la asesora médica; no se modifica automáticamente por este documento. El modelo clasifica `cardio` en el dataset, no estima incidencia clínica prospectiva.

## 11. Amenazas a la validez y controles pendientes

- **Reutilización de Validation:** C1–C5 y B/B3 exploraron reiteradamente la misma partición. Los análisis son exploratorios y sus intervalos no corrigen el sesgo de selección del proceso completo.
- **Influencia histórica de Test:** los análisis anteriores por subgrupos y la selección de cortes etarios estuvieron informados en parte por el Test original. El `test_used: false` de C3–C5 no convierte esas decisiones históricas en independientes.
- **Población:** la base observada llega aproximadamente a 64,9 años; no se debe extrapolar a ≥65 ni asumir representatividad clínica general.
- **C5:** el referente global se entrenó solo con Train; es comparable experimentalmente, pero distinto del artefacto final de producción entrenado con Train+Validation.
- **Equidad:** diferencias de recall no son por sí solas una evaluación integral de justicia, seguridad clínica o beneficio sanitario.
- **MLOps:** los protocolos registran semilla, hash de datos, commit y MLflow; verificar retención de artefactos y ejecuciones exitosas de CI antes de integrar cualquier PR. Las pruebas locales no equivalen a checks reales de GitHub Actions.
- **Confiabilidad funcional:** cualquier modificación futura en umbral/modelos exige verificar contratos `/predict`, `/explain` (SHAP), `/simulate` y `/api/analyze`, coherencia de IMC y regresiones del flujo RAG; una familia de modelos diferente podría requerir recalcular explicaciones y actualizar documentación.

## 12. Relación con B/B3: no duplicar un supuesto experimento D

Los experimentos **B y B3 ya compararon** umbral único global frente a umbrales por edad en un único XGBoost, con políticas recall ≥0,80, Balanced Accuracy, minimax y ponderación 60/40; también estudiaron estabilidad de umbrales y discontinuidades. Por tanto, **no corresponde repetir esa matriz bajo la etiqueta “experimento D”**. Las diferencias relevantes de C5 son la evaluación común global–especializados y el entrenamiento/control de procedencia de los referentes. Si se exigiera una comparación unificada B/B3–C5, habría que comprobar primero identidades exactas de registros, entrenamiento y selección, y limitarse a cálculos complementarios no cubiertos por trabajos previos.

## 13. Próximos pasos de cierre

1. Congelar informes B/B3 y C1–C5 con rutas de artefactos, hashes, versiones y un registro de decisiones.
2. Preparar un documento breve para la asesora médica con recall por grupo, especificidad, FP/FN, consecuencias de los cambios de umbral y limitaciones.
3. Mantener PULSO v1 sin cambios hasta acuerdo médico/técnico y disponibilidad de una evaluación confirmatoria genuinamente independiente (idealmente datos externos nuevos).
4. Si se propone cambio de política, preparar protocolo preespecificado de validación, criterios de aceptación, impacto en SHAP/simulación y CI/CD antes de alterar producción.

## 14. Artefactos de respaldo

- `INFORME_EXPERIMENTAL_PULSO_AUDITORIA_2_B_B3.md`: análisis previos de umbral global y por edad.
- `c1_metricas_evaluacion.csv`, `c1_comparacion_probabilidades.csv`: C1.
- `c2_v2.zip`: búsqueda, validación cruzada y manifiestos C2.
- `c3_calibracion.zip`, `c3_umbrales.zip`: calibración, umbrales y 24 métricas de C3.
- `c4.zip`: incertidumbre, estabilidad, continuidad y protocolos C4.
- `c5_comparacion.zip`: métricas, predicciones pareadas, umbrales y protocolo C5.
- `GUIA_CI_CD_MLOPS_TESTING_PULSO`: referencia para comprobación previa a PR, no prueba de que todos los workflows se ejecutaron satisfactoriamente.

**Estado:** informe consolidado de investigación exploratoria C1–C5. No es aprobación de despliegue, recomendación clínica ni sustitución del modelo oficial.

# PULSO — Informe técnico de experimentación por edad

**Alcance:** desde la segunda auditoría del conjunto de datos hasta los experimentos B, B3 y sus análisis de estabilidad.  
**Fecha de consolidación:** 28 de octubre de 2026.  
**Rama de trabajo:** `experiment/ml-age-analysis`.  
**Estado:** investigación exploratoria; **no se han aprobado cambios al modelo ni al umbral oficial de PULSO v1**.

## 1. Resumen ejecutivo

El propósito de esta línea de trabajo fue estudiar las diferencias de comportamiento del clasificador cardiovascular PULSO v1 entre los grupos de edad **menores de 50**, **50–59** y **60–64 años**, e investigar reglas de clasificación alternativas sobre un **único XGBoost global**. El proyecto clasifica la etiqueta `cardio` del conjunto de datos empleado; **no predice directamente eventos cardiovasculares futuros a diez años**.

Los principales resultados fueron:

1. **Auditoría 2:** las asociaciones descriptivas de presión arterial, IMC y otras variables con `cardio` cambian entre edades; se detectaron coincidencias de perfiles entre Train y Validation que requieren seguimiento, pero no prueban duplicación de pacientes.
2. **Experimento B original:** los umbrales por edad **0,23 / 0,38 / 0,55**, seleccionados para buscar recall ≥80 % por grupo, homogeneizaron el recall, pero en la evaluación redujeron la especificidad global de **60,35 % a 52,58 %**.
3. **Estabilidad B:** los umbrales resultaron estrechamente agrupados en 100 particiones reutilizadas; el recall ≥80 % no se mantuvo de manera sistemática en la evaluación separada. Los cortes etarios introducen posibles discontinuidades de clasificación.
4. **Experimento B3:** se compararon **Balanced Accuracy**, ponderación **60/40** a favor del recall y **minimax**, tanto globalmente como por edad. El mejor promedio de Balanced Accuracy global correspondió a **Balanced Accuracy con un solo umbral global**; **minimax por edad** mostró los mejores mínimos promedio entre subgrupos en las dos métricas, a costa de menor recall global.
5. **Estabilidad B3:** los resultados anteriores persistieron en 100 redistribuciones internas; ninguna alternativa demuestra superioridad clínica o justifica aún reemplazar la política oficial **0,38**.

**Decisión experimental:** mantener PULSO v1 sin modificaciones; conservar B y B3 como resultados de investigación y continuar con el diseño controlado del experimento C (modelos especializados), sin reutilizar Test para optimizar decisiones.

## 2. Contexto técnico y alcance de los datos

| Elemento | Especificación |
|---|---|
| Dataset procesado | `data/processed/cardio_clean_v1.csv` |
| Filas después de limpieza | 68.610 |
| Train | 48.027 |
| Validation | 10.291 |
| Test | 10.292 |
| Modelo de referencia | XGBoost de PULSO v1 |
| Configuración | `models/pulso/v1/final_model.yaml` |
| Umbral oficial | 0,38 |
| Edad observada | Aproximadamente 29,6–64,9 años |
| Grupos exploratorios | `<50`, `50–59`, `60–64` |
| Variables del modelo | `gender`, `height`, `weight`, `ap_hi`, `ap_lo`, `smoke`, `alco`, `active`, `age_years`, `bmi` |

**Distinción indispensable:** el artefacto final de PULSO v1 se reentrenó originalmente utilizando Train + Validation. Los experimentos B/B3, en cambio, entrenan **otro ejemplar del XGBoost configurado como v1** sobre Train solamente. Por tanto, los resultados experimentales con umbral 0,38 son una **referencia dentro del protocolo**, no una reevaluación idéntica del artefacto de producción.

Los grupos de edad fueron estudiados previamente con datos de Test. Aunque B y B3 no utilizan Test durante sus propias ejecuciones, **la elección de grupos no es totalmente independiente de Test**; esto limita las afirmaciones confirmatorias futuras.

## 3. Auditoría 2: variables, hábitos y coincidencias de perfiles

**Script:** `experiments/age_analysis/auditoria_2.py`.  
**Ejecución:** `python -m experiments.age_analysis.auditoria_2`.  
**Resultados:** `experiments/age_analysis/results/auditoria_2/`.

### 3.1 Objetivos y procedimiento

La auditoría fue **descriptiva** y se realizó sobre Train + Validation (**58.318 registros**); no entrenó ni ajustó un modelo. Comparó distribuciones de presión sistólica y diastólica, IMC, talla, peso, hábitos, clase real y correlaciones de Spearman por edad. También contó perfiles repetidos dentro del conjunto de desarrollo y coincidencias entre sus particiones.

### 3.2 Grupos y prevalencia en desarrollo

| Grupo | n | Positivos `cardio=1` | Prevalencia aproximada |
|---|---:|---:|---:|
| Menores de 50 | 18.087 | 6.575 | 36,35 % |
| 50–59 | 29.587 | 15.170 | 51,27 % |
| 60–64 | 10.644 | 7.105 | 66,75 % |

La prevalencia de la etiqueta positiva aumenta con la edad. Este dato, por sí solo, **no define los umbrales de clasificación**.

### 3.3 Correlaciones exploratorias con `cardio`

| Variable | Menores de 50 | 50–59 | 60–64 |
|---|---:|---:|---:|
| Presión sistólica (`ap_hi`) | 0,490 | 0,417 | 0,310 |
| Presión diastólica (`ap_lo`) | 0,402 | 0,328 | 0,223 |
| IMC (`bmi`) | 0,216 | 0,180 | 0,126 |
| Peso (`weight`) | 0,217 | 0,168 | 0,105 |
| Edad dentro del grupo | 0,144 | 0,111 | 0,097 |
| Tabaquismo | 0,002 | −0,010 | −0,017 |
| Alcohol | −0,003 | −0,002 | −0,007 |
| Actividad física | −0,028 | −0,041 | −0,033 |

Estas magnitudes son **correlaciones marginales descriptivas**, no efectos causales, medidas de importancia SHAP, ni evidencia suficiente de interacciones estadísticas. Correlaciones pequeñas de hábitos no implican ausencia de efectos cardiovasculares ni autorizan eliminar esas variables.

Las medianas de presión sistólica por clase fueron aproximadamente **120 mmHg (`cardio=0`) y 130 mmHg (`cardio=1`)** en los tres grupos. La diferencia de medianas de IMC entre clases disminuyó aproximadamente de **2,17** unidades en menores de 50 a **1,48** en 60–64 años.

### 3.4 Perfiles repetidos

| Criterio | Filas correspondientes a perfiles repetidos en desarrollo | Perfiles distintos repetidos | Filas Train con equivalente en Validation |
|---|---:|---:|---:|
| Mismas diez variables | 70 | 35 | 12 |
| Mismas diez variables y etiqueta | 40 | 20 | 5 |

**Interpretación:** dos personas distintas pueden compartir todas estas mediciones; las coincidencias no permiten afirmar duplicación del mismo paciente. Se recomienda investigar los identificadores originales, si están disponibles, y efectuar una comprobación adicional de coincidencias con Test **como control de integridad**, no para volver a ajustar umbrales utilizando resultados de Test. No se eliminaron registros en esta auditoría.

### 3.5 Productos de la auditoría

- `01_mediciones_por_edad.png`
- `02_habitos_por_edad.png`
- `03_variables_por_edad_y_clase.png`
- `variables_por_grupo_y_clase.csv`
- `asociaciones_exploratorias.csv`
- `duplicados_desarrollo.csv`
- `resumen.txt`

## 4. Protocolo común de experimentos B y B3

1. Cargar el dataset depurado y respetar `split_data()`.
2. Entrenar un único pipeline XGBoost sobre **Train = 48.027** con los hiperparámetros de PULSO v1.
3. Obtener probabilidades de **Validation = 10.291** y dividirlo, con semilla 42, en **selección = 5.145** y **evaluación = 5.146**.
4. Optimizar umbrales **solo con la mitad de selección**.
5. Comparar políticas sobre la mitad de evaluación, que no participó en la elección de esos umbrales.
6. Mantener **Test = 10.292** fuera de estas ejecuciones.

El modelo permanece fijo cuando se comparan políticas: las diferencias de recall y especificidad provienen de las reglas de clasificación, no de cambios en `predict_proba`. Por ello, **ROC-AUC y Brier son idénticos entre políticas que usan las mismas probabilidades**.

### Métricas y sus definiciones

- **Recall / sensibilidad:** `TP / (TP + FN)`.
- **Especificidad:** `TN / (TN + FP)`.
- **Precisión / PPV:** `TP / (TP + FP)`.
- **Balanced Accuracy (BA):** `(recall + especificidad) / 2`.
- **F1:** media armónica de precisión y recall.
- **ROC-AUC:** discriminación del modelo por probabilidades; no cambia al mover el umbral.
- **Brier:** error cuadrático medio de las probabilidades; tampoco cambia al mover el umbral.

## 5. Experimento B: selección por recall objetivo ≥80 %

**Script:** `experiments/age_thresholds/experimento_b.py`.  
**Ejecución:** `python -m experiments.age_thresholds.experimento_b`.  
**Artefactos principales:** `experiments/age_thresholds/results/umbrales_seleccionados.csv`, `metricas_validacion_evaluacion.csv`, `protocolo.json` (según ejecución).

### 5.1 Pregunta y función objetivo

¿Puede un único XGBoost, con umbrales diferentes según edad, llevar el recall de cada grupo aproximadamente al 80 %? En la muestra de selección, se eligió un umbral que satisficiera **recall ≥0,80**, priorizando luego precisión. La condición es **solo de selección**; no es una garantía de recall sobre nuevos registros.

### 5.2 Umbrales seleccionados

| Alcance | Umbral |
|---|---:|
| Global optimizado | 0,38 |
| Menores de 50 | 0,23 |
| 50–59 | 0,38 |
| 60–64 | 0,55 |

### 5.3 Evaluación global separada (n=5.146)

| Política | Recall | Especificidad | Precisión | F1 | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Referencia 0,38 | 80,36 % | 60,35 % | 66,49 % | 72,77 % | 1.031 | 500 |
| Umbrales por edad | 81,07 % | 52,58 % | 62,60 % | 70,65 % | 1.233 | 482 |

**Cambio respecto a 0,38:** **18 falsos negativos menos** y **202 falsos positivos adicionales** en la misma evaluación.

Por grupos, el recall pasó aproximadamente de **62,06 % a 81,96 %** en menores de 50, permaneció en **80,38 %** para 50–59 y descendió de **98,34 % a 81,73 %** en 60–64. La especificidad del grupo mayor mejoró de cerca de **6,81 % a 42,41 %**, mientras que la de menores de 50 bajó de cerca de **86,44 % a 55,30 %**.

**Conclusión B:** se consiguió una distribución de recall más homogénea, pero el intercambio agregado entre FN y FP y la caída de especificidad desaconsejan proponer esta política directamente como sustitución de PULSO v1.

## 6. Estabilidad del experimento B

**Script:** `experiments/age_thresholds/analisis_estabilidad_b.py`.  
**Protocolo:** 100 redistribuciones estratificadas 50/50 de Validation, semillas **42–141**, con **Train y modelo fijos**.

### 6.1 Estabilidad de umbrales

| Alcance | Mediana | P5–P95 |
|---|---:|---:|
| Global | 0,38 | 0,37–0,38 |
| Menores de 50 | 0,23 | 0,22–0,24 |
| 50–59 | 0,38 | 0,37–0,38 |
| 60–64 | 0,55 | 0,55–0,56 |

La estrechez de estos rangos sugiere estabilidad **condicionada al modelo y Validation utilizados**. Los percentiles de estas 100 redistribuciones **no son intervalos de confianza poblacionales**.

### 6.2 Rendimiento promedio global en las 100 redistribuciones

| Política | Recall medio | Especificidad media |
|---|---:|---:|
| Umbral fijo 0,38 | 80,26 % | 61,08 % |
| Umbrales por edad | 80,96 % | 53,99 % |

En el grupo de menores de 50, el recall de evaluación alcanzó ≥80 % en **51 de las 100** redistribuciones; para 50–59 ocurrió en **88 de 100**, y para 60–64 en **69 de 100**. No es válido afirmar que la condición de sensibilidad se cumplirá necesariamente en población externa.

Los intervalos de Wilson del 95 % de la evaluación original para el recall de la política por edad fueron, aproximadamente: **78,66–84,84 %** (<50), **78,18–82,41 %** (50–59) y **78,44–84,61 %** (60–64). Todos incluyen valores inferiores a 80 %.

### 6.3 Discontinuidades en los cortes etarios

El análisis mantuvo **fija la probabilidad predicha** y comprobó si se invertiría la clase al utilizar el umbral del grupo vecino. Para la política B se detectaron cambios potenciales en cerca de **40,8 %** de los registros situados a ±0,5 años de los 50 y **37,4 %** de los situados a ±0,5 años de los 60 (según el archivo de análisis de cortes). **No representa un experimento longitudinal ni una simulación completa de aumentar la edad**, ya que las probabilidades podrían cambiar.

## 7. Experimento B3: balance recall–especificidad

**Script:** `experiments/age_thresholds/experimento_b3.py`.  
**Ejecución:** `python -m experiments.age_thresholds.experimento_b3`.  
**Resultados:** `experiments/age_thresholds/results/b3/`.

### 7.1 Motivación

B optimizaba prioridad de sensibilidad por grupo, pero sacrificaba especificidad. Se diseñó B3 para comparar **equilibrios alternativos** sin cambiar el modelo base ni utilizar Test.

### 7.2 Funciones objetivo

1. **Balanced Accuracy (BA):** maximizar `(recall + especificidad) / 2`. Equivale a maximizar el índice de Youden en cuanto a elección de umbral.
2. **Ponderación 60/40:** maximizar `0,6 × recall + 0,4 × especificidad`; **ponderación exploratoria, no validada por el equipo médico**.
3. **Minimax:** maximizar `min(recall, especificidad)`; favorece evitar que una de ambas métricas sea demasiado baja.

Cada función se aplicó **globalmente** (un umbral) y **por edad** (tres umbrales). Se mantuvieron como referencias 0,38 y el B original. El barrido de candidatos fue de **0,05 a 0,95, paso 0,01**, con desempate definido en el protocolo (`BA`, proximidad a 0,38 y umbral).

### 7.3 Umbrales B3 seleccionados en la partición inicial

| Objetivo | Global | Menores de 50 | 50–59 | 60–64 |
|---|---:|---:|---:|---:|
| BA | 0,49 | 0,39 | 0,49 | 0,63 |
| 60/40 | 0,39 | 0,26 | 0,39 | 0,63 |
| Minimax | 0,45 | 0,27 | 0,44 | 0,63 |

Que los tres criterios seleccionaran 0,63 en el grupo 60–64 en esta partición no implica que dicho valor sea óptimo fuera del dataset.

### 7.4 Evaluación global separada (n=5.146)

| Política | Recall | Especificidad | BA | FP | FN |
|---|---:|---:|---:|---:|---:|
| Referencia 0,38 | 80,36 % | 60,35 % | 70,35 % | 1.031 | 500 |
| B previo por edad | 81,07 % | 52,58 % | 66,82 % | 1.233 | 482 |
| B3 BA global | 69,72 % | 74,96 % | **72,34 %** | 651 | 771 |
| B3 BA por edad | 64,41 % | 77,69 % | 71,05 % | 580 | 906 |
| B3 60/40 global | 78,52 % | 62,46 % | 70,49 % | 976 | 547 |
| B3 60/40 por edad | 73,84 % | 61,42 % | 67,63 % | 1.003 | 666 |
| B3 minimax global | 72,62 % | 70,77 % | 71,70 % | 760 | 697 |
| B3 minimax por edad | 69,87 % | 68,50 % | 69,19 % | 819 | 767 |

**Lectura correcta:** BA global obtuvo la BA agregada más alta en esa muestra, pero produjo **271 FN más** que 0,38. Minimax global presentó recall y especificidad globales muy similares y evita añadir discontinuidades por umbrales etarios. Minimax por edad equilibró más las métricas **dentro de cada grupo**, pero sacrificó recall respecto a la referencia.

### 7.5 Límites de edad en B3

En una ventana de ±0,5 años, el porcentaje de posibles inversiones de clase por cambiar el umbral de grupo —**manteniendo fija la probabilidad**— fue aproximadamente:

| Política por edad | Corte 50 | Corte 60 |
|---|---:|---:|
| BA | 3,14 % | 22,76 % |
| 60/40 | 22,46 % | 50,38 % |
| Minimax | 21,50 % | 35,04 % |

Los porcentajes describen sensibilidad de la **regla de decisión** a un cambio de grupo, no la variación real del riesgo estimado durante el envejecimiento.

## 8. Estabilidad B3: 100 redistribuciones

**Script:** `experiments/age_thresholds/estabilidad_b3.py`.  
**Resultados:** `experiments/age_thresholds/results/b3_estabilidad/`.  
**Protocolo:** Train fija, un modelo único, 100 divisiones estratificadas de Validation con semillas **42–141**; comprobación con semilla 42 **coincidente** con B3 original.

### 8.1 Resultados globales medios

| Política | Recall | Especificidad | BA |
|---|---:|---:|---:|
| Referencia 0,38 | **80,26 %** | 61,08 % | 70,67 % |
| B previo por edad | 81,25 % | 53,41 % | 67,33 % |
| BA global | 69,42 % | 75,24 % | **72,33 %** |
| BA por edad | 62,75 % | **79,41 %** | 71,08 % |
| 60/40 global | 78,29 % | 63,67 % | 70,98 % |
| 60/40 por edad | 74,32 % | 64,66 % | 69,49 % |
| Minimax global | 72,11 % | 72,38 % | 72,24 % |
| Minimax por edad | 69,60 % | 70,49 % | 70,05 % |

### 8.2 Rendimiento del peor grupo por repetición

Cada valor es el **promedio del mínimo** de la métrica entre los tres grupos en cada redistribución, no un promedio de un mismo grupo fijo.

| Política | Peor recall grupal medio | Peor especificidad grupal media | Peor BA grupal media |
|---|---:|---:|---:|
| Referencia 0,38 | 60,57 % | 7,14 % | 52,64 % |
| B previo | **80,46 %** | 42,91 % | 62,24 % |
| BA global | 55,94 % | 25,29 % | 58,14 % |
| BA por edad | 56,38 % | 70,16 % | 64,93 % |
| 60/40 global | 59,68 % | 8,75 % | 53,17 % |
| 60/40 por edad | 68,83 % | 46,41 % | 62,14 % |
| Minimax global | 57,18 % | 18,91 % | 56,40 % |
| Minimax por edad | 65,42 % | **65,10 %** | **65,36 %** |

**Resultado relevante:** minimax por edad evitó mínimos extremadamente bajos en ambas métricas, mientras que la referencia 0,38 conservó su prioridad de recall global pero presentó especificidad muy baja en el grupo peor situado.

### 8.3 Estabilidad de umbrales minimax

| Grupo | Mediana | P5–P95 |
|---|---:|---:|
| Global | 0,46 | 0,45–0,46 |
| Menores de 50 | 0,27 | 0,27–0,28 |
| 50–59 | 0,44 | 0,44–0,45 |
| 60–64 | 0,64 | 0,63–0,66 |

Es una estabilidad interna relativamente alta, pero **las repeticiones reutilizan registros y no miden la variación del modelo al volver a entrenarlo**.

### 8.4 Diferencias de FP y FN frente a 0,38 (promedios por evaluación)

| Política | Δ FP | Δ FN |
|---|---:|---:|
| BA global | −368 | +276 |
| BA por edad | −477 | +446 |
| 60/40 global | −67 | +50 |
| 60/40 por edad | −93 | +151 |
| Minimax global | −294 | +208 |
| Minimax por edad | −245 | +271 |

Los valores promedian **100 evaluaciones con registros reutilizados**; no representan una cohorte de 100 grupos de pacientes independientes.

## 9. Interpretación integrada y decisiones

### 9.1 Qué sí muestran los datos

- Elegir umbrales por edad modifica sustancialmente el reparto de errores entre edades.
- Los umbrales del B original fueron estables dentro de Validation, pero no conservaron de forma segura recall ≥80 % en cada evaluación separada.
- El enfoque BA global logra mayor BA agregada en B3, con una reducción importante de recall.
- Minimax global produce un balance numérico de sensibilidad y especificidad globales sin introducir umbrales etarios.
- Minimax por edad produce los mejores mínimos conjuntos por grupo entre los criterios B3 probados, pero aumenta FN respecto a la referencia.
- Mover umbrales no modifica ROC-AUC ni Brier cuando las probabilidades del modelo son idénticas.

### 9.2 Qué NO puede concluirse

- Que un umbral alternativo tenga utilidad clínica demostrada.
- Que se haya alcanzado una sensibilidad poblacional mínima de 80 % por grupo.
- Que las 100 redistribuciones sean 100 muestras independientes o una validación externa.
- Que estos resultados correspondan al artefacto final entrenado con Train + Validation.
- Que correlaciones descriptivas prueben causalidad o que las coincidencias de perfiles prueben duplicación de pacientes.
- Que se pueda seleccionar una política ganadora a posteriori sobre la misma evaluación y proclamar una mejora confirmada.

### 9.3 Estado de las decisiones

| Decisión | Estado |
|---|---|
| Mantener umbral de producción en 0,38 | **Sí, sin cambios** |
| Incorporar B (recall ≥80 % por edad) a producción | **No recomendado en esta fase** |
| Incorporar B3 a producción | **No aprobado** |
| Conservar minimax por edad como candidato de equilibrio entre subgrupos | **Sí, para investigación** |
| Conservar BA global y minimax global como referencias | **Sí** |
| Reentrenar modelos especializados (C) | **Siguiente experimento propuesto; no ejecutado aquí** |

La política final requiere una decisión explícita sobre el costo relativo de falsos positivos y falsos negativos, revisión por asesoría médica y validación adecuada. La clasificación `cardio` en este dataset no equivale a diagnóstico clínico ni riesgo futuro calibrado para una población real.

## 10. Pendientes y recomendaciones metodológicas

1. **Integridad de particiones:** profundizar en las coincidencias exactas de perfiles y documentar un análisis de sensibilidad a duplicados; evitar deducir automáticamente fuga de pacientes.
2. **Validación independiente:** reconocer que Test ya se examinó en el análisis exploratorio de subgrupos y que se necesita una evaluación nueva verdaderamente independiente para afirmaciones confirmatorias.
3. **Definir utilidad antes de elegir:** acordar con asesoría médica si prima sensibilidad, equilibrio global o protección del peor grupo; documentar consecuencias de FP y FN.
4. **Experimento C:** comparar, en un mismo protocolo, un XGBoost global contra tres XGBoost especializados; separar optimización, elección de umbral y evaluación; no transferir mecánicamente umbrales B3 a modelos con probabilidades diferentes.
5. **Discontinuidades:** si se conservan umbrales etarios, evaluar políticas suaves o límites alternativos con justificación clínica y metodológica.
6. **Reproducibilidad:** registrar dependencias y versiones, semilla, hash de dataset, hash de commit, configuración y artefactos de cada ejecución, y preservar scripts en rama experimental.

## 11. Inventario de scripts y artefactos

| Fase | Script | Resultados y documentación |
|---|---|---|
| Auditoría 2 | `experiments/age_analysis/auditoria_2.py` | `experiments/age_analysis/results/auditoria_2/` |
| B original | `experiments/age_thresholds/experimento_b.py` | `experiments/age_thresholds/results/` |
| Estabilidad B | `experiments/age_thresholds/analisis_estabilidad_b.py` | Archivos `b_*` de estabilidad en `results/` |
| B3 | `experiments/age_thresholds/experimento_b3.py` | `experiments/age_thresholds/results/b3/` |
| Estabilidad B3 | `experiments/age_thresholds/estabilidad_b3.py` | `experiments/age_thresholds/results/b3_estabilidad/` |

**Fuente de las cifras:** CSV y protocolos JSON producidos por estas ejecuciones y compartidos en la conversación. El informe resume la ejecución observada; no equivale a una nueva ejecución independiente de todo el pipeline.

## 12. Conclusión general

Desde la Auditoría 2 hasta la estabilidad de B3, la investigación mostró que el principal problema no puede formularse simplemente como «encontrar el umbral correcto». Los distintos objetivos producen intercambios distintos entre sensibilidad y especificidad, tanto globalmente como por edad. Un umbral que mejora el peor grupo puede incrementar los falsos negativos en el total, mientras que priorizar recall puede dejar la especificidad muy baja en ciertos grupos.

**Resultado documentado:** mantener PULSO v1 y el umbral 0,38; conservar B y B3 como evidencia experimental; avanzar al experimento C con un protocolo comparativo que valore calidad de probabilidades, discriminación y consecuencias de clasificación, sin atribuir validez clínica a estas pruebas exploratorias.

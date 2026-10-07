# Modelo final de PULSO y guía para integración con SHAP

## 1. Objetivo

Este documento describe el modelo de Machine Learning seleccionado como versión final de PULSO y deja la información necesaria para que el equipo encargado de explicabilidad pueda desarrollar la integración con SHAP.

El objetivo es que la implementación de SHAP utilice exactamente el mismo modelo, conjunto de variables y flujo de inferencia definidos durante las etapas de entrenamiento, tuning, calibración, selección de threshold y evaluación final.

---

## 2. Modelo seleccionado

Después de comparar los modelos:

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- Gradient Boosting

el modelo seleccionado para PULSO fue:

```text
XGBoost
```

La selección se realizó utilizando el conjunto de Validation y considerando como requisito:

```text
Recall >= 0.80
```

Entre los modelos que cumplían esta condición se priorizó el balance entre:

- Precision
- Recall
- Specificity
- F1
- ROC-AUC
- Brier Score
- Log Loss
- Expected Calibration Error (ECE)

---

## 3. Configuración final

La configuración congelada del modelo se encuentra en:

```text
ml/configs/final_model.yaml
```

Configuración actual:

```yaml
model_type: xgboost

model_params:
  colsample_bytree: 0.8
  learning_rate: 0.03
  max_depth: 3
  min_child_weight: 5
  n_estimators: 300
  reg_lambda: 5
  subsample: 0.8

  objective: binary:logistic
  eval_metric: logloss
  tree_method: hist
  random_state: 42
  n_jobs: -1

calibration:
  method: none

threshold: 0.38
```

Esta configuración debe considerarse congelada para la versión actual del modelo.

---

## 4. Calibración

Durante el desarrollo se compararon tres alternativas para cada modelo:

```text
uncalibrated
sigmoid
isotonic
```

Para XGBoost, la versión sin calibración adicional presentó el mejor comportamiento global.

Por tanto, el modelo final utiliza:

```text
calibration.method = none
```

Esto significa que las probabilidades utilizadas por PULSO corresponden directamente a las generadas por `predict_proba()` del XGBoost final.

---

## 5. Threshold de clasificación

El threshold convencional de `0.50` no es utilizado por el modelo final.

La selección del threshold se realizó sobre Validation considerando un recall mínimo de:

```text
0.80
```

El threshold seleccionado fue:

```text
0.38
```

Por tanto, la clasificación final se realiza conceptualmente mediante:

```python
prediction = int(probability >= 0.38)
```

Es importante distinguir:

```text
predict_proba()
```

produce la probabilidad del modelo, mientras que:

```text
threshold = 0.38
```

determina cómo esa probabilidad se transforma en una clasificación binaria.

SHAP debe explicar el comportamiento del modelo y sus predicciones, no el proceso de búsqueda del threshold.

---

## 6. Variables utilizadas por el modelo

El modelo final utiliza exactamente las siguientes variables:

```text
gender
height
weight
ap_hi
ap_lo
smoke
alco
active
age_years
bmi
```

Estas variables y su estructura deben conservarse durante la implementación de SHAP.

Variables excluidas del entrenamiento:

```text
id
age
cholesterol
gluc
```

Aunque algunas de estas columnas puedan existir en el dataset procesado, no forman parte de las features utilizadas por el modelo.

---

## 7. Dataset procesado

El dataset utilizado durante el desarrollo se encuentra en:

```text
data/processed/cardio_clean_v1.csv
```

Después del proceso de limpieza se conservaron:

```text
68,610 registros
```

La división utilizada fue:

```text
Train       = 48,027
Validation  = 10,291
Test        = 10,292
```

correspondiente aproximadamente a:

```text
70 % / 15 % / 15 %
```

---

## 8. Entrenamiento del modelo definitivo

Durante tuning, calibración y selección de threshold se mantuvieron separados:

```text
Train
Validation
Test
```

Una vez seleccionado y congelado el candidato definitivo, el modelo final fue nuevamente entrenado utilizando:

```text
Train + Validation
```

Número total utilizado para el refit final:

```text
58,318 registros
```

El conjunto Test permaneció separado y se utilizó únicamente para la evaluación final.

El flujo fue:

```text
Train
  +
Validation
  ↓
58,318 registros
  ↓
Refit XGBoost
  ↓
Test
10,292 registros
```

---

## 9. Evaluación final sobre Test

Resultados obtenidos con el candidato final:

```text
Model: XGBoost
Calibration: none
Threshold: 0.38
```

### Métricas

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.707928 |
| Precision | 0.671492 |
| Recall | 0.801807 |
| Specificity | 0.616035 |
| F1 | 0.730886 |
| ROC-AUC | 0.796757 |
| Brier Score | 0.182506 |
| Log Loss | 0.545384 |
| ECE | 0.012113 |

### Matriz de confusión

```text
TN = 3204
FP = 1997
FN = 1009
TP = 4082
```

El modelo mantiene en Test el requisito establecido durante la selección:

```text
Recall >= 0.80
```

Resultado:

```text
Recall = 0.801807
```

---

## 10. Script de evaluación final

La evaluación final está implementada en:

```text
ml/final_evaluate.py
```

Este script:

1. carga `final_model.yaml`;
2. carga el dataset procesado;
3. reproduce las particiones originales;
4. combina Train y Validation;
5. construye el modelo final;
6. realiza el refit;
7. obtiene probabilidades sobre Test;
8. aplica el threshold congelado de `0.38`;
9. calcula métricas;
10. genera artefactos;
11. serializa el modelo;
12. registra la ejecución en MLflow.

Puede ejecutarse mediante:

```bash
python -m ml.final_evaluate --config ml/configs/final_model.yaml
```

---

## 11. Modelo serializado

La evaluación final genera el modelo entrenado en:

```text
artifacts/final/model/pulso_xgboost.joblib
```

Este archivo contiene el modelo/pipeline entrenado que puede ser reutilizado posteriormente para inferencia y explicabilidad.

Ejemplo de carga:

```python
import joblib

model = joblib.load(
    "artifacts/final/model/pulso_xgboost.joblib"
)
```

### Importante

El directorio:

```text
artifacts/
```

puede estar incluido en `.gitignore`.

Por esta razón, el archivo `.joblib` puede no encontrarse almacenado directamente en el repositorio remoto.

En ese caso, cualquier integrante del equipo puede reconstruirlo ejecutando:

```bash
python -m ml.final_evaluate --config ml/configs/final_model.yaml
```

si dispone del dataset procesado y las dependencias correspondientes.

---

## 12. Archivos relevantes para SHAP

El equipo encargado de SHAP debe revisar principalmente:

```text
ml/configs/final_model.yaml
ml/common.py
ml/final_evaluate.py
ml/calibration.py
data/processed/cardio_clean_v1.csv
```

Y, si está disponible localmente:

```text
artifacts/final/model/pulso_xgboost.joblib
```

`ml/common.py` es particularmente importante porque contiene la construcción del pipeline utilizado por los modelos.

Antes de implementar SHAP se debe verificar la estructura exacta del objeto serializado y determinar cómo acceder al estimador `XGBClassifier` dentro del pipeline.

---

## 13. Consideraciones para SHAP

La implementación de SHAP debe utilizar el XGBoost definitivo y no volver a entrenar o seleccionar otro modelo.

El objetivo de SHAP será explicar:

### Explicabilidad global

Determinar qué variables tienen mayor influencia general sobre las predicciones del modelo.

Ejemplos de visualizaciones posibles:

```text
SHAP summary / beeswarm plot
SHAP feature importance bar plot
```

### Explicabilidad local

Explicar una predicción individual realizada para un usuario de PULSO.

Por ejemplo:

```text
Probabilidad estimada: 0.72
Threshold: 0.38
Clasificación: cardio = 1
```

SHAP deberá permitir identificar qué variables empujaron la predicción hacia una mayor o menor probabilidad.

Ejemplo conceptual:

```text
ap_hi alto       → aumenta la salida del modelo
age_years alto   → aumenta la salida del modelo
bmi alto         → aumenta la salida del modelo
active           → puede reducir la salida del modelo
```

Las direcciones reales deben obtenerse directamente de SHAP y no asumirse manualmente.

---

## 14. SHAP y threshold

El threshold no debe confundirse con la explicación SHAP.

El pipeline conceptual de inferencia es:

```text
Datos del usuario
      ↓
XGBoost
      ↓
predict_proba()
      ↓
probabilidad
      ↓
SHAP explica la salida del modelo
      ↓
threshold 0.38
      ↓
clasificación 0 / 1
```

Por tanto, SHAP explica principalmente el comportamiento del modelo asociado con la generación de la predicción/probabilidad.

El threshold es posteriormente utilizado para convertir esa probabilidad en una decisión binaria.

---

## 15. SHAP y calibración

El modelo final utiliza:

```text
calibration = none
```

Esto simplifica la integración con SHAP porque no existe una capa adicional de calibración entre XGBoost y la probabilidad utilizada por PULSO.

El equipo puede concentrarse directamente en explicar el estimador XGBoost.

---

## 16. Consideración sobre interpretación clínica

La variable objetivo del dataset es:

```text
cardio
```

y representa la clasificación:

```text
cardio = 0
cardio = 1
```

Las probabilidades producidas por el modelo deben interpretarse dentro del contexto del dataset y la población sobre la cual fue entrenado.

No deben describirse automáticamente como, por ejemplo:

```text
"riesgo cardiovascular a 10 años"
```

ya que el dataset utilizado no define un horizonte temporal prospectivo equivalente a escalas clínicas como SCORE2, PREVENT o Framingham.

Por la misma razón, las explicaciones SHAP deben presentarse como factores que influyen en la predicción del modelo y no como relaciones causales.

Por ejemplo, es apropiado indicar:

```text
"Esta variable contribuyó a aumentar la predicción del modelo."
```

No es apropiado concluir únicamente desde SHAP:

```text
"Esta variable causó el aumento del riesgo cardiovascular."
```

SHAP describe contribuciones al resultado del modelo, no causalidad clínica.

---

## 17. Estado actual del pipeline de Machine Learning

El pipeline completado hasta este punto es:

```text
Dataset
  ↓
Preparación de datos
  ↓
Split 70 / 15 / 15
  ↓
Baseline de modelos
  ↓
GridSearchCV
  ↓
Mejor configuración por modelo
  ↓
Calibración
  ├── uncalibrated
  ├── sigmoid
  └── isotonic
  ↓
Selección de threshold
  ↓
Comparación en Validation
  ↓
Selección de XGBoost
  ↓
XGBoost
calibration = none
threshold = 0.38
  ↓
Refit Train + Validation
  ↓
Evaluación única sobre Test
  ↓
Modelo definitivo
  ↓
SHAP
```

---

## 18. Resumen para el equipo de SHAP

Para comenzar el desarrollo de SHAP se debe utilizar:

```text
Modelo:
XGBoost

Configuración:
ml/configs/final_model.yaml

Modelo serializado:
artifacts/final/model/pulso_xgboost.joblib

Threshold:
0.38

Calibración:
none

Features:
gender
height
weight
ap_hi
ap_lo
smoke
alco
active
age_years
bmi

Pipeline:
ml/common.py

Dataset:
data/processed/cardio_clean_v1.csv

Entrenamiento final:
Train + Validation

Evaluación independiente:
Test

ROC-AUC Test:
0.796757

Recall Test:
0.801807
```

No se deben volver a realizar tuning, calibración o selección de threshold durante el desarrollo de SHAP.

SHAP debe construirse sobre el modelo definitivo ya seleccionado.

---

## 19. Implementación disponible

La integración está implementada en:

```text
ml/shap_explain.py
```

Para generar las explicaciones globales y locales se debe ejecutar primero la evaluación final, si el modelo serializado todavía no existe:

```bash
python -m ml.final_evaluate --config ml/configs/final_model.yaml
```

Después se ejecuta:

```bash
python -m ml.shap_explain
```

El comando utiliza Test para las explicaciones globales y una muestra de Train + Validation como referencia del explicador. Para reducir el costo computacional se explican por defecto 1,000 registros y se utilizan 1,000 registros de referencia. Estos tamaños pueden cambiarse mediante:

```bash
python -m ml.shap_explain --sample-size 500 --background-size 500
```

Los resultados se guardan en:

```text
artifacts/shap/global_feature_importance.csv
artifacts/shap/shap_bar.png
artifacts/shap/shap_summary.png
artifacts/shap/local_explanations.csv
```

La versión actual calcula SHAP en escala `raw_log_odds`, debido a la compatibilidad entre SHAP y XGBoost 3.x. La suma del valor base y las contribuciones SHAP se transforma mediante la función sigmoide y reproduce la probabilidad de `predict_proba()`. El archivo local incluye además la probabilidad, el threshold `0.38` y la clasificación resultante.
# MLOps en PULSO

## 1. Objetivo

Este documento describe las prácticas de MLOps implementadas en PULSO para garantizar reproducibilidad, trazabilidad, validación y control del ciclo de desarrollo del modelo de Machine Learning.

El objetivo actual no es implementar un sistema MLOps de producción completo, sino establecer una base reproducible y auditable para:

- preparación de datos;
- entrenamiento;
- tuning;
- calibración;
- selección de threshold;
- evaluación final;
- tracking de experimentos;
- testing;
- integración continua;
- serialización;
- versionamiento del modelo.

Las etapas relacionadas con despliegue continuo, monitoreo de drift y retraining automático quedan fuera del alcance actual del MVP y se consideran trabajo posterior.

---

## 2. Flujo general

El pipeline actual de Machine Learning de PULSO sigue el siguiente flujo:

```text id="xy0qd3"
Dataset original
      ↓
Preparación y limpieza
      ↓
Dataset procesado
      ↓
Split Train / Validation / Test
      ↓
Entrenamiento baseline
      ↓
Tuning con GridSearchCV
      ↓
Mejor candidato por algoritmo
      ↓
Evaluación de calibración
      ↓
Selección de método de calibración
      ↓
Selección de threshold
      ↓
Comparación final en Validation
      ↓
Selección del modelo definitivo
      ↓
Refit con Train + Validation
      ↓
Evaluación única sobre Test
      ↓
Serialización
      ↓
Versionamiento del modelo
```

---

## 3. Preparación reproducible de datos

El pipeline de preparación se encuentra implementado en:

```text id="nkmjvx"
ml/prepare.py
```

El dataset procesado utilizado por los modelos es:

```text id="1y6w4j"
data/processed/cardio_clean_v1.csv
```

Después del proceso de limpieza se conservaron:

```text id="j7ru52"
68,610 registros
```

Las transformaciones principales incluyen:

- filtrado de altura;
- filtrado de peso;
- filtrado de presión arterial;
- validación de `ap_hi > ap_lo`;
- creación de `age_years`;
- creación de `bmi`.

Las variables utilizadas por el modelo son:

```text id="ohcgmf"
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

Las variables excluidas del entrenamiento son:

```text id="slxb2q"
id
age
cholesterol
gluc
```

---

## 4. División de datos

Todos los modelos utilizan la misma división reproducible:

```text id="mxfxev"
Train       70 %
Validation  15 %
Test        15 %
```

Con:

```text id="astq5e"
random_state = 42
```

Para el dataset actual:

```text id="eqd8pb"
Train       = 48,027
Validation  = 10,291
Test        = 10,292
```

Esta división se mantiene constante durante todo el proceso de experimentación.

### Uso de cada partición

Train se utiliza para:

- entrenamiento;
- validación cruzada;
- tuning;
- ajuste interno de calibradores.

Validation se utiliza para:

- comparar calibraciones;
- seleccionar threshold;
- comparar candidatos finales.

Test se mantiene aislado hasta que todas las decisiones están congeladas.

---

## 5. Modelos evaluados

PULSO evalúa los siguientes clasificadores:

```text id="ldo7qt"
Logistic Regression
Decision Tree
Random Forest
XGBoost
Gradient Boosting
```

Todos utilizan el mismo contrato de entrada y la misma división de datos.

---

## 6. Configuración mediante YAML

La configuración de los modelos se separa del código mediante archivos YAML.

Esto permite:

- reproducir experimentos;
- modificar hiperparámetros sin modificar la lógica del pipeline;
- mantener trazabilidad;
- comparar candidatos;
- congelar configuraciones finales.

Las configuraciones se almacenan principalmente en:

```text id="5l8zwa"
ml/configs/
```

Los search spaces utilizados para tuning se encuentran en:

```text id="x9o4bs"
ml/configs/search_spaces/
```

Los candidatos seleccionados se almacenan en:

```text id="pnl85l"
ml/configs/candidates/
```

La configuración definitiva se encuentra en:

```text id="4fpqvj"
ml/configs/final_model.yaml
```

---

## 7. Tuning de hiperparámetros

El tuning se implementa en:

```text id="dy8jgf"
ml/tune.py
```

Se utiliza:

```text id="e1as8g"
GridSearchCV
```

con:

```text id="1vht7w"
scoring = roc_auc
```

La validación cruzada se realiza únicamente sobre Train.

Validation y Test no participan en GridSearchCV.

Durante tuning se registran:

- tipo de modelo;
- configuración;
- método de búsqueda;
- métrica;
- número de folds;
- número de candidatos;
- número de fits;
- tiempo de ejecución;
- best score;
- best parameters;
- hash del dataset.

---

## 8. Tracking de experimentos con MLflow

PULSO utiliza MLflow para registrar experimentos.

Se utilizan diferentes experimentos para separar etapas del pipeline.

### Tuning

```text id="dwan6u"
PULSO-model-tuning
```

### Calibración

```text id="87qb5i"
PULSO-calibration
```

### Threshold selection

```text id="4ri5nb"
PULSO-threshold-selection
```

### Evaluación final

```text id="ibfc4p"
PULSO-final-evaluation
```

MLflow registra:

- parámetros;
- métricas;
- configuraciones YAML;
- artefactos;
- resultados CSV;
- gráficos;
- hash del dataset.

Esto permite reconstruir y comparar ejecuciones.

---

## 9. Fingerprinting del dataset

Para garantizar trazabilidad del dataset se utiliza SHA-256.

El hash del dataset procesado utilizado para el modelo final es:

```text id="3txek9"
16f4beca139c5e0be6a6a7e1df41e1d08d047d6897c218afb7df666c2248eb91
```

Este hash identifica de manera única el archivo:

```text id="fyvxlg"
data/processed/cardio_clean_v1.csv
```

Si el archivo cambia, el hash también cambia.

Esto permite asociar una versión del modelo con el dataset exacto utilizado para entrenarla.

---

## 10. Calibración de probabilidades

Después del tuning se evalúa la calidad probabilística de cada candidato.

Los métodos comparados son:

```text id="f7aiub"
uncalibrated
sigmoid
isotonic
```

Las métricas utilizadas incluyen:

- Brier Score;
- Log Loss;
- Expected Calibration Error;
- ROC-AUC como métrica de control.

La calibración se implementa mediante:

```text id="a1q0so"
ml/calibration.py
ml/calibrate.py
```

El método seleccionado queda almacenado en el YAML del candidato.

Ejemplo:

```yaml id="bjtgzv"
calibration:
  method: isotonic
  cv: 5
  ensemble: false
```

o:

```yaml id="6x6nc3"
calibration:
  method: none
```

No se fuerza calibración si el modelo original presenta mejores resultados.

---

## 11. Selección de threshold

La selección del threshold se encuentra implementada mediante:

```text id="x4s1qj"
ml/threshold.py
ml/select_threshold.py
```

El criterio definido es:

```text id="tue3k0"
Recall mínimo = 0.80
```

Entre los thresholds que cumplen el recall mínimo se prioriza Precision.

El threshold se selecciona únicamente sobre Validation.

El Test no se utiliza para ajustar esta decisión.

---

## 12. Selección del modelo definitivo

Después de tuning, calibración y threshold selection se compararon los cinco modelos.

El modelo seleccionado fue:

```text id="glfz9b"
XGBoost
```

Configuración final:

```text id="g2k9s6"
Calibration = none
Threshold = 0.38
```

El candidato definitivo se encuentra congelado en:

```text id="tn08ls"
ml/configs/final_model.yaml
```

---

## 13. Refit final

Después de congelar:

- algoritmo;
- hiperparámetros;
- calibración;
- threshold;

se combinaron Train y Validation.

Resultado:

```text id="h2ocjj"
48,027 + 10,291 = 58,318 registros
```

El modelo definitivo fue entrenado con:

```text id="rrkp0l"
Train + Validation
```

Test permaneció completamente separado.

---

## 14. Evaluación final

La evaluación final se implementa en:

```text id="owjlv4"
ml/final_evaluate.py
```

El Test se utilizó una única vez después de congelar todas las decisiones.

Resultados:

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

Matriz de confusión:

```text id="y4a48g"
TN = 3204
FP = 1997
FN = 1009
TP = 4082
```

El requisito definido durante selección se mantiene en Test:

```text id="pb5m8y"
Recall >= 0.80
```

---

## 15. Serialización

El modelo final se serializa utilizando `joblib`.

Ruta generada:

```text id="lil9nd"
artifacts/final/model/pulso_xgboost.joblib
```

Este archivo contiene el modelo entrenado que posteriormente puede ser utilizado por:

- API de inferencia;
- SHAP;
- simulaciones;
- integración con el backend.

El directorio `artifacts/` puede permanecer excluido de Git.

El modelo puede reconstruirse mediante:

```bash id="bure8k"
python -m ml.final_evaluate --config ml/configs/final_model.yaml
```

---

## 16. Versionamiento del modelo

PULSO mantiene una separación entre:

```text id="rmnrhx"
experimentos
candidatos
versiones oficiales
```

### Experimentos

Son ejecuciones realizadas durante:

- baseline;
- tuning;
- calibración;
- comparación de modelos.

Estos se rastrean mediante MLflow.

### Candidatos

Son las mejores configuraciones obtenidas para cada algoritmo.

Se mantienen en:

```text id="h7x01o"
ml/configs/candidates/
```

### Versiones oficiales

Una versión se crea cuando un modelo es seleccionado como candidato definitivo para PULSO.

La estructura utilizada es:

```text id="e3nqrj"
models/
└── pulso/
    └── v1/
        ├── final_model.yaml
        ├── metadata.yaml
        └── README.md
```

La versión actual es:

```text id="d0pb71"
PULSO v1
```

Algoritmo:

```text id="86r381"
XGBoost
```

---

## 17. Metadata del modelo

Cada versión oficial incluye metadata para garantizar trazabilidad.

Ejemplo:

```yaml id="2rsgt5"
model:
  name: pulso
  version: 1
  algorithm: xgboost
  status: final

dataset:
  name: cardio_clean_v1
  sha256: 16f4beca139c5e0be6a6a7e1df41e1d08d047d6897c218afb7df666c2248eb91

training:
  random_state: 42
  refit_strategy: train_plus_validation

selection:
  calibration: none
  threshold: 0.38
```

También se registran:

- features;
- métricas;
- matriz de confusión;
- tamaño de particiones;
- ubicación de artefactos;
- experimento MLflow.

---

## 18. Trazabilidad del código

Además del hash del dataset, se recomienda asociar cada versión del modelo al commit de Git utilizado para generarla.

El commit puede obtenerse mediante:

```bash id="8ib9lb"
git rev-parse HEAD
```

Y almacenarse en:

```yaml id="gv2gxd"
code:
  git_commit: "<commit-hash>"
```

Esto permite reconstruir:

```text id="1qfnmh"
modelo
→ configuración
→ dataset
→ código
```

---

## 19. Dependencias y entorno

Las dependencias utilizadas por el pipeline de Machine Learning se mantienen en:

```text id="eprvmb"
requirements-ml.txt
```

El entorno de CI utiliza:

```text id="np0p9d"
Python 3.11
```

La instalación se realiza mediante:

```bash id="36iwlo"
python -m pip install -r requirements-ml.txt
```

---

## 20. Tests unitarios

PULSO cuenta con pruebas unitarias para componentes individuales del pipeline.

Se validan, entre otros:

- carga de dataset;
- exclusión de features;
- particiones;
- métricas;
- threshold;
- calibración;
- ECE;
- evaluación probabilística;
- construcción del modelo final.

Los tests utilizan datos sintéticos para evitar depender del dataset real.

---

## 21. Tests de integración

También existen pruebas de integración que verifican flujos completos.

Entre ellas:

```text id="1vjd30"
modelo
→ entrenamiento
→ evaluación
```

```text id="0vdkhk"
modelo
→ calibración
→ threshold
```

```text id="spx603"
config final
→ refit
→ evaluación
→ artefactos
→ serialización
```

Los cinco clasificadores soportados se prueban en las etapas correspondientes.

---

## 22. Integración continua

PULSO utiliza GitHub Actions para ejecutar automáticamente la suite de pruebas.

Workflow:

```text id="kpw3nb"
.github/workflows/ml-training-ci.yml
```

El workflow:

1. descarga el repositorio;
2. configura Python;
3. instala `requirements-ml.txt`;
4. ejecuta pytest.

Comando:

```bash id="pe8gtp"
python -m pytest -q tests
```

El CI utiliza datos sintéticos y no:

- descarga el dataset real;
- ejecuta tuning completo;
- entrena modelos finales.

Esto mantiene el workflow rápido y reproducible.

Actualmente el CI puede ejecutarse en:

```text id="hwpjvj"
Pull Requests
manual workflow_dispatch
```

Se recomienda también ejecutarlo después de `push` a `main`.

---

## 23. Estado actual de MLOps

### Implementado

```text id="qgyd5j"
✅ Preparación reproducible de datos
✅ Configuración mediante YAML
✅ Split reproducible
✅ Entrenamiento reproducible
✅ Tuning
✅ MLflow tracking
✅ Dataset fingerprinting
✅ Calibración
✅ Threshold selection
✅ Evaluación final independiente
✅ Serialización del modelo
✅ Tests unitarios
✅ Tests de integración
✅ CI
✅ Configuración final congelada
✅ Versionamiento de modelo
✅ Metadata de modelo
```

### Pendiente

```text id="59gbt9"
❌ Continuous Deployment
❌ Monitoring de producción
❌ Data drift detection
❌ Prediction drift monitoring
❌ Model performance monitoring
❌ Retraining automático
❌ Rollback automatizado
```

---

## 24. Continuous Deployment

CD todavía no se encuentra implementado.

Se integrará cuando PULSO disponga de una arquitectura desplegable con:

```text id="97duzi"
Frontend
Backend
ML Service
RAG Service
Reverse Proxy
Docker
```

Un posible flujo futuro será:

```text id="jsyhj7"
Merge a main
      ↓
Tests
      ↓
Build Docker images
      ↓
Deploy
      ↓
Health checks
```

---

## 25. Monitoring

El monitoreo en producción todavía no se encuentra implementado.

Cuando la API de PULSO esté desplegada, se recomienda registrar por inferencia:

```text id="ap6zlw"
timestamp
model_version
predicted_probability
prediction
input statistics
```

No se recomienda almacenar información sensible sin una política explícita de privacidad y tratamiento de datos.

---

## 26. Data drift

La detección de drift queda pendiente para una etapa futura.

Las distribuciones de producción podrían compararse con las utilizadas durante entrenamiento para variables como:

```text id="godve2"
age_years
bmi
ap_hi
ap_lo
height
weight
```

El objetivo sería detectar cambios relevantes en la población atendida por el sistema.

---

## 27. Model drift

Para detectar degradación del desempeño sería necesario disponer posteriormente de labels reales.

Se podrían comparar métricas históricas contra nuevas observaciones para detectar:

```text id="hg9p2y"
reducción de recall
reducción de precision
cambios de ROC-AUC
degradación de calibración
```

Actualmente PULSO no dispone de este flujo.

---

## 28. Retraining

El retraining automático no forma parte del MVP actual.

Actualmente el dataset es estático.

Una estrategia futura podría activar retraining cuando:

- exista una nueva versión del dataset;
- se detecte drift;
- disminuya el desempeño;
- cambien los requerimientos del sistema.

Cada retraining exitoso debería generar una nueva versión:

```text id="iqlhtr"
PULSO v2
PULSO v3
...
```

sin sobrescribir versiones anteriores.

---

## 29. Rollback

Actualmente existe únicamente:

```text id="ag3xwx"
PULSO v1
```

Cuando existan nuevas versiones, la estructura de versionamiento permitirá conservar versiones anteriores.

Ejemplo:

```text id="4dnlfh"
models/pulso/
├── v1/
└── v2/
```

Esto facilitará un rollback manual si una versión posterior presenta problemas.

La automatización del rollback queda fuera del alcance actual.

---

## 30. Relación con SHAP

SHAP debe utilizar la versión oficial del modelo:

```text id="tw6qwm"
PULSO v1
```

No debe realizar tuning adicional ni modificar:

```text id="ac3ki9"
features
hyperparameters
calibration
threshold
```

Documentación específica:

```text id="gj4zm6"
docs/MODELO_FINAL_Y_GUIA_SHAP.md
```

---

## 31. Reproducibilidad

Para reconstruir el entorno y ejecutar las pruebas:

```bash id="dgxmvi"
python -m venv .venv
```

Activar el entorno.

En Windows:

```powershell id="42i9de"
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```bash id="4jh1v1"
python -m pip install -r requirements-ml.txt
```

Ejecutar tests:

```bash id="878xve"
python -m pytest -q tests
```

Ejecutar evaluación final:

```bash id="f7lqgq"
python -m ml.final_evaluate --config ml/configs/final_model.yaml
```

---

## 32. Conclusión

PULSO cuenta actualmente con una infraestructura MLOps funcional enfocada en:

- reproducibilidad;
- trazabilidad;
- control de experimentos;
- testing;
- CI;
- versionamiento;
- evaluación independiente;
- serialización.

El sistema todavía no constituye un ciclo MLOps completo de producción, ya que no incorpora deployment automático, monitoring, drift detection ni retraining.

Estas capacidades se incorporarán progresivamente a medida que el modelo se integre con los servicios de PULSO y el sistema avance hacia despliegue.
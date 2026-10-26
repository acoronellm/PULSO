# PULSO — Fase 1: auditoría exploratoria de edades

**Objetivo:** comprobar si los cortes de edad actuales son viables estadísticamente antes de desarrollar B (un modelo con umbrales por edad) y C (tres modelos especializados). Este script **no entrena**, **no cambia el artefacto v1**, **no toca Test para decidir grupos** y **no determina categorías de riesgo clínico**.

## Cómo incorporarlo

1. En una rama experimental limpia, crear `experiments/age_analysis/`.
2. Copiar `analizar_edades.py` a esa carpeta. Ejecutar desde la **raíz de PULSO**:
   ```powershell
   python experiments/age_analysis/analizar_edades.py
   ```
3. Requiere el entorno de PULSO con `pandas`, `numpy`, `scikit-learn`, `matplotlib` y `xgboost`, así como `ml/common.py` y `data/processed/cardio_clean_v1.csv`.

## Archivos de salida

En `experiments/age_analysis/results/`:

- `edades_por_ano_desarrollo.csv`: distribución, clases y prevalencia por edad cumplida.
- `edades_cada_5_anos_desarrollo.csv`: lo mismo por intervalo quinquenal, con IC 95 % Wilson descriptivos.
- `comparacion_grupos_candidatos.csv`: tamaños y balance de clases de dos esquemas: `<50 / 50–59 / ≥60` y `<50 / 50–69 / ≥70`.
- `01_distribucion_edades.png`: histograma de registros por edad.
- `02_prevalencia_cinco_anos.png`: prevalencia y bandas de incertidumbre por cinco años.
- `03_balance_grupos_candidatos.png`: positivos y negativos disponibles por segmento.
- `resumen_auditoria.txt`: tamaños de partición, rango de edades, prevalencia y duplicados exactos en desarrollo.

## Interpretación y siguientes decisiones

- Los tamaños de Test de la evaluación previa **no** son los tamaños con los que se entrenarían tres modelos; el diseño usa únicamente Train+Validation.
- El criterio de alerta de **menos de 100 registros de alguna clase** es orientativo, no un tamaño muestral suficiente garantizado para entrenar XGBoost.
- Tras revisar los CSV y las gráficas, contrastar los cortes con la asesora médica. Los grupos de guías de riesgo cardiovascular futuro no son automáticamente adecuados para la etiqueta transversal `cardio`.
- Al definir los cortes, revisar `ml/train.py` y `ml/tune.py` para diseñar validación cruzada, selección de umbrales fuera de muestra y ajuste de modelos especializados sin fuga de datos.
- No incorporar cambios experimentales al PULSO v1 desplegado. Si se publica una versión nueva, exigir evaluación final independiente.

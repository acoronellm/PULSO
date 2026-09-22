# Preparación de datos de PULSO

## Dataset

- Fuente: [URL del dataset].
- Archivo original: `data/raw/cardio_train.csv`.
- Archivo depurado: `data/processed/cardio_clean_v1.csv`.

## Análisis exploratorio

El EDA se encuentra documentado en los tres notebooks de `notebooks/eda/`.

## Criterios de depuración

- Estatura entre 120 y 220 cm.
- Peso entre 30 y 200 kg.
- Presión sistólica entre 70 y 250 mmHg.
- Presión diastólica entre 40 y 150 mmHg.
- Presión sistólica superior a la diastólica.

## Variables derivadas

- `age_years = age / 365.25`
- `bmi = weight / ((height / 100) ** 2)`

## Variables conservadas

Las columnas `cholesterol` y `gluc` permanecen en el dataset depurado, pero serán excluidas inicialmente del entrenamiento debido a la falta de documentación suficiente sobre el significado de sus categorías.

## Reproducibilidad

El archivo depurado se genera ejecutando:

`python ml/prepare.py`
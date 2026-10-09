import os
from pathlib import Path


# Raíz del repositorio PULSO.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Artefacto serializado del modelo final.
#
# Puede sobrescribirse con PULSO_MODEL_PATH cuando posteriormente
# el servicio se ejecute dentro de Docker.
MODEL_PATH = Path(
    os.getenv(
        "PULSO_MODEL_PATH",
        PROJECT_ROOT
        / "artifacts"
        / "final"
        / "model"
        / "pulso_xgboost.joblib",
    )
)


# Versión oficial del modelo desplegado.
MODEL_VERSION = "v1"


# Threshold final seleccionado utilizando Validation.
MODEL_THRESHOLD = 0.38


# Orden exacto de variables esperado por PULSO v1.
FEATURES = (
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "smoke",
    "alco",
    "active",
    "age_years",
    "bmi",
)
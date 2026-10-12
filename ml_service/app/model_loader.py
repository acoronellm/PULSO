from functools import lru_cache

import joblib

from .config import MODEL_PATH


@lru_cache(maxsize=1)
def load_model():
    """
    Carga el modelo final de PULSO una sola vez.

    Returns:
        Modelo serializado listo para inferencia.

    Raises:
        FileNotFoundError:
            Si el artefacto del modelo no existe.
        RuntimeError:
            Si el archivo existe pero no puede cargarse.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo de PULSO en: {MODEL_PATH}"
        )

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as exc:
        raise RuntimeError(
            f"No fue posible cargar el modelo desde: {MODEL_PATH}"
        ) from exc

    return model
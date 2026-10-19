from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


RANDOM_STATE = 42

FEATURES = [
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
]

TARGET = "cardio"


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cardio_train.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "analysis"
    / "final_xgboost"
    / "outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Data loading and cleaning
# ---------------------------------------------------------

def load_and_clean_data() -> pd.DataFrame:
    """
    Carga cardio_train.csv y aplica la misma depuración
    utilizada para el dataset final de PULSO.
    """

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en: "
            f"{RAW_DATA_PATH}"
        )

    # El dataset original de Kaggle utiliza ';'
    df = pd.read_csv(
        RAW_DATA_PATH,
        sep=";",
    )

    print(
        f"Registros originales: {len(df):,}"
    )

    # Edad expresada en años
    df["age_years"] = (
        df["age"] / 365.25
    )

    # Filtros utilizados en PULSO
    df = df[
        df["height"].between(
            120,
            220,
        )
        & df["weight"].between(
            30,
            200,
        )
        & df["ap_hi"].between(
            70,
            250,
        )
        & df["ap_lo"].between(
            40,
            150,
        )
        & (
            df["ap_hi"]
            > df["ap_lo"]
        )
    ].copy()

    # BMI
    height_m = (
        df["height"] / 100
    )

    df["bmi"] = (
        df["weight"]
        / (height_m ** 2)
    )

    # Conservar únicamente las variables
    # utilizadas por PULSO + target
    df = df[
        FEATURES + [TARGET]
    ].copy()

    df = df.reset_index(
        drop=True
    )

    print(
        f"Registros después de depuración: "
        f"{len(df):,}"
    )

    return df


# ---------------------------------------------------------
# Train / Validation / Test
# ---------------------------------------------------------

def create_splits(
    df: pd.DataFrame,
):
    """
    División estratificada:

    Train      70 %
    Validation 15 %
    Test       15 %

    random_state = 42
    """

    X = df[FEATURES]
    y = df[TARGET]

    # Primera división:
    # 70 % train / 30 % temporal
    (
        X_train,
        X_temp,
        y_train,
        y_temp,
    ) = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Segunda división:
    # 15 % validation / 15 % test
    (
        X_validation,
        X_test,
        y_validation,
        y_test,
    ) = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    return {
        "total": (X, y),
        "train": (
            X_train,
            y_train,
        ),
        "validation": (
            X_validation,
            y_validation,
        ),
        "test": (
            X_test,
            y_test,
        ),
    }


# ---------------------------------------------------------
# Prevalence
# ---------------------------------------------------------

def calculate_prevalence(
    splits: dict,
) -> pd.DataFrame:
    """
    Calcula cantidad de cardio=0, cardio=1
    y prevalencia de cardio=1.
    """

    results = []

    for split_name, (_, y) in splits.items():

        total = len(y)

        cardio_0 = int(
            (y == 0).sum()
        )

        cardio_1 = int(
            (y == 1).sum()
        )

        prevalence = (
            cardio_1 / total
        )

        results.append(
            {
                "split": split_name,
                "n": total,
                "cardio_0": cardio_0,
                "cardio_1": cardio_1,
                "prevalence": prevalence,
                "prevalence_percent": (
                    prevalence * 100
                ),
            }
        )

    return pd.DataFrame(
        results
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    df = load_and_clean_data()

    splits = create_splits(df)

    prevalence_df = (
        calculate_prevalence(
            splits
        )
    )

    output_path = (
        OUTPUT_DIR
        / "prevalence.csv"
    )

    prevalence_df.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        "=== PREVALENCIA DE CARDIO = 1 ==="
    )
    print()

    display_df = (
        prevalence_df.copy()
    )

    display_df[
        "prevalence"
    ] = display_df[
        "prevalence"
    ].map(
        lambda value: f"{value:.4f}"
    )

    display_df[
        "prevalence_percent"
    ] = display_df[
        "prevalence_percent"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    print(
        display_df.to_string(
            index=False
        )
    )

    print()
    print(
        f"Resultados guardados en:"
    )
    print(
        output_path
    )


if __name__ == "__main__":
    main()
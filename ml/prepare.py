from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw" / "cardio_train.csv"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "cardio_clean_v1.csv"
REQUIRED_COLUMNS = ("height", "weight", "ap_hi", "ap_lo", "age")


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica las mismas reglas de filtrado y variables derivadas del notebook."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas necesarias: {', '.join(missing)}")

    valid_mask = (
        df["height"].between(120, 220)
        & df["weight"].between(30, 200)
        & df["ap_hi"].between(70, 250)
        & df["ap_lo"].between(40, 150)
        & (df["ap_hi"] > df["ap_lo"])
    )
    clean = df.loc[valid_mask].copy()
    clean["age_years"] = clean["age"] / 365.25
    clean["bmi"] = clean["weight"] / ((clean["height"] / 100) ** 2)
    return clean


def main() -> None:
    parser = argparse.ArgumentParser(description="Depura el dataset de PULSO.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV original; separador ';'.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV depurado de salida.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--verify", action="store_true", help="Compara con el CSV existente sin escribirlo.")
    action.add_argument("--overwrite", action="store_true", help="Autoriza reemplazar el CSV existente.")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"No se encuentra el CSV original: {args.input}")

    original = pd.read_csv(args.input, sep=";")
    clean = prepare_data(original)
    print(f"Registros originales: {len(original)}")
    print(f"Registros conservados: {len(clean)}")
    print(f"Registros excluidos: {len(original) - len(clean)}")
    print(f"Columnas de salida: {len(clean.columns)}")

    if args.verify:
        if not args.output.is_file():
            parser.error(f"No existe el CSV para comparar: {args.output}")
        existing = pd.read_csv(args.output)
        # La lectura del CSV puede introducir pequeñas diferencias de coma flotante.
        assert_frame_equal(
            clean.reset_index(drop=True),
            existing.reset_index(drop=True),
            check_dtype=False,
            check_exact=False,
            rtol=1e-12,
            atol=1e-12,
        )
        print("Verificación correcta: los datos coinciden dentro de la tolerancia numérica.")
        return

    if args.output.exists() and not args.overwrite:
        parser.error(
            f"El archivo ya existe: {args.output}. "
            "Usa --verify para compararlo o --overwrite para reemplazarlo."
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.output, index=False)
    print(f"CSV depurado guardado en: {args.output}")


if __name__ == "__main__":
    main()
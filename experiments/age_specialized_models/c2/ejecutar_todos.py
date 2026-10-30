"""Ejecuta secuencialmente los 15 entrenamientos por edad de PULSO C2 v2.

Ubicación en repo: experiments/age_specialized_models/c2/ejecutar_todos.py
Ejecutar: python -m experiments.age_specialized_models.c2.ejecutar_todos
Reanudar: ejecutar el mismo comando; omite trabajos con artefactos completos.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "age_specialized_models" / "c2"
RESULTS = ROOT / "experiments" / "age_specialized_models" / "results" / "c2_v2"
LOGS = RESULTS / "_batch_logs"
ALGORITHMS = (
    "logistic_regression", "decision_tree", "random_forest",
    "gradient_boosting", "xgboost",
)
GROUPS = ("menor_50", "50_59", "60_64")
REQUIRED_ARTIFACTS = ("manifest.json", "resumen.json", "modelo_experimental.joblib", "cv_candidatos.csv", "cv_folds.csv")


def status(algorithm: str, group: str) -> str:
    folder = RESULTS / algorithm / group
    if not folder.exists():
        return "pendiente"
    if not all((folder / name).is_file() for name in REQUIRED_ARTIFACTS):
        return "incompleto"
    try:
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        report = json.loads((folder / "resumen.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "incompleto"
    if (manifest.get("algoritmo"), manifest.get("grupo")) != (algorithm, group):
        return "incompleto"
    if (report.get("algoritmo"), report.get("grupo")) != (algorithm, group):
        return "incompleto"
    if not manifest.get("mlflow_run_id") or not report.get("mlflow_run_id"):
        return "incompleto"
    return "completado"


def save_summary(rows: list[dict]) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    output = LOGS / "resumen_lote.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=("algoritmo", "grupo", "estado", "duracion_segundos", "log"))
        writer.writeheader()
        writer.writerows(rows)


def run_one(algorithm: str, group: str, index: int, total: int) -> tuple[int, Path, float]:
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"{algorithm}__{group}.log"
    command = [sys.executable, "-u", "-m", f"experiments.age_specialized_models.c2.entrenar_{algorithm}", "--grupo", group]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    print(f"\n{'='*72}\n[{index}/{total}] {algorithm} / {group}\nComando: {' '.join(command)}\nLog: {log_path}\n{'='*72}", flush=True)
    start = time.monotonic()
    with log_path.open("wb") as log:
        proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
        try:
            assert proc.stdout is not None
            while True:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                log.write(chunk)
                log.flush()
                if hasattr(sys.stdout, "buffer"):
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                else:
                    sys.stdout.write(chunk.decode("utf-8", errors="replace"))
                    sys.stdout.flush()
            exit_code = proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            raise
    return exit_code, log_path, time.monotonic() - start


def main() -> int:
    parser = argparse.ArgumentParser(description="Ejecuta secuencialmente solo los entrenamientos por edad C2 v2 de PULSO")
    parser.add_argument("--solo-algoritmo", choices=ALGORITHMS, help="Opcional: limitar a un algoritmo")
    parser.add_argument("--solo-grupo", choices=GROUPS, help="Opcional: limitar a un rango")
    parser.add_argument("--continuar-si-falla", action="store_true", help="Continúa con otros trabajos si uno falla")
    parser.add_argument("--dry-run", action="store_true", help="Muestra el plan sin entrenar")
    args = parser.parse_args()

    if not (ROOT / "ml" / "common.py").is_file() or not BASE.is_dir():
        print(f"ERROR: No se reconoce la estructura del repositorio PULSO en {ROOT}", file=sys.stderr)
        return 2
    jobs = [(a, g) for a in ALGORITHMS for g in GROUPS
            if (not args.solo_algoritmo or a == args.solo_algoritmo)
            and (not args.solo_grupo or g == args.solo_grupo)]
    print(f"PULSO C2 v2 | {len(jobs)} trabajos | Python: {sys.executable}")
    print(f"Resultados: {RESULTS}")
    for a, g in jobs:
        print(f"  {a:23s} {g:9s} {status(a, g)}")
    if args.dry_run:
        return 0

    rows: list[dict] = []
    failures = 0
    for idx, (a, g) in enumerate(jobs, 1):
        current = status(a, g)
        if current == "completado":
            print(f"[{idx}/{len(jobs)}] OMITIDO: {a} / {g} (artefactos completos)", flush=True)
            rows.append(dict(algoritmo=a, grupo=g, estado="omitido_completado", duracion_segundos=0, log=""))
            save_summary(rows)
            continue
        if current == "incompleto":
            print(f"ERROR: Hay una carpeta parcial en {RESULTS / a / g}. No se eliminará ni sobrescribirá.", file=sys.stderr)
            rows.append(dict(algoritmo=a, grupo=g, estado="carpeta_incompleta", duracion_segundos=0, log=""))
            save_summary(rows)
            failures += 1
            if not args.continuar_si_falla:
                return 1
            continue
        try:
            exit_code, log, duration = run_one(a, g, idx, len(jobs))
        except KeyboardInterrupt:
            print("\nInterrumpido. Los entrenamientos completados se conservaron. Ejecuta de nuevo para reanudar.", file=sys.stderr)
            save_summary(rows)
            return 130
        completed = status(a, g) == "completado"
        success = exit_code == 0 and completed
        state = "correcto" if success else f"fallo_exit_{exit_code}" if exit_code else "artefactos_incompletos"
        print(f"\nResultado {a}/{g}: {state} ({duration:.1f} s)", flush=True)
        rows.append(dict(algoritmo=a, grupo=g, estado=state, duracion_segundos=round(duration, 2), log=str(log.relative_to(ROOT))))
        save_summary(rows)
        if not success:
            failures += 1
            print(f"Revisa el log: {log}", file=sys.stderr)
            if not args.continuar_si_falla:
                return 1
    print(f"\nLote finalizado: {len(jobs)-failures} sin errores de ejecución/pendientes resueltos, {failures} con problemas.")
    print(f"Resumen: {LOGS / 'resumen_lote.csv'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

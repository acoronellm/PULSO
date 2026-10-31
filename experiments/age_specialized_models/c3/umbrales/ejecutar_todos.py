"""Ejecución secuencial de las seis combinaciones de C3-umbrales."""
import argparse
import subprocess
import sys
from pathlib import Path
from .motor_umbrales import OUT_ROOT, ALGORITHMS, GROUPS

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    jobs=[(a,g) for a in ALGORITHMS for g in GROUPS]
    for i,(alg,group) in enumerate(jobs,1):
        out=OUT_ROOT/alg/group
        required=['umbrales_seleccionados.csv','metricas_evaluacion.csv','curvas_seleccion.csv','protocolo.json']
        complete=out.is_dir() and all((out/f).is_file() for f in required)
        state='COMPLETADO' if complete else 'INCOMPLETO' if out.exists() else 'PENDIENTE'
        print(f'[{i}/6] {alg} {group}: {state}',flush=True)
        if args.dry_run or complete:continue
        if out.exists():raise RuntimeError(f'Resultados incompletos: {out}; revisar antes de reanudar')
        subprocess.run([sys.executable,'-m',f'experiments.age_specialized_models.c3.umbrales.evaluar_{alg}',
                        '--grupo',group],check=True)

if __name__=='__main__':main()

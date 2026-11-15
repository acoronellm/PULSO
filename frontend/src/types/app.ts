// Pantallas de PULSO v1: no hay cuentas ni historial
export type View = "evaluacion" | "resultado" | "simulacion";

export type Navigate = (path: View) => void;

export function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

export function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === "AbortError";
}

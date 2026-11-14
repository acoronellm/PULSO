export type View = "evaluacion" | "resultado" | "simulacion" | "historial";

export type Navigate = (path: View) => void;

export function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

export function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === "AbortError";
}

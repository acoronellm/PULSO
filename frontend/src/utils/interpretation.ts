import type { Binary, Prediction } from "../types/pulso";
import { formatProbability, formatThreshold } from "./health";

// Basta con la clase para las etiquetas cortas (por ejemplo, en la simulación)
type Classified = Pick<Prediction, "classification">;

// El perfil pertenece al grupo de cardio = 1 cuando la probabilidad es igual o superior
// al umbral; el backend ya lo resuelve en prediction.classification.
function isAboveThreshold(prediction: Classified): boolean {
  return prediction.classification === 1;
}

const GROUP_WITH = "grupo que representa a las personas registradas con enfermedad cardiovascular";
const GROUP_WITHOUT = "grupo que representa a las personas registradas sin enfermedad cardiovascular";

export const THRESHOLD_EXPLANATION =
  "El umbral es el punto de referencia que utiliza PULSO para decidir a cuál de los dos grupos asignar tu perfil.";

// Etiqueta corta para chips y tarjetas, sin términos técnicos
export function thresholdLabel(prediction: { classification: Binary }): string {
  return isAboveThreshold(prediction) ? "Igual o superior al umbral" : "Por debajo del umbral";
}

export function resultSummary(prediction: Prediction): string {
  const probability = formatProbability(prediction.probability);
  const threshold = formatThreshold(prediction.threshold);
  const position = isAboveThreshold(prediction) ? "igual o superior al" : "por debajo del";
  // Espacio no separable para que el número y el % no queden en líneas distintas
  return `Al analizar tus datos, PULSO obtuvo una estimación del ${probability}\u00a0%, ${position} umbral de clasificación del ${threshold}\u00a0%.`;
}

export function groupExplanation(prediction: Prediction): string {
  if (isAboveThreshold(prediction)) {
    return `Como tu resultado es igual o superior a ese valor, el modelo asignó tu perfil al ${GROUP_WITH} en los datos utilizados para su entrenamiento.`;
  }
  return `Como tu resultado está por debajo de ese valor, el modelo asignó tu perfil al ${GROUP_WITHOUT} en los datos utilizados para su entrenamiento.`;
}

export function importantNote(prediction: Prediction): string {
  const scope = "PULSO ofrece una estimación estadística con fines educativos y preventivos, no un diagnóstico médico.";
  if (isAboveThreshold(prediction)) {
    return `Esto no confirma que tengas una enfermedad cardiovascular ni indica un riesgo clínico individual determinado. ${scope}`;
  }
  return `Esto no significa que estés libre de enfermedades cardiovasculares. ${scope}`;
}

// Detalle técnico para la sección secundaria "Detalles del modelo"
export function technicalDetail(prediction: Prediction): string {
  const threshold = String(prediction.threshold);
  const assigned = isAboveThreshold(prediction) ? "cardio = 1" : "cardio = 0";
  return `Modelo XGBoost de clasificación binaria. El porcentaje es la probabilidad estimada para la clase cardio = 1. El perfil se asigna a cardio = 1 cuando esa probabilidad es igual o superior al umbral (${threshold}); en este caso se asignó a ${assigned}.`;
}

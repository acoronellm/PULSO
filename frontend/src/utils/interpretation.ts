
import type { Binary, Prediction } from "../types/pulso";
import { formatProbability, formatThreshold } from "./health";

type Classified = Pick<Prediction, "classification">;

function isAboveThreshold(prediction: Classified): boolean {
  return prediction.classification === 1;
}

const GROUP_WITH =
  "grupo que representa a las personas registradas con enfermedad cardiovascular en los datos de entrenamiento";

const GROUP_WITHOUT =
  "grupo que representa a las personas registradas sin enfermedad cardiovascular en los datos de entrenamiento";

export const THRESHOLD_EXPLANATION =
  "El umbral de clasificación es el valor que utiliza PULSO para asignar cada perfil a uno de los dos grupos.";

export function thresholdLabel(
  prediction: { classification: Binary }
): string {
  return isAboveThreshold(prediction)
    ? "Igual o superior al umbral"
    : "Por debajo del umbral";
}

export function resultSummary(prediction: Prediction): string {
  const probability = formatProbability(prediction.probability);

  return `Según los datos que ingresaste, PULSO estimó una probabilidad del ${probability}\u00a0% de pertenecer al grupo de personas registradas con enfermedad cardiovascular en los datos con los que se entrenó el modelo.`;
}

export function groupExplanation(prediction: Prediction): string {
  const threshold = formatThreshold(prediction.threshold);

  if (isAboveThreshold(prediction)) {
    return (
      `Como tu resultado es igual o superior al ${threshold}\u00a0%, ` +
      `el modelo asignó tu perfil al ${GROUP_WITH}.`
    );
  }

  return (
    `Como tu resultado está por debajo del ${threshold}\u00a0%, ` +
    `el modelo asignó tu perfil al ${GROUP_WITHOUT}.`
  );
}

export function importantNote(prediction: Prediction): string {
  const scope =
    "PULSO ofrece una estimación estadística con fines educativos " +
    "y preventivos, no un diagnóstico médico.";

  if (isAboveThreshold(prediction)) {
    return (
      "Esto no confirma que tengas una enfermedad cardiovascular " +
      "ni representa una valoración clínica individual. " +
      scope
    );
  }

  return (
    "Esto no significa que estés libre de enfermedades " +
    "cardiovasculares. " +
    scope
  );
}

export function technicalDetail(prediction: Prediction): string {
  const threshold = String(prediction.threshold);
  const assigned = isAboveThreshold(prediction)
    ? "cardio = 1"
    : "cardio = 0";

  return (
    "Modelo XGBoost de clasificación binaria. " +
    "El porcentaje es la probabilidad estimada por el modelo " +
    "para la clase cardio = 1, no una probabilidad clínica " +
    "individual validada. " +
    "El perfil se asigna a cardio = 1 cuando esa probabilidad " +
    `es igual o superior al umbral (${threshold}); ` +
    `en este caso se asignó a ${assigned}.`
  );
}

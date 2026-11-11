
import type { Binary, Prediction } from "../types/pulso";
import { formatProbability, formatThreshold } from "./health";

type Classified = Pick<Prediction, "classification">;

function isAboveThreshold(prediction: Classified): boolean {
  return prediction.classification === 1;
}


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
    return `Este valor alcanza o supera el nivel de atención establecido en PULSO (${threshold} %). Esto indica que tus datos presentan características que el modelo relaciona más con personas con enfermedad cardiovascular.`;
  }

  return `Este valor está por debajo del nivel de atención establecido en PULSO (${threshold} %). Esto indica que tus datos presentan características que el modelo relaciona más con personas sin enfermedad cardiovascular.`;
}

export function resultGuidance(prediction: Prediction): string {
  if (isAboveThreshold(prediction)) {
    return "Este resultado no significa que tengas una enfermedad, pero sí es recomendable consultar con un profesional de la salud para una valoración más completa.";
  }

  return "Aunque tu resultado es favorable, recuerda que ninguna herramienta puede garantizar que estés libre de problemas cardiovasculares. Sigue cuidando tu salud y realizando tus controles habituales.";
}



export function importantNote(_prediction: Prediction): string {
  return "PULSO es una herramienta de orientación basada en inteligencia artificial. Sus resultados no constituyen un diagnóstico médico.";
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

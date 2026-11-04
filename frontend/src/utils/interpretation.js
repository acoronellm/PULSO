import { formatProbability, formatThreshold } from "./health";

export const MODEL_DISCLAIMER =
  "Este resultado es una estimación estadística del modelo de Machine Learning. No constituye un diagnóstico médico, no confirma ni descarta una enfermedad cardiovascular y no equivale a una evaluación clínica individual.";

// Mensaje de la salida de XGBoost frente al umbral que devuelve el backend
export function classificationMessage(prediction) {
  const probability = formatProbability(prediction.probability);
  const threshold = formatThreshold(prediction.threshold);
  const base = `El modelo PULSO estimó una probabilidad del ${probability} % de pertenecer a la clase cardio = 1.`;

  if (prediction.classification === 1) {
    return `${base} Este valor es igual o superior al umbral de clasificación del ${threshold} %, por lo que el modelo asignó el perfil a la clase 1.`;
  }
  return `${base} Este valor se encuentra por debajo del umbral de clasificación del ${threshold} %, por lo que el modelo asignó el perfil a la clase 0.`;
}

export function classLabel(classification) {
  return classification === 1 ? "Clase 1 asignada" : "Clase 0 asignada";
}

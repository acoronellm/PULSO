
import type { SimulationResponse } from "../types/pulso";
import { formatThreshold } from "./health";

export function formatDifference(difference: number): string {
  const points = difference * 100;

  if (Math.abs(points) < 0.05) {
    return "0,0 pp";
  }

  const sign = points > 0 ? "+" : "";

  return `${sign}${points.toFixed(1).replace(".", ",")} pp`;
}

export function differenceText(result: SimulationResponse): string {
  const points = result.probability_difference * 100;
  const magnitude = Math.abs(points);
  const threshold = formatThreshold(result.threshold);

  const originalAbove = result.original.classification === 1;
  const simulatedAbove = result.simulated.classification === 1;

  let variation: string;

  if (points === 0) {
    variation = "la estimación de PULSO no cambió";
  } else if (magnitude < 0.05) {
    variation =
      "la variación de la estimación de PULSO fue inferior a 0,05 puntos porcentuales";
  } else {
    const amount = magnitude.toFixed(1).replace(".", ",");
    const direction = points > 0 ? "aumentó" : "disminuyó";

    variation =
      `la estimación de PULSO ${direction} ${amount} puntos porcentuales`;
  }

  let classificationChange: string;

  if (originalAbove !== simulatedAbove) {
    classificationChange = simulatedAbove
      ? `El resultado pasó de estar por debajo a estar igual o por encima del umbral de clasificación del ${threshold} %.`
      : `El resultado pasó de estar igual o por encima a estar por debajo del umbral de clasificación del ${threshold} %.`;
  } else {
    const position = simulatedAbove
      ? "igual o por encima"
      : "por debajo";

    classificationChange =
      `El resultado permaneció ${position} del umbral de clasificación del ${threshold} %.`;
  }

  return `En este escenario hipotético, ${variation}. ${classificationChange}`;
}

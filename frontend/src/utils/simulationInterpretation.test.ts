
import { describe, expect, it } from "vitest";

import {
  differenceText,
  formatDifference,
} from "./simulationInterpretation";

import type {
  Binary,
  SimulationResponse,
} from "../types/pulso";

function simulation(
  originalProbability: number,
  simulatedProbability: number,
  originalClassification: Binary,
  simulatedClassification: Binary,
  threshold = 0.38,
): SimulationResponse {
  return {
    original: {
      probability: originalProbability,
      classification: originalClassification,
    },
    simulated: {
      probability: simulatedProbability,
      classification: simulatedClassification,
    },
    probability_difference:
      simulatedProbability - originalProbability,
    applied_changes: {},
    model_version: "v1",
    threshold,
  };
}

describe("interpretación de simulaciones", () => {
  it("explica un aumento que cruza el umbral", () => {
    const result = simulation(0.256, 0.775, 0, 1);

    expect(differenceText(result)).toContain(
      "aumentó 51,9 puntos porcentuales",
    );

    expect(differenceText(result)).toContain(
      "pasó de estar por debajo a estar igual o por encima",
    );
  });

  it("explica una disminución que cruza el umbral", () => {
    const result = simulation(0.6, 0.3333, 1, 0);

    expect(differenceText(result)).toContain(
      "disminuyó 26,7 puntos porcentuales",
    );

    expect(differenceText(result)).toContain(
      "pasó de estar igual o por encima a estar por debajo",
    );
  });

  it("explica cuando permanece por debajo del umbral", () => {
    const result = simulation(0.25, 0.30, 0, 0);

    expect(differenceText(result)).toContain(
      "aumentó 5,0 puntos porcentuales",
    );

    expect(differenceText(result)).toContain(
      "permaneció por debajo del umbral",
    );
  });

  it("explica cuando permanece por encima del umbral", () => {
    const result = simulation(0.65, 0.60, 1, 1);

    expect(differenceText(result)).toContain(
      "disminuyó 5,0 puntos porcentuales",
    );

    expect(differenceText(result)).toContain(
      "permaneció igual o por encima del umbral",
    );
  });

  it("explica una variación inferior a 0,05 puntos porcentuales", () => {
    const result = simulation(0.25, 0.2502, 0, 0);

    expect(differenceText(result)).toContain(
      "inferior a 0,05 puntos porcentuales",
    );

    expect(formatDifference(result.probability_difference)).toBe(
      "0,0 pp",
    );
  });

  it("distingue una diferencia exactamente nula", () => {
    const result = simulation(0.25, 0.25, 0, 0);

    expect(differenceText(result)).toContain(
      "la estimación de PULSO no cambió",
    );

    expect(formatDifference(result.probability_difference)).toBe(
      "0,0 pp",
    );
  });

  it("utiliza el umbral proporcionado por el backend", () => {
    const result = simulation(0.45, 0.55, 0, 1, 0.5);

    expect(differenceText(result)).toContain(
      "umbral de clasificación del 50 %",
    );
  });

  it("formatea correctamente las diferencias positivas y negativas", () => {
    expect(formatDifference(0.15)).toBe("+15,0 pp");
    expect(formatDifference(-0.2667)).toBe("-26,7 pp");
  });
});

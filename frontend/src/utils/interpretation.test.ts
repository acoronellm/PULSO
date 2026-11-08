import { describe, expect, it } from "vitest";

import { formatProbability, formatThreshold } from "./health";
import {
  THRESHOLD_EXPLANATION,
  groupExplanation,
  importantNote,
  resultSummary,
  technicalDetail,
  thresholdLabel,
} from "./interpretation";

import type { Binary, Prediction } from "../types/pulso";

function prediction(probability: number, classification: Binary, threshold = 0.38): Prediction {
  return { probability, classification, threshold, model_version: "v1" };
}

const below = prediction(0.2561, 0);
const above = prediction(0.65, 1);

describe("resultado por debajo del umbral", () => {
  it("resume la estimación frente al umbral recibido", () => {
    expect(resultSummary(below)).toBe(
      "Al analizar tus datos, PULSO obtuvo una estimación del 25,6\u00a0%, por debajo del umbral de clasificación del 38\u00a0%."
    );
  });

  it("explica el grupo asignado sin términos técnicos", () => {
    expect(groupExplanation(below)).toBe(
      "Como tu resultado está por debajo de ese valor, el modelo asignó tu perfil al grupo que representa a las personas registradas sin enfermedad cardiovascular en los datos utilizados para su entrenamiento."
    );
    expect(importantNote(below)).toBe(
      "Esto no significa que estés libre de enfermedades cardiovasculares. PULSO ofrece una estimación estadística con fines educativos y preventivos, no un diagnóstico médico."
    );
    expect(thresholdLabel(below)).toBe("Por debajo del umbral");
  });
});

describe("resultado igual o superior al umbral", () => {
  it("resume la estimación y el grupo asignado", () => {
    expect(resultSummary(above)).toBe(
      "Al analizar tus datos, PULSO obtuvo una estimación del 65,0\u00a0%, igual o superior al umbral de clasificación del 38\u00a0%."
    );
    expect(groupExplanation(above)).toContain(
      "al grupo que representa a las personas registradas con enfermedad cardiovascular"
    );
    expect(importantNote(above)).toBe(
      "Esto no confirma que tengas una enfermedad cardiovascular ni indica un riesgo clínico individual determinado. PULSO ofrece una estimación estadística con fines educativos y preventivos, no un diagnóstico médico."
    );
    expect(thresholdLabel(above)).toBe("Igual o superior al umbral");
  });

  it("trata el valor igual al umbral como igual o superior", () => {
    expect(resultSummary(prediction(0.38, 1, 0.38))).toContain(
      "38,0\u00a0%, igual o superior al umbral de clasificación del 38\u00a0%"
    );
  });
});

describe("textos compartidos", () => {
  it("usa el umbral del backend, no un valor fijo", () => {
    expect(resultSummary(prediction(0.45, 0, 0.5))).toContain(
      "umbral de clasificación del 50\u00a0%"
    );
  });

  it("explica qué es el umbral y evita etiquetas de riesgo", () => {
    expect(THRESHOLD_EXPLANATION).toBe(
      "El umbral es el punto de referencia que utiliza PULSO para decidir a cuál de los dos grupos asignar tu perfil."
    );
    const texts = [below, above].flatMap((prediction) => [
      resultSummary(prediction),
      groupExplanation(prediction),
      importantNote(prediction),
      thresholdLabel(prediction),
    ]);
    texts.forEach((text) => {
      expect(text).not.toMatch(/clase|\bcardio\b|riesgo (bajo|alto)|\bsano\b|\benfermo\b/i);
    });
  });

  it("deja los términos técnicos solo en el detalle del modelo", () => {
    expect(technicalDetail(below)).toContain("se asignó a cardio = 0");
    expect(technicalDetail(above)).toContain("se asignó a cardio = 1");
  });

  it("formatea con coma decimal", () => {
    expect(formatProbability(0.63366)).toBe("63,4");
    expect(formatThreshold(0.38)).toBe("38");
    expect(formatThreshold(0.425)).toBe("42,5");
  });
});

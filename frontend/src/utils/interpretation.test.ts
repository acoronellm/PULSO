
import { describe, expect, it } from "vitest";

import { formatProbability, formatThreshold } from "./health";
import {
  THRESHOLD_EXPLANATION,
  groupExplanation,
  importantNote,
  resultGuidance,
  resultSummary,
  technicalDetail,
  thresholdLabel,
} from "./interpretation";

import type { Binary, Prediction } from "../types/pulso";

function prediction(
  probability: number,
  classification: Binary,
  threshold = 0.38,
): Prediction {
  return {
    probability,
    classification,
    threshold,
    model_version: "v1",
  };
}

const below = prediction(0.2561, 0);
const above = prediction(0.65, 1);

const EXPECTED_SUMMARY = (percentage: string) =>
  `Según los datos que ingresaste, PULSO estimó una probabilidad del ${percentage}\u00a0% de pertenecer al grupo de personas registradas con enfermedad cardiovascular en los datos con los que se entrenó el modelo.`;

describe("resultado por debajo del umbral", () => {
  it("explica qué representa la estimación del modelo", () => {
    expect(resultSummary(below)).toBe(
      EXPECTED_SUMMARY("25,6"),
    );
  });

  it("explica el grupo asignado sin términos técnicos", () => {
    expect(groupExplanation(below)).toBe(
      "Este valor está por debajo del umbral de clasificación establecido en PULSO (38 %). Esto indica que tus datos presentan características que el modelo relaciona más con personas sin enfermedad cardiovascular."
    );

    expect(resultGuidance(below)).toBe(
      "Aunque tu resultado es favorable, recuerda que ninguna herramienta puede garantizar que estés libre de problemas cardiovasculares. Sigue cuidando tu salud y realizando tus controles habituales."
    );

    expect(importantNote(below)).toBe(
      "PULSO es una herramienta de orientación basada en inteligencia artificial. Sus resultados no constituyen un diagnóstico médico."
    );
  });
});

describe("resultado igual o superior al umbral", () => {
  it("explica la estimación y el grupo asignado", () => {
    expect(resultSummary(above)).toBe(
      EXPECTED_SUMMARY("65,0"),
    );

    expect(groupExplanation(above)).toBe(
      "Este valor alcanza o supera el umbral de clasificación establecido en PULSO (38 %). Esto indica que tus datos presentan características que el modelo relaciona más con personas con enfermedad cardiovascular."
    );

    expect(resultGuidance(above)).toBe(
      "Este resultado no significa que tengas una enfermedad, pero sí es recomendable consultar con un profesional de la salud para una valoración más completa."
    );

    expect(importantNote(above)).toBe(
      "PULSO es una herramienta de orientación basada en inteligencia artificial. Sus resultados no constituyen un diagnóstico médico."
    );
  });


  it("trata un resultado igual al umbral como igual o superior", () => {
    const equal = prediction(0.38, 1, 0.38);

    expect(resultSummary(equal)).toBe(EXPECTED_SUMMARY("38,0"));

    expect(groupExplanation(equal)).toContain(
      "alcanza o supera el umbral de clasificación establecido en PULSO (38 %)"
    );

    expect(thresholdLabel(equal)).toBe("Igual o superior al umbral");
  });

});

describe("textos compartidos", () => {

  it("utiliza el umbral del backend y no un valor fijo", () => {
    const customThreshold = prediction(0.45, 0, 0.5);

    expect(groupExplanation(customThreshold)).toContain(
      "por debajo del umbral de clasificación establecido en PULSO (50 %)"
    );

    expect(resultSummary(customThreshold)).toBe(EXPECTED_SUMMARY("45,0"));

    expect(thresholdLabel(customThreshold)).toBe("Por debajo del umbral");
  });


  it("explica el umbral y evita etiquetas clínicas incorrectas", () => {
    expect(THRESHOLD_EXPLANATION).toBe(
      "El umbral de clasificación es el valor que utiliza PULSO para asignar cada perfil a uno de los dos grupos.",
    );

    const texts = [below, above].flatMap((item) => [
      resultSummary(item),
      groupExplanation(item),
      importantNote(item),
      thresholdLabel(item),
    ]);

    texts.forEach((text) => {
      expect(text).not.toMatch(
        /clase|\bcardio\b|riesgo (bajo|alto)|\bsano\b|\benfermo\b/i,
      );
    });
  });

  it("deja los términos técnicos en el detalle del modelo", () => {
    expect(technicalDetail(below)).toContain(
      "se asignó a cardio = 0",
    );

    expect(technicalDetail(above)).toContain(
      "se asignó a cardio = 1",
    );
  });

  it("formatea los porcentajes con coma decimal", () => {
    expect(formatProbability(0.63366)).toBe("63,4");
    expect(formatThreshold(0.38)).toBe("38");
    expect(formatThreshold(0.425)).toBe("42,5");
  });
});

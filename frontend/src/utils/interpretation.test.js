import { describe, expect, it } from "vitest";

import { formatProbability, formatThreshold } from "./health";
import { classLabel, classificationMessage } from "./interpretation";

describe("classificationMessage", () => {
  it("describes class 0 below the threshold sent by the backend", () => {
    expect(
      classificationMessage({ probability: 0.2346, classification: 0, threshold: 0.38 })
    ).toBe(
      "El modelo PULSO estimó una probabilidad del 23.5 % de pertenecer a la clase cardio = 1. Este valor se encuentra por debajo del umbral de clasificación del 38 %, por lo que el modelo asignó el perfil a la clase 0."
    );
  });

  it("describes class 1 at or above the threshold", () => {
    expect(
      classificationMessage({ probability: 0.38, classification: 1, threshold: 0.38 })
    ).toBe(
      "El modelo PULSO estimó una probabilidad del 38.0 % de pertenecer a la clase cardio = 1. Este valor es igual o superior al umbral de clasificación del 38 %, por lo que el modelo asignó el perfil a la clase 1."
    );
  });

  it("uses the threshold from the prediction instead of a fixed value", () => {
    expect(
      classificationMessage({ probability: 0.45, classification: 0, threshold: 0.5 })
    ).toContain("umbral de clasificación del 50 %");
  });

  it("follows the class decided by the model", () => {
    expect(classLabel(0)).toBe("Clase 0 asignada");
    expect(classLabel(1)).toBe("Clase 1 asignada");
  });
});

describe("formatting", () => {
  it("formats probability with one decimal and threshold without trailing zeros", () => {
    expect(formatProbability(0.63366)).toBe("63.4");
    expect(formatThreshold(0.38)).toBe("38");
    expect(formatThreshold(0.425)).toBe("42.5");
  });
});

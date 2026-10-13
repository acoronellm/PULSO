import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  analyzeProfile,
  simulateScenario,
} from "../api";

describe("API service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("analyzeProfile realiza POST a /api/analyze", async () => {
    const payload = {
      gender: 1,
      height: 170,
      weight: 70,
      ap_hi: 120,
      ap_lo: 80,
      smoke: 0,
      alco: 0,
      active: 1,
      age_years: 45,
      bmi: 24.22,
    };

    const responseData = {
      prediction: {
        probability: 0.6,
        classification: 1,
        threshold: 0.38,
        model_version: "v1",
      },
      shap: {
        top_factors: [],
      },
      rag: {
        summary: "Resumen.",
        recommendations: [],
        considerations: "",
        note: "",
        insufficient_information: false,
      },
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(responseData),
    });

    const result = await analyzeProfile(payload);

    expect(fetch).toHaveBeenCalledTimes(1);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/analyze"),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    expect(result).toEqual(responseData);
  });

  it("analyzeProfile utiliza el detail devuelto por el backend", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: vi.fn().mockResolvedValue({
        detail: "Datos inválidos.",
      }),
    });

    await expect(
      analyzeProfile({})
    ).rejects.toThrow("Datos inválidos.");
  });

  it("analyzeProfile utiliza mensaje genérico si no puede leer el error", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: vi.fn().mockRejectedValue(
        new Error("Invalid JSON")
      ),
    });

    await expect(
      analyzeProfile({})
    ).rejects.toThrow(
      "No fue posible analizar el perfil."
    );
  });

  it("simulateScenario realiza POST a /api/simulate", async () => {
    const payload = {
      original: {
        gender: 1,
        height: 170,
        weight: 70,
        ap_hi: 120,
        ap_lo: 80,
        smoke: 0,
        alco: 0,
        active: 1,
        age_years: 45,
        bmi: 24.22,
      },
      changes: {
        weight: 65,
      },
    };

    const responseData = {
      original: {
        probability: 0.6,
        classification: 1,
      },
      simulated: {
        probability: 0.45,
        classification: 1,
      },
      probability_difference: -0.15,
      applied_changes: {
        weight: 65,
      },
      model_version: "v1",
      threshold: 0.38,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(responseData),
    });

    const result = await simulateScenario(payload);

    expect(fetch).toHaveBeenCalledTimes(1);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/simulate"),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    expect(result).toEqual(responseData);
  });

  it("simulateScenario utiliza el detail devuelto por el backend", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: vi.fn().mockResolvedValue({
        detail: "Escenario inválido.",
      }),
    });

    await expect(
      simulateScenario({})
    ).rejects.toThrow("Escenario inválido.");
  });

  it("simulateScenario utiliza mensaje genérico si no puede leer el error", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: vi.fn().mockRejectedValue(
        new Error("Invalid JSON")
      ),
    });

    await expect(
      simulateScenario({})
    ).rejects.toThrow(
      "No fue posible realizar la simulación."
    );
  });
});
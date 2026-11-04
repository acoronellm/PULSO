import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./services/api", () => ({
  analyzeProfile: vi.fn(),
  requestRecommendations: vi.fn(),
  simulateScenario: vi.fn(),
}));

import App from "./App";
import {
  analyzeProfile,
  requestRecommendations,
  simulateScenario,
} from "./services/api";

const labels = {
  edad: /Edad actual/,
  estatura: /^Estatura$/,
  peso: /^Peso$/,
  sistolica: /Presión sistólica/,
  diastolica: /Presión diastólica/,
};

const profile = {
  edad: "47",
  estatura: "170",
  peso: "80",
  sistolica: "128",
  diastolica: "82",
};

function analysis(prediction) {
  return {
    analysis_id: "00000000-0000-0000-0000-000000000001",
    prediction: { model_version: "v1", ...prediction },
    shap: {
      top_factors: [
        { feature: "ap_hi", value: 128, shap_value: 0.4, direction: "increase" },
        { feature: "active", value: 1, shap_value: -0.1, direction: "decrease" },
      ],
    },
  };
}

async function analyze(prediction) {
  analyzeProfile.mockResolvedValueOnce(analysis(prediction));
  render(<App />);

  Object.entries(profile).forEach(([name, value]) => {
    fireEvent.change(screen.getByLabelText(labels[name]), { target: { value } });
  });
  fireEvent.click(screen.getByRole("button", { name: /ver mi resultado/i }));

  return screen.findByTestId("classification-message");
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("acceso y alcance de PULSO v1", () => {
  it("abre directamente la evaluación, sin login ni historial", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /completa tu evaluación/i })).toBeInTheDocument();
    expect(screen.queryByText(/iniciar sesión/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/historial/i)).not.toBeInTheDocument();
    expect(screen.getByLabelText(labels.edad)).toHaveValue(null);
  });

  it("no permite abrir el resultado antes de un análisis real", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("link", { name: "Resultado" }));

    expect(screen.getByRole("heading", { name: /completa tu evaluación/i })).toBeInTheDocument();
  });
});

describe("interpretación del resultado", () => {
  it("explica la clase 0 con el umbral recibido del backend", async () => {
    const message = await analyze({ probability: 0.3456, classification: 0, threshold: 0.5 });

    expect(message).toHaveTextContent(
      "El modelo PULSO estimó una probabilidad del 34.6 % de pertenecer a la clase cardio = 1. Este valor se encuentra por debajo del umbral de clasificación del 50 %, por lo que el modelo asignó el perfil a la clase 0."
    );
    expect(screen.getByText("Umbral: 50 %")).toBeInTheDocument();
    expect(screen.getByTestId("model-disclaimer")).toHaveTextContent(
      "No constituye un diagnóstico médico, no confirma ni descarta una enfermedad cardiovascular"
    );
  });

  it("explica la clase 1 cuando la probabilidad alcanza el umbral", async () => {
    const message = await analyze({ probability: 0.38, classification: 1, threshold: 0.38 });

    expect(message).toHaveTextContent(
      "Este valor es igual o superior al umbral de clasificación del 38 %, por lo que el modelo asignó el perfil a la clase 1."
    );
    expect(screen.getByTestId("probability-value")).toHaveTextContent("38.0");
  });

  it("no muestra identidades, porcentajes demostrativos ni etiquetas clínicas", async () => {
    await analyze({ probability: 0.6337, classification: 1, threshold: 0.38 });
    const text = document.body.textContent;

    expect(text).not.toMatch(/Clara/);
    expect(text).not.toMatch(/\b28 ?%/);
    expect(text).not.toMatch(/SCORE2?/i);
    expect(text).not.toMatch(/10 años|diez años/i);
    expect(text).not.toMatch(/riesgo (bajo|alto)|margen controlado|parámetros óptimos|atención prioritaria|elevación leve/i);
    expect(text).toMatch(/Perfil evaluado: Mujer · 47 años/);
  });

  it("describe SHAP como contribución al modelo, sin causalidad", async () => {
    await analyze({ probability: 0.6, classification: 1, threshold: 0.38 });

    expect(screen.getByText("Aumentó la salida del modelo")).toBeInTheDocument();
    expect(screen.getAllByText(/No implica una relación causal médica/)).toHaveLength(2);
  });
});

describe("recomendaciones RAG", () => {
  it("muestra información insuficiente y solo enlaza URLs http(s)", async () => {
    await analyze({ probability: 0.6, classification: 1, threshold: 0.38 });
    requestRecommendations.mockResolvedValueOnce({
      summary: "Resumen educativo.",
      recommendations: [
        {
          factor: "Presión arterial",
          recommendation: "Información preventiva.",
          sources: [
            { source_id: "s1", source: "guia_hipertension.pdf", score: 0.9, lines: { from: 1, to: 9 } },
            { source_id: "s2", source: "guia_externa", score: 0.8, lines: { from: 2, to: 4 }, url: "https://example.org/guia" },
            { source_id: "s3", source: "enlace_inseguro", score: 0.7, lines: { from: 3, to: 5 }, url: "javascript:alert(1)" },
          ],
        },
      ],
      considerations: "",
      note: "",
      insufficient_information: true,
    });

    fireEvent.click(screen.getByRole("button", { name: /solicitar recomendaciones/i }));

    expect(await screen.findByText(/no fue suficiente para generar recomendaciones/)).toBeInTheDocument();
    expect(requestRecommendations).toHaveBeenCalledWith(
      { analysis_id: "00000000-0000-0000-0000-000000000001" },
      expect.any(Object)
    );
    expect(screen.getAllByText("guia_hipertension.pdf")[0].closest("a")).toBeNull();
    expect(screen.getAllByRole("link", { name: "guia_externa" })[0]).toHaveAttribute("href", "https://example.org/guia");
    expect(screen.getAllByText("enlace_inseguro")[0].closest("a")).toBeNull();
  });
});

describe("simulación de escenarios", () => {
  it("pide calcular primero un resultado si no hay análisis", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("link", { name: "Simulación" }));

    expect(screen.getByText(/primero necesitas calcular tu resultado/i)).toBeInTheDocument();
    expect(screen.queryByText(/%/)).not.toBeInTheDocument();
  });

  it("muestra las probabilidades y la variación que devuelve /api/simulate", async () => {
    await analyze({ probability: 0.6, classification: 1, threshold: 0.38 });
    simulateScenario.mockResolvedValueOnce({
      original: { probability: 0.6, classification: 1 },
      simulated: { probability: 0.3333, classification: 0 },
      probability_difference: -0.2667,
      applied_changes: { ap_hi: 128 },
      model_version: "v1",
      threshold: 0.38,
    });

    fireEvent.click(screen.getByRole("link", { name: "Simulación" }));
    expect(screen.getByRole("heading", { name: /simulación de escenarios con pulso v1/i })).toBeInTheDocument();
    expect(screen.queryByText(/sodio|sal/i, { selector: "label *" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /calcular escenario/i }));

    await waitFor(() => expect(screen.getByTestId("simulation-difference")).toHaveTextContent("-26.7 pp"));
    expect(simulateScenario).toHaveBeenCalledWith({
      original: expect.objectContaining({ ap_hi: 128, ap_lo: 82, weight: 80, age_years: 47 }),
      changes: { ap_hi: 128, ap_lo: 82, weight: 80, active: 0, smoke: 0, alco: 0 },
    });
    const simulated = screen.getAllByText("Escenario simulado")[0].parentElement;
    expect(within(simulated).getByText("33.3 %")).toBeInTheDocument();
    expect(within(simulated).getByText("Clase 0 asignada")).toBeInTheDocument();
    expect(screen.getByTestId("simulation-description")).toHaveTextContent(
      "la probabilidad estimada por el modelo disminuye 26.7 puntos porcentuales"
    );
  });
});

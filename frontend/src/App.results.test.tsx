import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./services/api", () => ({
  analyzeProfile: vi.fn(),
  requestRecommendations: vi.fn(),
  simulateScenario: vi.fn(),
}));

import App from "./App";
import {
  analyzeProfile as analyzeProfileApi,
  requestRecommendations as requestRecommendationsApi,
  simulateScenario as simulateScenarioApi,
} from "./services/api";
import type { AnalysisResponse, Prediction, RequestOptions, SimulationResponse } from "./types/pulso";

const analyzeProfile = vi.mocked(analyzeProfileApi);
const requestRecommendations = vi.mocked(requestRecommendationsApi);
const simulateScenario = vi.mocked(simulateScenarioApi);

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

type TestPrediction = Omit<Prediction, "model_version">;

function analysis(prediction: TestPrediction): AnalysisResponse {
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

async function analyze(prediction: TestPrediction) {
  analyzeProfile.mockResolvedValueOnce(analysis(prediction));
  render(<App />);

  (Object.entries(profile) as [keyof typeof labels, string][]).forEach(([name, value]) => {
    fireEvent.change(screen.getByLabelText(labels[name]), { target: { value } });
  });
  fireEvent.click(screen.getByRole("button", { name: /ver mi resultado/i }));

  return screen.findByTestId("result-summary");
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

  it("explica en lenguaje sencillo un resultado por debajo del umbral", async () => {
    const summary = await analyze({
      probability: 0.3456,
      classification: 0,
      threshold: 0.5,
    });

    expect(summary).toHaveTextContent(
      "Según los datos que ingresaste, PULSO estimó una probabilidad del 34,6 % de pertenecer al grupo de personas registradas con enfermedad cardiovascular en los datos con los que se entrenó el modelo.",
    );


    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "Este valor está por debajo del nivel de atención establecido en PULSO (50 %)"
    );

    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "tus datos presentan características que el modelo relaciona más con personas sin enfermedad cardiovascular"
    );

    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "Aunque tu resultado es favorable"
    );

    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "Sigue cuidando tu salud y realizando tus controles habituales."
    );

    expect(screen.getByTestId("result-important")).toHaveTextContent(
      "PULSO es una herramienta de orientación basada en inteligencia artificial. Sus resultados no constituyen un diagnóstico médico."
    );

    const important = screen.getByTestId("result-important");

    expect(important).toHaveClass("font-semibold");
    expect(important).toHaveClass("text-body-lg");

    expect(
      screen.getByText("Importante")
    ).toBeInTheDocument();


    expect(screen.getAllByText("Umbral: 50 %").length).toBeGreaterThan(0);
  });

  it("explica un resultado igual al umbral como igual o superior", async () => {
    const summary = await analyze({
      probability: 0.38,
      classification: 1,
      threshold: 0.38,
    });

    expect(summary).toHaveTextContent(
      "PULSO estimó una probabilidad del 38,0 %",
    );


    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "Este valor alcanza o supera el nivel de atención establecido en PULSO (38 %)"
    );

    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "tus datos presentan características que el modelo relaciona más con personas con enfermedad cardiovascular"
    );

    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "Este resultado no significa que tengas una enfermedad"
    );

    expect(screen.getByTestId("result-meaning")).toHaveTextContent(
      "es recomendable consultar con un profesional de la salud"
    );

    expect(screen.getByTestId("result-important")).toHaveTextContent(
      "PULSO es una herramienta de orientación basada en inteligencia artificial. Sus resultados no constituyen un diagnóstico médico."
    );


    const important = screen.getByTestId("result-important");

    expect(important).toHaveClass("font-semibold");
    expect(important).toHaveClass("text-body-lg");

    expect(
      screen.getByText("Importante")
    ).toBeInTheDocument();

    expect(screen.getByTestId("probability-value")).toHaveTextContent(
      "38,0",
    );
  });

  it("no muestra clases ni cardio = 1 en la vista principal", async () => {
    await analyze({ probability: 0.2561, classification: 0, threshold: 0.38 });
    const main = document.body.cloneNode(true) as HTMLElement;
    main.querySelector("[data-testid=technical-details]")?.remove();

    expect(main.textContent).not.toMatch(/clase [01]|cardio ?= ?[01]|clase cardio/i);
    expect(screen.getByTestId("technical-details")).toHaveTextContent("se asignó a cardio = 0");
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


    expect(
      screen.getByText("Aumentó el resultado")
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: "¿Qué pesó en tu resultado?",
      })
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /Los 3 factores que más influyeron en tu estimación/
      )
    ).toHaveTextContent(
      "Muestran cómo los usó el modelo, no una causa médica."
    );

    expect(
      screen.queryByText(/No implica una relación causal médica/)
    ).not.toBeInTheDocument();
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
    expect(screen.getByRole("heading", { name: /¿qué pasaría si cambian tus factores\?/i })).toBeInTheDocument(); expect(screen.queryByText(/sodio|sal/i, { selector: "label *" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /calcular escenario/i }));

    await waitFor(() => expect(screen.getByTestId("simulation-difference")).toHaveTextContent("-26,7 pp"));
    expect(simulateScenario).toHaveBeenCalledWith({
      original: expect.objectContaining({ ap_hi: 128, ap_lo: 82, weight: 80, age_years: 47 }),
      changes: { ap_hi: 128, ap_lo: 82, weight: 80, active: 0, smoke: 0, alco: 0 },
    }, expect.objectContaining({ signal: expect.any(AbortSignal) }));
    const simulated = screen.getAllByText("Escenario simulado")[0].parentElement as HTMLElement;
    expect(within(simulated).getByText("33,3 %")).toBeInTheDocument();
    expect(within(simulated).getByText("Por debajo del umbral")).toBeInTheDocument();

    expect(screen.getByTestId("simulation-description")).toHaveTextContent(
      "la estimación de PULSO disminuyó 26,7 puntos porcentuales"
    );

    expect(screen.getByTestId("simulation-description")).toHaveTextContent(
      "El resultado pasó de estar igual o por encima a estar por debajo del umbral de clasificación del 38 %."
    );

  });

  it("descarta la respuesta de un escenario anterior si cambian los valores", async () => {
    await analyze({ probability: 0.6, classification: 1, threshold: 0.38 });
    let resolveA: (value: SimulationResponse) => void = () => { };
    simulateScenario.mockImplementationOnce(
      (_payload, _options?: RequestOptions) => new Promise<SimulationResponse>((resolve) => {
        resolveA = resolve;
      })
    );

    fireEvent.click(screen.getByRole("link", { name: "Simulación" }));
    fireEvent.click(screen.getByRole("button", { name: /calcular escenario/i }));
    await waitFor(() => expect(simulateScenario).toHaveBeenCalledTimes(1));
    const signalA = simulateScenario.mock.calls[0][1]?.signal as AbortSignal;

    // Escenario B: el usuario cambia la presión mientras A sigue pendiente
    fireEvent.change(screen.getByLabelText(/Presión sistólica/), { target: { value: "118" } });
    expect(signalA.aborted).toBe(true);

    resolveA({
      original: { probability: 0.6, classification: 1 },
      simulated: { probability: 0.55, classification: 1 },
      probability_difference: -0.05,
      applied_changes: {},
      model_version: "v1",
      threshold: 0.38,
    });
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(screen.getByTestId("simulation-difference")).toHaveTextContent("--");
    expect(screen.queryByText("55,0 %")).not.toBeInTheDocument();

    simulateScenario.mockResolvedValueOnce({
      original: { probability: 0.6, classification: 1 },
      simulated: { probability: 0.31, classification: 0 },
      probability_difference: -0.29,
      applied_changes: { ap_hi: 118 },
      model_version: "v1",
      threshold: 0.38,
    });
    fireEvent.click(screen.getByRole("button", { name: /calcular escenario/i }));

    await waitFor(() => expect(screen.getByTestId("simulation-difference")).toHaveTextContent("-29,0 pp"));
    expect(simulateScenario.mock.calls[1][0].changes.ap_hi).toBe(118);
    expect(screen.getAllByText("31,0 %").length).toBeGreaterThan(0);
  });
});

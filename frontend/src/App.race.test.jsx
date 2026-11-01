import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const analysisRequests = [];
const recommendationRequests = [];

function deferred() {
  let resolve;
  const promise = new Promise((promiseResolve) => {
    resolve = promiseResolve;
  });
  return { promise, resolve };
}

vi.mock("./services/api", () => ({
  analyzeProfile: vi.fn((userData) => {
    const request = deferred();
    analysisRequests.push({ request, userData });
    return request.promise;
  }),
  requestRecommendations: vi.fn((context, options) => {
    const request = deferred();
    recommendationRequests.push({ request, context, options });
    return request.promise;
  }),
  simulateScenario: vi.fn(),
}));

import App from "./App";

const profile = {
  gender: "1",
  age_years: "61",
  height: "172",
  weight: "88",
  ap_hi: "150",
  ap_lo: "92",
  smoke: "1",
  alco: "0",
  active: "0",
};

function submitProfile(overrides = {}) {
  const values = { ...profile, ...overrides };
  const labels = {
    gender: "Sexo",
    age_years: "Edad",
    height: "Altura",
    weight: "Peso",
    ap_hi: "Presión sistólica",
    ap_lo: "Presión diastólica",
    smoke: "¿Fuma?",
    alco: "¿Consume alcohol?",
    active: "¿Realiza actividad física?",
  };

  Object.entries(values).forEach(([name, value]) => {
    fireEvent.change(screen.getByLabelText(new RegExp(labels[name])), {
      target: { value },
    });
  });

  fireEvent.click(screen.getByRole("button", { name: /analizar mi perfil/i }));
}

function analysisResult(analysisId, probability) {
  return {
    analysis_id: analysisId,
    prediction: {
      probability,
      classification: 0,
      threshold: 0.38,
      model_version: "v1",
    },
    shap: { top_factors: [] },
  };
}

describe("recommendation request consistency", () => {
  it("does not display stale RAG results after a new analysis", async () => {
    render(<App />);

    submitProfile();
    await waitFor(() => expect(analysisRequests).toHaveLength(1));
    analysisRequests[0].request.resolve(
      analysisResult("analysis-a", 0.35)
    );

    await screen.findByText("35.0%");
    fireEvent.click(
      screen.getByRole("button", {
        name: /solicitar recomendaciones/i,
      })
    );
    await waitFor(() => expect(recommendationRequests).toHaveLength(1));

    submitProfile({ weight: "70" });
    await waitFor(() => expect(analysisRequests).toHaveLength(2));
    expect(recommendationRequests[0].options.signal.aborted).toBe(true);
    analysisRequests[1].request.resolve(
      analysisResult("analysis-b", 0.8)
    );

    await screen.findByText("80.0%");
    recommendationRequests[0].request.resolve({
      summary: "Recomendaciones del perfil A",
      recommendations: [],
      considerations: "",
      note: "",
      insufficient_information: false,
    });

    await waitFor(() => {
      expect(
        screen.queryByText("Recomendaciones del perfil A")
      ).not.toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", { name: /solicitar recomendaciones/i })
    ).toBeInTheDocument();
  });
});

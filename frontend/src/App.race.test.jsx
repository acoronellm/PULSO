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
  edad: "61",
  estatura: "172",
  peso: "88",
  sistolica: "150",
  diastolica: "92",
};

const labels = {
  edad: /Edad actual/,
  estatura: /Estatura habitual/,
  peso: /Peso actual/,
  sistolica: /Presión sistólica/,
  diastolica: /Presión diastólica/,
};

function submitProfile(overrides = {}) {
  const values = { ...profile, ...overrides };

  Object.entries(values).forEach(([name, value]) => {
    fireEvent.change(screen.getByLabelText(labels[name]), {
      target: { value },
    });
  });

  fireEvent.click(screen.getByRole("button", { name: /ver mi resultado/i }));
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
    fireEvent.click(screen.getByRole("button", { name: /usuario demo/i }));
    fireEvent.click(screen.getByRole("button", { name: /ingresar a pulso/i }));

    submitProfile();
    await waitFor(() => expect(analysisRequests).toHaveLength(1));
    analysisRequests[0].request.resolve(
      analysisResult("analysis-a", 0.35)
    );

    await screen.findByText("Tu punto: 35%");
    fireEvent.click(
      screen.getByRole("button", {
        name: /solicitar recomendaciones/i,
      })
    );
    await waitFor(() => expect(recommendationRequests).toHaveLength(1));

    fireEvent.click(screen.getByRole("link", { name: /editar mis datos/i }));
    submitProfile({ peso: "70" });
    await waitFor(() => expect(analysisRequests).toHaveLength(2));
    expect(recommendationRequests[0].options.signal.aborted).toBe(true);
    analysisRequests[1].request.resolve(
      analysisResult("analysis-b", 0.8)
    );

    await screen.findByText("Tu punto: 80%");
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

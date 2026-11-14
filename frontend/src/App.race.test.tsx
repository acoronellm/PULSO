import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type {
  AnalysisResponse,
  RagRequest,
  RagResponse,
  RequestOptions,
  UserData,
} from "./types/pulso";

interface Deferred<T> {
  promise: Promise<T>;
  resolve: (value: T) => void;
}

const analysisRequests: { request: Deferred<AnalysisResponse>; userData: UserData }[] = [];
const recommendationRequests: {
  request: Deferred<RagResponse>;
  context: RagRequest;
  options: RequestOptions;
}[] = [];

function deferred<T>(): Deferred<T> {
  let resolve: (value: T) => void = () => {};
  const promise = new Promise<T>((promiseResolve) => {
    resolve = promiseResolve;
  });
  return { promise, resolve };
}

vi.mock("./services/api", () => ({
  analyzeProfile: vi.fn((userData: UserData) => {
    const request = deferred<AnalysisResponse>();
    analysisRequests.push({ request, userData });
    return request.promise;
  }),
  requestRecommendations: vi.fn((context: RagRequest, options: RequestOptions) => {
    const request = deferred<RagResponse>();
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
  estatura: /^Estatura$/,
  peso: /^Peso$/,
  sistolica: /Presión sistólica/,
  diastolica: /Presión diastólica/,
};

type ProfileField = keyof typeof labels;

function submitProfile(overrides: Partial<Record<ProfileField, string>> = {}) {
  const values = { ...profile, ...overrides };

  (Object.entries(values) as [ProfileField, string][]).forEach(([name, value]) => {
    fireEvent.change(screen.getByLabelText(labels[name]), {
      target: { value },
    });
  });

  fireEvent.click(screen.getByRole("button", { name: /ver mi resultado/i }));
}

function analysisResult(analysisId: string, probability: number): AnalysisResponse {
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

    await screen.findByText("Tu resultado: 35,0 %");
    fireEvent.click(
      screen.getByRole("button", {
        name: /consultar información educativa/i,
      })
    );
    await waitFor(() => expect(recommendationRequests).toHaveLength(1));

    fireEvent.click(screen.getByRole("link", { name: /editar mis datos/i }));
    submitProfile({ peso: "70" });
    await waitFor(() => expect(analysisRequests).toHaveLength(2));
    expect(recommendationRequests[0].options.signal?.aborted).toBe(true);
    analysisRequests[1].request.resolve(
      analysisResult("analysis-b", 0.8)
    );

    await screen.findByText("Tu resultado: 80,0 %");
    recommendationRequests[0].request.resolve({
      summary: "Recomendaciones del perfil A",
      recommendations: [],
      considerations: "",
      note: "",
      insufficient_information: false,
      factor_explanations: [],
    });

    await waitFor(() => {
      expect(
        screen.queryByText("Recomendaciones del perfil A")
      ).not.toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", { name: /consultar información educativa/i })
    ).toBeInTheDocument();
  });
});

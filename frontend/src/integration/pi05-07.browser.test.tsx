import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";
import type { RagResponse } from "../types/pulso";

interface ApiResponse {
  path: string;
  status: number;
  body: unknown;
}

const apiResponses: ApiResponse[] = [];
const realFetch = globalThis.fetch.bind(globalThis);

function isSuccessfulResponse(path: string): boolean {
  return apiResponses.some((response) => response.path === path && response.status === 200);
}

function isRagResponse(body: unknown): body is RagResponse {
  if (typeof body !== "object" || body === null) {
    return false;
  }

  const response = body as Record<string, unknown>;
  return typeof response.summary === "string"
    && Array.isArray(response.recommendations)
    && Array.isArray(response.factor_explanations)
    && typeof response.considerations === "string"
    && typeof response.note === "string"
    && typeof response.insufficient_information === "boolean";
}

async function submitExampleProfile() {
  await act(async () => {
    fireEvent.click(
      screen.getByRole("button", { name: /usar datos de ejemplo/i })
    );
  });

  await waitFor(() => {
    expect(screen.getByLabelText(/edad actual/i)).not.toHaveValue(null);
  });

  fireEvent.click(
    screen.getByRole("button", { name: /ver mi resultado/i })
  );

  await screen.findByTestId("result-summary", {}, { timeout: 15000 });
}

beforeAll(async () => {
  const response = await fetch("/api/health");

  if (!response.ok) {
    throw new Error(`El backend respondió HTTP ${response.status} en /api/health.`);
  }
});

beforeEach(() => {
  apiResponses.length = 0;
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const response = await realFetch(input, init);
    const requestUrl = typeof input === "string"
      ? input
      : input instanceof URL
        ? input.href
        : input.url;
    const path = new URL(requestUrl, window.location.href).pathname;

    if (path.startsWith("/api/")) {
      const body: unknown = response.headers.get("content-type")?.includes("application/json")
        ? await response.clone().json()
        : null;
      apiResponses.push({ path, status: response.status, body });
    }

    return response;
  });
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("PI-05 a PI-07: integración de frontend con backend real", () => {
  it("PI-05 analiza un perfil y obtiene recomendaciones RAG del backend", async () => {
    render(<App />);
    await submitExampleProfile();

    expect(isSuccessfulResponse("/api/analyze")).toBe(true);
    const analysis = apiResponses.find((response) => response.path === "/api/analyze");
    expect(analysis?.body).toMatchObject({
      analysis_id: expect.any(String),
      prediction: expect.objectContaining({
        probability: expect.any(Number),
        model_version: "v1",
      }),
      shap: expect.objectContaining({ top_factors: expect.any(Array) }),
    });

    fireEvent.click(
      screen.getByRole("button", { name: /consultar información educativa/i }),
    );

    await waitFor(
      () => expect(isSuccessfulResponse("/api/rag")).toBe(true),
      { timeout: 100_000 },
    );

    const rag = apiResponses.find((response) => response.path === "/api/rag");
    if (!rag || !isRagResponse(rag.body)) {
      throw new Error("La respuesta del endpoint RAG no cumple el contrato del frontend.");
    }

    const sourcesButton = screen.getByRole("button", {
      name: /fuentes documentales consultadas/i,
    });

    expect(sourcesButton).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(sourcesButton);

    expect(sourcesButton).toHaveAttribute("aria-expanded", "true");
    if (rag.body.insufficient_information) {
      expect(screen.getByRole("status")).toHaveTextContent(/información documental disponible/i);
      return;
    }

    const displayedText = rag.body.recommendations.find((item) => item.recommendation.trim())
      ?.recommendation
      || rag.body.factor_explanations.find((item) => item.explanation.trim())?.explanation
      || rag.body.considerations
      || rag.body.note;
    if (!displayedText) {
      throw new Error("La respuesta RAG no contiene contenido educativo para mostrar.");
    }
    expect(screen.getByText(displayedText, { exact: false })).toBeInTheDocument();
  });

  it("PI-06 envía cambios de escenario al backend y muestra la comparación", async () => {
    render(<App />);
    await submitExampleProfile();
    fireEvent.click(screen.getByRole("link", { name: /simular escenarios/i }));

    await screen.findByRole("heading", { name: /qué pasaría si cambian tus factores/i });
    fireEvent.change(screen.getByRole("slider", { name: /peso/i }), { target: { value: "70" } });
    fireEvent.click(screen.getByRole("button", { name: /calcular escenario/i }));

    await waitFor(() => expect(isSuccessfulResponse("/api/simulate")).toBe(true));

    const simulation = apiResponses.find((response) => response.path === "/api/simulate");
    expect(simulation?.body).toMatchObject({
      original: expect.objectContaining({ probability: expect.any(Number) }),
      simulated: expect.objectContaining({ probability: expect.any(Number) }),
      probability_difference: expect.any(Number),
      model_version: "v1",
      applied_changes: expect.objectContaining({ weight: 70 }),
    });
    expect(screen.getByTestId("simulation-difference")).not.toHaveTextContent("--");
    expect(screen.getAllByText("Escenario simulado")[0].parentElement)
      .toHaveTextContent(/\d+,\d %/);
  });

  it("PI-07 rechaza presiones inconsistentes antes de llamar al backend", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /usar datos de ejemplo/i }));
    fireEvent.change(screen.getByLabelText(/presión sistólica \(máxima\)/i), {
      target: { value: "80" },
    });
    fireEvent.change(screen.getByLabelText(/presión diastólica \(mínima\)/i), {
      target: { value: "90" },
    });
    fireEvent.click(screen.getByRole("button", { name: /ver mi resultado/i }));

    expect(
      await screen.findByText("La presión sistólica debe ser mayor que la diastólica."),
    ).toBeInTheDocument();
    expect(apiResponses.filter((response) => response.path === "/api/analyze")).toHaveLength(0);
  });
});

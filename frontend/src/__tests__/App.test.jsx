import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";
import { analyzeProfile } from "../services/api";

vi.mock("../services/api", () => ({
  analyzeProfile: vi.fn(),
  simulateScenario: vi.fn(),
}));

const mockAnalysis = {
  prediction: {
    probability: 0.68,
    classification: 1,
    threshold: 0.38,
    model_version: "v1",
  },
  shap: {
    top_factors: [
      {
        feature: "ap_hi",
        value: 150,
        shap_value: 0.44,
        direction: "increase",
      },
      {
        feature: "smoke",
        value: 1,
        shap_value: 0.31,
        direction: "increase",
      },
    ],
  },
  rag: {
    summary: "Resumen preventivo personalizado.",
    recommendations: [
      {
        factor: "ap_hi",
        recommendation:
          "Mantener seguimiento de la presión arterial.",
        source_ids: ["source-1"],
        sources: [
          {
            source_id: "source-1",
            source: "Guía cardiovascular",
            score: 0.95,
            lines: {
              from: 1,
              to: 5,
            },
          },
        ],
      },
    ],
    considerations:
      "La información debe interpretarse con precaución.",
    note:
      "Esta respuesta no constituye diagnóstico médico.",
    insufficient_information: false,
  },
};

async function completeForm(user) {
  await user.type(
    screen.getByLabelText(/edad/i),
    "45"
  );

  await user.type(
    screen.getByLabelText(/altura/i),
    "170"
  );

  await user.type(
    screen.getByLabelText(/peso/i),
    "70"
  );

  await user.type(
    screen.getByLabelText(/presión sistólica/i),
    "150"
  );

  await user.type(
    screen.getByLabelText(/presión diastólica/i),
    "90"
  );

  await user.selectOptions(
    screen.getByLabelText(/¿fuma\?/i),
    "1"
  );
}

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("muestra el formulario inicialmente y no muestra resultados", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: /conoce tu perfil cardiovascular/i,
      })
    ).toBeInTheDocument();

    expect(
      screen.queryByText(/resultado estimado por pulso/i)
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText(/factores que más influyeron/i)
    ).not.toBeInTheDocument();
  });

  it("envía el perfil al servicio de análisis", async () => {
    const user = userEvent.setup();

    analyzeProfile.mockResolvedValue(mockAnalysis);

    render(<App />);

    await completeForm(user);

    await user.click(
      screen.getByRole("button", {
        name: /analizar mi perfil/i,
      })
    );

    expect(analyzeProfile).toHaveBeenCalledTimes(1);

    expect(analyzeProfile).toHaveBeenCalledWith({
      gender: 1,
      height: 170,
      weight: 70,
      ap_hi: 150,
      ap_lo: 90,
      smoke: 1,
      alco: 0,
      active: 1,
      age_years: 45,
      bmi: 24.22,
    });
  });

  it("muestra los resultados completos después de un análisis exitoso", async () => {
    const user = userEvent.setup();

    analyzeProfile.mockResolvedValue(mockAnalysis);

    render(<App />);

    await completeForm(user);

    await user.click(
      screen.getByRole("button", {
        name: /analizar mi perfil/i,
      })
    );

    expect(
      await screen.findByText(/resultado estimado por pulso/i)
    ).toBeInTheDocument();

    expect(
      screen.getByText("68.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText(/factores que más influyeron/i)
    ).toBeInTheDocument();

    expect(
      screen.getByText("Resumen preventivo personalizado.")
    ).toBeInTheDocument();

    expect(
      screen.getByText(/explora un escenario hipotético/i)
    ).toBeInTheDocument();
  });

  it("muestra un mensaje de error si falla el análisis", async () => {
    const user = userEvent.setup();

    analyzeProfile.mockRejectedValue(
      new Error("No fue posible comunicarse con el servidor.")
    );

    render(<App />);

    await completeForm(user);

    await user.click(
      screen.getByRole("button", {
        name: /analizar mi perfil/i,
      })
    );

    expect(
      await screen.findByText(
        "No fue posible comunicarse con el servidor."
      )
    ).toBeInTheDocument();

    expect(
      screen.getByText(/no fue posible completar el análisis/i)
    ).toBeInTheDocument();

    expect(
      screen.queryByText(/resultado estimado por pulso/i)
    ).not.toBeInTheDocument();
  });

  it("muestra estado de carga mientras espera el análisis", async () => {
    const user = userEvent.setup();

    let resolveAnalysis;

    analyzeProfile.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveAnalysis = resolve;
        })
    );

    render(<App />);

    await completeForm(user);

    await user.click(
      screen.getByRole("button", {
        name: /analizar mi perfil/i,
      })
    );

    const loadingButton = screen.getByRole("button", {
      name: /analizando/i,
    });

    expect(loadingButton).toBeDisabled();

    resolveAnalysis(mockAnalysis);

    expect(
      await screen.findByRole("button", {
        name: /analizar mi perfil/i,
      })
    ).toBeEnabled();
  });
});
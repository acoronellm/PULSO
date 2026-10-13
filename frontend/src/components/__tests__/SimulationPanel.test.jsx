import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SimulationPanel from "../SimulationPanel";
import { simulateScenario } from "../../services/api";

vi.mock("../../services/api", () => ({
  simulateScenario: vi.fn(),
}));

const originalProfile = {
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

const originalPrediction = {
  probability: 0.6,
  classification: 1,
  threshold: 0.38,
  model_version: "v1",
};

describe("SimulationPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("muestra error si no se selecciona ningún cambio", async () => {
    const user = userEvent.setup();

    render(
      <SimulationPanel
        originalProfile={originalProfile}
        originalPrediction={originalPrediction}
      />
    );

    await user.click(
      screen.getByRole("button", {
        name: /simular escenario/i,
      })
    );

    expect(
      screen.getByText(
        /selecciona al menos un cambio para realizar la simulación/i
      )
    ).toBeInTheDocument();

    expect(simulateScenario).not.toHaveBeenCalled();
  });

  it("envía únicamente los cambios seleccionados", async () => {
    const user = userEvent.setup();

    simulateScenario.mockResolvedValue({
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
    });

    render(
      <SimulationPanel
        originalProfile={originalProfile}
        originalPrediction={originalPrediction}
      />
    );

    await user.type(
      screen.getByLabelText(/nuevo peso/i),
      "65"
    );

    await user.click(
      screen.getByRole("button", {
        name: /simular escenario/i,
      })
    );

    expect(simulateScenario).toHaveBeenCalledTimes(1);

    expect(simulateScenario).toHaveBeenCalledWith({
      original: originalProfile,
      changes: {
        weight: 65,
      },
    });
  });

  it("muestra el resultado original y el resultado simulado", async () => {
    const user = userEvent.setup();

    simulateScenario.mockResolvedValue({
      original: {
        probability: 0.6,
        classification: 1,
      },
      simulated: {
        probability: 0.35,
        classification: 0,
      },
      probability_difference: -0.25,
      applied_changes: {
        ap_hi: 110,
      },
      model_version: "v1",
      threshold: 0.38,
    });

    render(
      <SimulationPanel
        originalProfile={originalProfile}
        originalPrediction={originalPrediction}
      />
    );

    await user.type(
      screen.getByLabelText(/nueva presión sistólica/i),
      "110"
    );

    await user.click(
      screen.getByRole("button", {
        name: /simular escenario/i,
      })
    );

    expect(
      await screen.findByText("60.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("35.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText(/-25.0 puntos porcentuales/i)
    ).toBeInTheDocument();
  });

  it("muestra la clasificación simulada", async () => {
    const user = userEvent.setup();

    simulateScenario.mockResolvedValue({
      original: {
        probability: 0.6,
        classification: 1,
      },
      simulated: {
        probability: 0.3,
        classification: 0,
      },
      probability_difference: -0.3,
      applied_changes: {
        active: 1,
      },
      model_version: "v1",
      threshold: 0.38,
    });

    render(
      <SimulationPanel
        originalProfile={originalProfile}
        originalPrediction={originalPrediction}
      />
    );

    await user.selectOptions(
      screen.getByLabelText(/actividad física/i),
      "1"
    );

    await user.click(
      screen.getByRole("button", {
        name: /simular escenario/i,
      })
    );

    expect(
      await screen.findByText(/por debajo del umbral/i)
    ).toBeInTheDocument();
  });

  it("muestra error cuando falla el servicio de simulación", async () => {
    const user = userEvent.setup();

    simulateScenario.mockRejectedValue(
      new Error("Error de simulación")
    );

    render(
      <SimulationPanel
        originalProfile={originalProfile}
        originalPrediction={originalPrediction}
      />
    );

    await user.type(
      screen.getByLabelText(/nuevo peso/i),
      "65"
    );

    await user.click(
      screen.getByRole("button", {
        name: /simular escenario/i,
      })
    );

    expect(
      await screen.findByText("Error de simulación")
    ).toBeInTheDocument();
  });

  it("muestra estado de carga mientras espera la simulación", async () => {
    const user = userEvent.setup();

    let resolvePromise;

    simulateScenario.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePromise = resolve;
        })
    );

    render(
      <SimulationPanel
        originalProfile={originalProfile}
        originalPrediction={originalPrediction}
      />
    );

    await user.type(
      screen.getByLabelText(/nuevo peso/i),
      "65"
    );

    await user.click(
      screen.getByRole("button", {
        name: /simular escenario/i,
      })
    );

    const loadingButton = screen.getByRole("button", {
      name: /simulando/i,
    });

    expect(loadingButton).toBeDisabled();

    resolvePromise({
      original: {
        probability: 0.6,
        classification: 1,
      },
      simulated: {
        probability: 0.5,
        classification: 1,
      },
      probability_difference: -0.1,
      applied_changes: {
        weight: 65,
      },
      model_version: "v1",
      threshold: 0.38,
    });

    expect(
      await screen.findByRole("button", {
        name: /simular escenario/i,
      })
    ).toBeEnabled();
  });
});
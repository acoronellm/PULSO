import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ShapFactors from "../ShapFactors";

describe("ShapFactors", () => {
  it("no renderiza contenido si no hay factores SHAP", () => {
    const { container } = render(
      <ShapFactors shap={{ top_factors: [] }} />
    );

    expect(container).toBeEmptyDOMElement();
  });

  it("muestra correctamente el nombre legible del factor", () => {
    render(
      <ShapFactors
        shap={{
          top_factors: [
            {
              feature: "ap_hi",
              value: 150,
              shap_value: 0.44,
              direction: "increase",
            },
          ],
        }}
      />
    );

    expect(
      screen.getByText(/presión sistólica/i)
    ).toBeInTheDocument();
  });

  it("muestra correctamente las unidades de presión arterial", () => {
    render(
      <ShapFactors
        shap={{
          top_factors: [
            {
              feature: "ap_hi",
              value: 150,
              shap_value: 0.44,
              direction: "increase",
            },
          ],
        }}
      />
    );

    expect(
      screen.getByText("150 mmHg")
    ).toBeInTheDocument();
  });

  it("traduce correctamente un valor binario de tabaquismo", () => {
    render(
      <ShapFactors
        shap={{
          top_factors: [
            {
              feature: "smoke",
              value: 1,
              shap_value: 0.31,
              direction: "increase",
            },
          ],
        }}
      />
    );

    expect(
      screen.getByText(/tabaquismo/i)
    ).toBeInTheDocument();

    expect(
      screen.getByText(/^sí$/i)
    ).toBeInTheDocument();
  });

  it("muestra cuando un factor aumentó la salida del modelo", () => {
    render(
      <ShapFactors
        shap={{
          top_factors: [
            {
              feature: "ap_hi",
              value: 150,
              shap_value: 0.44,
              direction: "increase",
            },
          ],
        }}
      />
    );

    expect(
      screen.getByText(/aumentó la salida del modelo/i)
    ).toBeInTheDocument();
  });

  it("muestra cuando un factor disminuyó la salida del modelo", () => {
    render(
      <ShapFactors
        shap={{
          top_factors: [
            {
              feature: "active",
              value: 1,
              shap_value: -0.20,
              direction: "decrease",
            },
          ],
        }}
      />
    );

    expect(
      screen.getByText(/disminuyó la salida del modelo/i)
    ).toBeInTheDocument();
  });

  it("muestra correctamente múltiples factores", () => {
    render(
      <ShapFactors
        shap={{
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
            {
              feature: "active",
              value: 0,
              shap_value: 0.19,
              direction: "increase",
            },
          ],
        }}
      />
    );

    expect(
      screen.getByText(/presión sistólica/i)
    ).toBeInTheDocument();

    expect(
      screen.getByText(/tabaquismo/i)
    ).toBeInTheDocument();

    expect(
      screen.getByText(/actividad física/i)
    ).toBeInTheDocument();
  });

  it("muestra la advertencia sobre causalidad", () => {
    render(
      <ShapFactors
        shap={{
          top_factors: [
            {
              feature: "bmi",
              value: 28.4,
              shap_value: 0.15,
              direction: "increase",
            },
          ],
        }}
      />
    );

    expect(
      screen.getByText(/no representa por sí sola una relación causal/i)
    ).toBeInTheDocument();
  });
});
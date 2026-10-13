import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import PredictionResult from "../PredictionResult";

describe("PredictionResult", () => {
  it("no renderiza contenido si no recibe prediction", () => {
    const { container } = render(<PredictionResult prediction={null} />);

    expect(container).toBeEmptyDOMElement();
  });

  it("muestra correctamente la probabilidad y el umbral", () => {
    render(
      <PredictionResult
        prediction={{
          probability: 0.68,
          classification: 1,
          threshold: 0.38,
          model_version: "v1",
        }}
      />
    );

    expect(screen.getByText("68.0%")).toBeInTheDocument();
    expect(screen.getByText("38%")).toBeInTheDocument();
  });

  it("muestra que el resultado está por encima del umbral", () => {
    render(
      <PredictionResult
        prediction={{
          probability: 0.68,
          classification: 1,
          threshold: 0.38,
          model_version: "v1",
        }}
      />
    );

    expect(
      screen.getByText(/por encima del umbral/i)
    ).toBeInTheDocument();
  });

  it("muestra que el resultado está por debajo del umbral", () => {
    render(
      <PredictionResult
        prediction={{
          probability: 0.25,
          classification: 0,
          threshold: 0.38,
          model_version: "v1",
        }}
      />
    );

    expect(
      screen.getByText(/por debajo del umbral/i)
    ).toBeInTheDocument();
  });

  it("muestra la advertencia educativa", () => {
    render(
      <PredictionResult
        prediction={{
          probability: 0.68,
          classification: 1,
          threshold: 0.38,
          model_version: "v1",
        }}
      />
    );

    expect(
      screen.getByText(/no realiza diagnósticos médicos/i)
    ).toBeInTheDocument();
  });
});
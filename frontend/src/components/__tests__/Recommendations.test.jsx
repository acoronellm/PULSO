import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Recommendations from "../Recommendations";

describe("Recommendations", () => {
  it("no renderiza contenido si rag es null", () => {
    const { container } = render(<Recommendations rag={null} />);

    expect(container).toBeEmptyDOMElement();
  });

  it("muestra el resumen del RAG", () => {
    render(
      <Recommendations
        rag={{
          summary: "Resumen preventivo personalizado.",
          recommendations: [],
          considerations: "",
          note: "",
          insufficient_information: false,
        }}
      />
    );

    expect(
      screen.getByText("Resumen preventivo personalizado.")
    ).toBeInTheDocument();
  });

  it("muestra una recomendación y su factor", () => {
    render(
      <Recommendations
        rag={{
          summary: "Resumen.",
          recommendations: [
            {
              factor: "ap_hi",
              recommendation:
                "Mantener seguimiento de la presión arterial.",
              source_ids: [],
              sources: [],
            },
          ],
          considerations: "",
          note: "",
          insufficient_information: false,
        }}
      />
    );

    expect(screen.getByText("ap_hi")).toBeInTheDocument();

    expect(
      screen.getByText(
        "Mantener seguimiento de la presión arterial."
      )
    ).toBeInTheDocument();
  });

  it("muestra la fuente y las líneas utilizadas", () => {
    render(
      <Recommendations
        rag={{
          summary: "Resumen.",
          recommendations: [
            {
              factor: "ap_hi",
              recommendation: "Controlar la presión arterial.",
              source_ids: ["source-1"],
              sources: [
                {
                  source_id: "source-1",
                  source: "Guía cardiovascular",
                  score: 0.95,
                  lines: {
                    from: 10,
                    to: 15,
                  },
                },
              ],
            },
          ],
          considerations: "",
          note: "",
          insufficient_information: false,
        }}
      />
    );

    expect(
      screen.getByText("Guía cardiovascular")
    ).toBeInTheDocument();

    expect(
      screen.getByText(/referencia: source-1/i)
    ).toBeInTheDocument();

    expect(
      screen.getByText(/líneas 10–15/i)
    ).toBeInTheDocument();
  });

  it("muestra las consideraciones", () => {
    render(
      <Recommendations
        rag={{
          summary: "",
          recommendations: [],
          considerations:
            "La información debe interpretarse con precaución.",
          note: "",
          insufficient_information: false,
        }}
      />
    );

    expect(
      screen.getByText(
        "La información debe interpretarse con precaución."
      )
    ).toBeInTheDocument();
  });

  it("muestra la nota de advertencia", () => {
    render(
      <Recommendations
        rag={{
          summary: "",
          recommendations: [],
          considerations: "",
          note: "Esta respuesta no constituye diagnóstico médico.",
          insufficient_information: false,
        }}
      />
    );

    expect(
      screen.getByText(
        "Esta respuesta no constituye diagnóstico médico."
      )
    ).toBeInTheDocument();
  });

  it("muestra múltiples recomendaciones", () => {
    render(
      <Recommendations
        rag={{
          summary: "Resumen.",
          recommendations: [
            {
              factor: "ap_hi",
              recommendation: "Recomendación sobre presión arterial.",
              source_ids: [],
              sources: [],
            },
            {
              factor: "smoke",
              recommendation: "Recomendación sobre tabaquismo.",
              source_ids: [],
              sources: [],
            },
          ],
          considerations: "",
          note: "",
          insufficient_information: false,
        }}
      />
    );

    expect(screen.getByText("ap_hi")).toBeInTheDocument();
    expect(screen.getByText("smoke")).toBeInTheDocument();
  });
});
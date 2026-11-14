import { describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";

import RagRecommendations, {
    RagFactorExplanations,
    RagSources,
} from "./RagRecommendations";

import type { RagResponse } from "../types/pulso";

const RAG_RESPONSE: RagResponse = {
    summary: "RESUMEN_CONCATENADO_NO_VISIBLE",
    considerations: "Una medición aislada no confirma un diagnóstico.",
    note: "PULSO no constituye un diagnóstico médico.",
    insufficient_information: false,
    recommendations: [],
    factor_explanations: [
        {
            query_group: "blood_pressure",
            factor: "Presión arterial",
            features: ["ap_hi", "ap_lo"],
            explanation: "La presión arterial está relacionada con la salud cardiovascular.",
            source_ids: ["SOURCE_1"],
            sources: [
                {
                    source_id: "SOURCE_1",
                    source: "Documento sobre presión arterial",
                    author: "American Heart Association",
                    publication_year: 2025,
                    source_url: "https://example.org/documento",
                    pdf_url: null,
                    score: null,
                    lines: null,
                },
            ],
        },
    ],
};

describe("Integración RAG v3.4.2", () => {
    it("muestra factor_explanations sin recomendaciones", () => {
        render(<RagFactorExplanations rag={RAG_RESPONSE} />);

        expect(
            screen.getByText("Comprende los factores de tu resultado")
        ).toBeInTheDocument();

        expect(
            screen.getByText(
                "La presión arterial está relacionada con la salud cardiovascular."
            )
        ).toBeInTheDocument();

        expect(
            screen.getByText("Presión arterial")
        ).toBeInTheDocument();
    });

    it("no muestra el summary concatenado", () => {
        render(
            <RagRecommendations
                rag={RAG_RESPONSE}
                loading={false}
                error=""
                onRequest={vi.fn()}
            />
        );

        expect(
            screen.queryByText("RESUMEN_CONCATENADO_NO_VISIBLE")
        ).not.toBeInTheDocument();

        expect(
            screen.getByText(/Una medición aislada/)
        ).toBeInTheDocument();
    });

    it("presenta las fuentes documentales de las explicaciones", () => {
        render(<RagFactorExplanations rag={RAG_RESPONSE} />);

        const link = screen.getByRole("link", {
            name: "Documento sobre presión arterial",
        });

        expect(link).toHaveAttribute(
            "href",
            "https://example.org/documento"
        );

        expect(link).toHaveAttribute(
            "rel",
            "noopener noreferrer"
        );

        expect(
            screen.getByText(/American Heart Association/)
        ).toBeInTheDocument();
    });

    it("prioriza pdf_url cuando está disponible", () => {
        const rag: RagResponse = {
            ...RAG_RESPONSE,
            factor_explanations: [
                {
                    ...RAG_RESPONSE.factor_explanations[0],
                    sources: [
                        {
                            ...RAG_RESPONSE.factor_explanations[0].sources[0],
                            pdf_url: "https://example.org/documento.pdf",
                        },
                    ],
                },
            ],
        };

        render(<RagFactorExplanations rag={rag} />);

        expect(
            screen.getByRole("link", {
                name: "Documento sobre presión arterial",
            })
        ).toHaveAttribute(
            "href",
            "https://example.org/documento.pdf"
        );
    });

    it("no convierte URLs inseguras en enlaces", () => {
        const rag: RagResponse = {
            ...RAG_RESPONSE,
            factor_explanations: [
                {
                    ...RAG_RESPONSE.factor_explanations[0],
                    sources: [
                        {
                            ...RAG_RESPONSE.factor_explanations[0].sources[0],
                            source_url: "javascript:alert(1)",
                            pdf_url: null,
                        },
                    ],
                },
            ],
        };

        render(<RagFactorExplanations rag={rag} />);

        expect(
            screen.queryByRole("link", {
                name: "Documento sobre presión arterial",
            })
        ).not.toBeInTheDocument();

        expect(
            screen.getByText("Documento sobre presión arterial")
        ).toBeInTheDocument();
    });

    it("deduplica fuentes entre explicaciones y recomendaciones", () => {
        const rag: RagResponse = {
            ...RAG_RESPONSE,
            recommendations: [
                {
                    factor: "Presión arterial",
                    recommendation: "Consulta con un profesional de salud.",
                    source_ids: ["SOURCE_1"],
                    sources: RAG_RESPONSE.factor_explanations[0].sources,
                },
            ],
        };

        render(<RagSources rag={rag} />);

        const list = screen.getByRole("list");

        expect(
            within(list).getAllByRole("listitem")
        ).toHaveLength(1);
    });

    it("no interpreta ausencia de recomendaciones como información insuficiente", () => {
        render(
            <RagRecommendations
                rag={RAG_RESPONSE}
                loading={false}
                error=""
                onRequest={vi.fn()}
            />
        );

        expect(
            screen.queryByText(/no permitió obtener explicaciones/i)
        ).not.toBeInTheDocument();

        expect(
            screen.getByText(/PULSO no constituye un diagnóstico médico/)
        ).toBeInTheDocument();
    });
    it("muestra una sola referencia cuando varios fragmentos pertenecen al mismo documento", () => {
        const source = RAG_RESPONSE.factor_explanations[0].sources[0];

        const rag: RagResponse = {
            ...RAG_RESPONSE,
            factor_explanations: [
                {
                    ...RAG_RESPONSE.factor_explanations[0],
                    source_ids: ["SOURCE_1", "SOURCE_2"],
                    sources: [
                        source,
                        {
                            ...source,
                            source_id: "SOURCE_2",
                            lines: { from: 6, to: 10 },
                        },
                    ],
                },
            ],
        };

        render(<RagFactorExplanations rag={rag} />);

        expect(
            screen.getAllByRole("link", {
                name: "Documento sobre presión arterial",
            })
        ).toHaveLength(1);
    });

    it("no muestra números de línea de los fragmentos documentales", () => {
        const source = RAG_RESPONSE.factor_explanations[0].sources[0];

        const rag: RagResponse = {
            ...RAG_RESPONSE,
            factor_explanations: [
                {
                    ...RAG_RESPONSE.factor_explanations[0],
                    sources: [
                        {
                            ...source,
                            lines: { from: 1, to: 5 },
                        },
                    ],
                },
            ],
        };

        render(<RagFactorExplanations rag={rag} />);

        expect(
            screen.queryByText(/Líneas 1–5/)
        ).not.toBeInTheDocument();
    });
});
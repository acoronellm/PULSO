import type { RagResponse, RagSource } from "../types/pulso";

// Recomendaciones educativas del módulo RAG (POST /api/rag con analysis_id)

// Las fuentes actuales traen source, source_id, score y lines; `url` es opcional
// para cuando el RAG empiece a devolverla. Nunca se construyen enlaces propios.
function safeUrl(url: unknown): string | null {
  return typeof url === "string" && /^https?:\/\//i.test(url) ? url : null;
}
function uniqueDocuments(sources: RagSource[]): RagSource[] {
  const seen = new Set<string>();

  return sources.filter((source) => {
    const documentKey = (
      safeUrl(source.pdf_url) ??
      safeUrl(source.source_url) ??
      safeUrl(source.url) ??
      `${source.source}|${source.author ?? ""}|${source.publication_year ?? ""}`
    ).trim().toLowerCase();

    if (seen.has(documentKey)) {
      return false;
    }

    seen.add(documentKey);
    return true;
  });
}
function SourceItem({ source }: { source: RagSource }) {
  const url =
    safeUrl(source.pdf_url) ??
    safeUrl(source.source_url) ??
    safeUrl(source.url);

  const metadata = [
    source.author,
    source.publication_year != null
      ? String(source.publication_year)
      : null,
  ].filter(Boolean).join(" · ");



  return (
    <li className="flex items-start gap-1.5">
      <span
        className="material-symbols-outlined text-primary text-[16px] shrink-0 mt-0.5"
        aria-hidden="true"
      >
        bookmark
      </span>

      <div className="min-w-0">
        {url ? (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="font-semibold text-primary hover:underline break-words"
          >
            {source.source}
          </a>
        ) : (
          <span className="font-semibold text-on-surface">
            {source.source}
          </span>
        )}

        {metadata && (
          <p className="text-on-surface-variant text-sm">
            {metadata}
          </p>
        )}


      </div>
    </li>
  );
}

function uniqueSources(rag: RagResponse | null): RagSource[] {
  if (!rag) return [];

  const recommendationSources = rag.recommendations.flatMap(
    (item) => item.sources ?? []
  );

  const explanationSources = (
    rag.factor_explanations ?? []
  ).flatMap(
    (item) => item.sources ?? []
  );

  return uniqueDocuments([
    ...explanationSources,
    ...recommendationSources,
  ]);
}

export function RagSources({ rag }: { rag: RagResponse | null }) {
  const sources = uniqueSources(rag);

  if (!sources.length) {
    return (
      <p className="font-body-md text-on-surface-variant">
        {rag
          ? "La respuesta del módulo RAG no incluyó fuentes documentales."
          : "Solicita las recomendaciones para ver las fuentes documentales utilizadas."}
      </p>
    );
  }

  return (
    <ul className="grid grid-cols-1 md:grid-cols-2 gap-space-sm font-body-md">
      {sources.map((source) => (
        <SourceItem key={source.source_id} source={source} />
      ))}
    </ul>
  );
}

export function RagFactorExplanations({
  rag,
}: {
  rag: RagResponse | null;
}) {
  const explanations = rag?.factor_explanations ?? [];

  if (explanations.length === 0) {
    return null;
  }

  return (
    <section
      className="mt-space-xl"
      aria-labelledby="rag-explanations-title"
      data-testid="rag-factor-explanations"
    >
      <div className="mb-space-md">
        <span className="font-label-sm uppercase font-semibold text-secondary tracking-wider">
          Información educativa
        </span>

        <h2
          id="rag-explanations-title"
          className="font-headline-md text-headline-md text-on-surface font-semibold"
        >
          Comprende los factores de tu resultado
        </h2>

        <p className="font-body-md text-on-surface-variant mt-2">
          Estas explicaciones describen la relación general
          de los factores con la salud cardiovascular.
          No representan causas individuales de enfermedad.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
        {explanations.map((item) => (
          <article
            key={item.query_group}
            className="bg-surface-container-lowest rounded-xl shadow-sm p-space-lg flex flex-col gap-space-md"
          >
            <div>
              <h3 className="font-headline-sm text-on-surface font-semibold">
                {item.factor}
              </h3>

              <p className="font-body-md text-on-surface-variant mt-space-sm leading-relaxed whitespace-pre-line">
                {item.explanation}
              </p>
            </div>

            <div className="border-t border-surface-container pt-space-sm mt-auto">
              <h4 className="font-label-sm text-on-surface font-semibold mb-space-sm">
                Fuentes de esta explicación
              </h4>

              {item.sources.length > 0 ? (
                <ul className="flex flex-col gap-2 font-label-sm">
                  {uniqueDocuments(item.sources).map((source) => (
                    <SourceItem
                      key={source.source_id}
                      source={source}
                    />
                  ))}
                </ul>
              ) : (
                <p className="text-on-surface-variant text-sm">
                  No se adjuntaron fuentes documentales.
                </p>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

interface RagRecommendationsProps {
  rag: RagResponse | null;
  loading: boolean;
  error: string;
  onRequest: () => void;
}

export default function RagRecommendations({ rag, loading, error, onRequest }: RagRecommendationsProps) {
  if (!rag) {
    return (
      <div className="md:col-span-3 bg-surface-container-lowest rounded-xl shadow-sm p-space-lg flex flex-col sm:flex-row sm:items-center justify-between gap-space-md">
        <div className="flex items-start gap-space-sm">
          <div className="w-10 h-10 rounded-xl bg-primary-fixed flex items-center justify-center text-primary shrink-0">
            <span className="material-symbols-outlined text-[24px]">
              menu_book
            </span>
          </div>
          <div>
            <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
              Información educativa personalizada
            </h3>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Consulta explicaciones sobre los factores de tu resultado y recomendaciones preventivas basadas en fuentes documentales.            </p>
            {error && (
              <p className="font-label-md text-error mt-2" role="alert">
                {error}
              </p>
            )}
          </div>
        </div>
        <button className="px-5 py-2.5 rounded-xl bg-primary-container hover:bg-primary text-on-primary font-label-md font-semibold transition-all shadow-md flex items-center justify-center gap-1.5 shrink-0 disabled:opacity-70" disabled={loading} onClick={onRequest} type="button">
          <span className="material-symbols-outlined text-[18px]">
            {loading ? "hourglass_top" : "auto_awesome"}
          </span>
          <span>
            {loading ? "Consultando información educativa..." : "Consultar información educativa"}          </span>
        </button>
      </div>
    );
  }

  return (
    <>
      {rag.insufficient_information && (
        <div className="md:col-span-3 bg-amber-warning-subtle border border-amber-warning-border rounded-xl p-space-md flex items-start gap-space-sm" role="status">
          <span className="material-symbols-outlined text-amber-warning text-[22px] shrink-0">
            info
          </span>
          <p className="font-body-md text-body-md text-on-surface">
            La información documental disponible no permitió obtener
            explicaciones ni recomendaciones educativas válidas
            para este análisis.
          </p>
        </div>
      )}

      {rag.recommendations?.map((item, index) => (
        <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col" key={index}>
          <div className="p-space-md flex-1 flex flex-col justify-between">
            <div>
              <span className="inline-flex bg-surface-container px-2.5 py-1 rounded-full text-primary font-label-sm font-semibold items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">
                  label
                </span>
                {item.factor}
              </span>
              <p className="font-body-md text-body-md text-on-surface-variant mt-space-sm">
                {item.recommendation}
              </p>
            </div>
            <div className="mt-space-md bg-surface-container-low p-2.5 rounded-lg font-label-sm">
              {item.sources?.length ? (
                <ul className="flex flex-col gap-1">
                  {uniqueDocuments(item.sources).map((source) => (
                    <SourceItem key={source.source_id} source={source} />
                  ))}
                </ul>
              ) : (
                <span className="text-on-surface-variant">
                  Sin fuentes asociadas en la respuesta
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
      {(rag.considerations || rag.note) && (
        <div className="md:col-span-3 bg-surface-container-high/60 rounded-xl p-3.5 flex items-start gap-2.5 text-on-surface-variant">
          <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
            verified_user
          </span>
          <div className="font-label-sm text-label-sm leading-snug space-y-1">
            {rag.considerations && (
              <p>
                <strong className="text-on-surface font-semibold">
                  Consideraciones:
                </strong>{" "}
                {rag.considerations}
              </p>
            )}
            {rag.note && (
              <p>
                <strong className="text-on-surface font-semibold">
                  Importante:
                </strong>{" "}
                {rag.note}
              </p>
            )}
          </div>
        </div>
      )}
    </>
  );
}

import type { RagResponse, RagSource } from "../types/pulso";

// Recomendaciones educativas del módulo RAG (POST /api/rag con analysis_id)

// Las fuentes actuales traen source, source_id, score y lines; `url` es opcional
// para cuando el RAG empiece a devolverla. Nunca se construyen enlaces propios.
function safeUrl(url: unknown): string | null {
  return typeof url === "string" && /^https?:\/\//i.test(url) ? url : null;
}

function SourceItem({ source }: { source: RagSource }) {
  const url = safeUrl(source.url);
  const lines = source.lines ? ` · Líneas ${source.lines.from}–${source.lines.to}` : "";

  return (
    <li className="flex items-start gap-1.5">
      <span className="material-symbols-outlined text-primary text-[16px] shrink-0 mt-0.5">
        bookmark
      </span>
      <span>
        {url ? (
          <a className="font-semibold text-primary hover:underline" href={url} rel="noopener noreferrer" target="_blank">
            {source.source}
          </a>
        ) : (
          <span className="font-semibold text-on-surface">
            {source.source}
          </span>
        )}
        <span className="text-on-surface-variant">
          {`${lines}`}
        </span>
      </span>
    </li>
  );
}

function uniqueSources(rag: RagResponse | null): RagSource[] {
  const sources = (rag?.recommendations || []).flatMap((item) => item.sources || []);
  return sources.filter(
    (source, index) => sources.findIndex((other) => other.source_id === source.source_id) === index
  );
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
              Información preventiva para este análisis
            </h3>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Solicita recomendaciones educativas basadas en este análisis, sus factores explicativos y la documentación disponible.
            </p>
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
            {loading ? "Consultando recomendaciones..." : "Solicitar recomendaciones"}
          </span>
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
            La documentación disponible no fue suficiente para generar recomendaciones específicas para este perfil. Se muestra la información general que pudo recuperarse.
          </p>
        </div>
      )}
      {rag.summary && (
        <div className="md:col-span-3 bg-surface-container-lowest rounded-xl shadow-sm p-space-md">
          <span className="font-label-sm uppercase font-semibold text-secondary tracking-wider">
            Resumen
          </span>
          <p className="font-body-lg text-body-lg text-on-surface mt-1">
            {rag.summary}
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
                  {item.sources.map((source) => (
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

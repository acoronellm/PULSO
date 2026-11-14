import { useEffect, useRef, useState } from "react";

import { getAnalysisHistory } from "../services/api";
import { errorText } from "../types/app";
import type { AnalysisHistoryItem } from "../types/pulso";

const PAGE_SIZE = 20;

function formatProbability(probability: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(probability);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");
  const [hasMore, setHasMore] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const requestId = useRef(0);

  useEffect(() => {
    const request = ++requestId.current;
    const controller = new AbortController();

    void getAnalysisHistory(PAGE_SIZE, 0, { signal: controller.signal })
      .then((page) => {
        if (request === requestId.current) {
          setAnalyses(page.items);
          setHasMore(page.has_more);
        }
      })
      .catch((cause: unknown) => {
        if (request === requestId.current && !controller.signal.aborted) {
          setError(errorText(cause));
        }
      })
      .finally(() => {
        if (request === requestId.current) setLoading(false);
      });

    return () => {
      controller.abort();
      requestId.current += 1;
    };
  }, [retryCount]);

  async function loadMore() {
    if (loadingMore || !hasMore) return;
    const request = ++requestId.current;
    setLoadingMore(true);
    setError("");
    try {
      const page = await getAnalysisHistory(PAGE_SIZE, analyses.length);
      if (request === requestId.current) {
        setAnalyses((current) => [...current, ...page.items]);
        setHasMore(page.has_more);
      }
    } catch (cause) {
      if (request === requestId.current) setError(errorText(cause));
    } finally {
      if (request === requestId.current) setLoadingMore(false);
    }
  }

  return (
    <main className="min-h-screen bg-surface-container-lowest px-margin-mobile pb-16 pt-36 md:px-margin">
      <section aria-labelledby="history-title" className="mx-auto max-w-4xl">
        <p className="font-label-sm font-semibold uppercase tracking-wider text-primary">
          Tu cuenta
        </p>
        <h1 className="mt-2 font-title-md text-3xl font-bold text-on-surface" id="history-title">
          Historial de análisis
        </h1>
        <p className="mt-2 font-body-md text-on-surface-variant">
          Aquí solo se muestran la fecha y el resultado de cada análisis.
        </p>

        {loading && (
          <p aria-live="polite" className="mt-8 font-body-md text-on-surface-variant">
            Cargando tu historial...
          </p>
        )}

        {error && (
          <div className="mt-8 rounded-xl bg-error-container p-4 text-on-error-container" role="alert">
            <p>{error}</p>
            <button
              className="mt-3 font-label-md font-semibold underline"
              onClick={() => {
                setLoading(true);
                setError("");
                setRetryCount((count) => count + 1);
              }}
              type="button"
            >
              Intentar de nuevo
            </button>
          </div>
        )}

        {!loading && !error && analyses.length === 0 && (
          <p className="mt-8 rounded-2xl border border-outline-variant/40 bg-surface-container-low p-6 font-body-md text-on-surface-variant">
            Todavía no tienes análisis guardados.
          </p>
        )}

        {!loading && analyses.length > 0 && (
          <ol aria-label="Resultados anteriores" className="mt-8 space-y-3">
            {analyses.map(({ analysis_id, created_at, prediction }) => (
              <li
                className="flex flex-col gap-3 rounded-2xl border border-outline-variant/40 bg-surface-container-lowest p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between"
                key={analysis_id}
              >
                <time className="font-label-md text-on-surface-variant" dateTime={created_at}>
                  {formatDate(created_at)}
                </time>
                <p className="font-title-md text-xl font-bold text-primary">
                  {formatProbability(prediction.probability)}
                </p>
              </li>
            ))}
          </ol>
        )}

        {hasMore && (
          <button
            className="mt-6 rounded-xl border border-primary px-5 py-3 font-label-md font-semibold text-primary disabled:opacity-60"
            disabled={loadingMore}
            onClick={() => void loadMore()}
            type="button"
          >
            {loadingMore ? "Cargando..." : "Cargar más resultados"}
          </button>
        )}
      </section>
    </main>
  );
}

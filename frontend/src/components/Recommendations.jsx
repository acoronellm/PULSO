function Recommendations({ rag, loading, error, onRequest }) {
  return (
    <section className="card">
      <h2>Información preventiva personalizada</h2>

      {!rag && (
        <>
          <p>
            Puedes solicitar recomendaciones educativas basadas en este
            análisis y en sus factores explicativos.
          </p>
          <button
            type="button"
            onClick={onRequest}
            disabled={loading}
          >
            {loading
              ? "Consultando recomendaciones..."
              : "Solicitar recomendaciones"}
          </button>
        </>
      )}

      {error && <p className="error-message">{error}</p>}

      {rag && (
        <>
      {rag.summary && (
        <div className="rag-summary">
          <h3>Resumen</h3>
          <p>{rag.summary}</p>
        </div>
      )}

      {rag.recommendations?.length > 0 && (
        <div className="recommendation-list">
          {rag.recommendations.map((item, index) => (
            <article className="recommendation-item" key={index}>
              <h3>{item.factor}</h3>

              <p>{item.recommendation}</p>

              {item.sources?.length > 0 && (
                <details>
                  <summary>Consultar fuentes utilizadas</summary>

                  <div className="source-list">
                    {item.sources.map((source) => (
                      <div
                        className="source-item"
                        key={source.source_id}
                      >
                        <strong>{source.source}</strong>

                        <p>
                          Referencia: {source.source_id}
                        </p>

                        {source.lines && (
                          <p>
                            Líneas {source.lines.from}–{source.lines.to}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </article>
          ))}
        </div>
      )}

      {rag.considerations && (
        <div className="info-box">
          <strong>Consideraciones:</strong>
          <p>{rag.considerations}</p>
        </div>
      )}

      {rag.note && (
        <div className="warning-box">
          <strong>Importante:</strong>
          <p>{rag.note}</p>
        </div>
      )}
        </>
      )}
    </section>
  );
}

export default Recommendations;
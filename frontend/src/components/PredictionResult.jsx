function PredictionResult({ prediction }) {
  if (!prediction) {
    return null;
  }

  const probabilityPercentage = (
    prediction.probability * 100
  ).toFixed(1);

  const thresholdPercentage = (
    prediction.threshold * 100
  ).toFixed(0);

  return (
    <section className="card">
      <h2>Resultado estimado por PULSO</h2>

      <div className="prediction-number">
        {probabilityPercentage}%
      </div>

      <p>
        Probabilidad estimada por el modelo.
      </p>

      <p>
        Umbral de referencia del sistema:{" "}
        <strong>{thresholdPercentage}%</strong>
      </p>

      <p>
        Clasificación del modelo:{" "}
        <strong>
          {prediction.classification === 1
            ? "Por encima del umbral"
            : "Por debajo del umbral"}
        </strong>
      </p>

      <div className="warning-box">
        Este resultado tiene fines educativos y preventivos. PULSO no realiza
        diagnósticos médicos y no sustituye la valoración de un profesional de
        la salud.
      </div>
    </section>
  );
}

export default PredictionResult;
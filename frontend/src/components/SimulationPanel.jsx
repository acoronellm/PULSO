import { useState } from "react";
import { simulateScenario } from "../services/api";

function SimulationPanel({ originalProfile, originalPrediction }) {
  const [changes, setChanges] = useState({
    weight: "",
    ap_hi: "",
    ap_lo: "",
    smoke: "",
    alco: "",
    active: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setChanges((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSimulate() {
    try {
      setLoading(true);
      setError("");
      setResult(null);

      const payloadChanges = {};

      if (changes.weight !== "") {
        payloadChanges.weight = Number(changes.weight);
      }

      if (changes.ap_hi !== "") {
        payloadChanges.ap_hi = Number(changes.ap_hi);
      }

      if (changes.ap_lo !== "") {
        payloadChanges.ap_lo = Number(changes.ap_lo);
      }

      if (changes.smoke !== "") {
        payloadChanges.smoke = Number(changes.smoke);
      }

      if (changes.alco !== "") {
        payloadChanges.alco = Number(changes.alco);
      }

      if (changes.active !== "") {
        payloadChanges.active = Number(changes.active);
      }

      if (Object.keys(payloadChanges).length === 0) {
        setError("Selecciona al menos un cambio para realizar la simulación.");
        return;
      }

      const response = await simulateScenario({
        original: originalProfile,
        changes: payloadChanges,
      });

      setResult(response);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  const originalPercentage = result
    ? (result.original.probability * 100).toFixed(1)
    : originalPrediction
    ? (originalPrediction.probability * 100).toFixed(1)
    : null;

  const simulatedPercentage = result
    ? (result.simulated.probability * 100).toFixed(1)
    : null;

  const differencePercentage = result
    ? (result.probability_difference * 100).toFixed(1)
    : null;

  return (
    <section className="card">
      <h2>Explora un escenario hipotético</h2>

      <p className="section-description">
        Modifica uno o varios factores para observar cómo cambiaría la salida
        del modelo en un escenario hipotético.
      </p>

      <div className="form-grid">
        <label>
          Nuevo peso (kg)
          <input
            type="number"
            name="weight"
            value={changes.weight}
            onChange={handleChange}
            min="30"
            max="200"
            step="0.1"
            placeholder={`Actual: ${originalProfile.weight}`}
          />
        </label>

        <label>
          Nueva presión sistólica
          <input
            type="number"
            name="ap_hi"
            value={changes.ap_hi}
            onChange={handleChange}
            min="70"
            max="250"
            placeholder={`Actual: ${originalProfile.ap_hi}`}
          />
        </label>

        <label>
          Nueva presión diastólica
          <input
            type="number"
            name="ap_lo"
            value={changes.ap_lo}
            onChange={handleChange}
            min="40"
            max="150"
            placeholder={`Actual: ${originalProfile.ap_lo}`}
          />
        </label>

        <label>
          Tabaquismo
          <select
            name="smoke"
            value={changes.smoke}
            onChange={handleChange}
          >
            <option value="">Mantener valor actual</option>
            <option value="0">No</option>
            <option value="1">Sí</option>
          </select>
        </label>

        <label>
          Consumo de alcohol
          <select
            name="alco"
            value={changes.alco}
            onChange={handleChange}
          >
            <option value="">Mantener valor actual</option>
            <option value="0">No</option>
            <option value="1">Sí</option>
          </select>
        </label>

        <label>
          Actividad física
          <select
            name="active"
            value={changes.active}
            onChange={handleChange}
          >
            <option value="">Mantener valor actual</option>
            <option value="1">Sí</option>
            <option value="0">No</option>
          </select>
        </label>
      </div>

      {error && <p className="error-message">{error}</p>}

      <button type="button" onClick={handleSimulate} disabled={loading}>
        {loading ? "Simulando..." : "Simular escenario"}
      </button>

      {result && (
        <div className="simulation-result">
          <div className="simulation-comparison">
            <div className="simulation-box">
              <span>Resultado original</span>
              <strong>{originalPercentage}%</strong>
            </div>

            <div className="simulation-arrow">→</div>

            <div className="simulation-box">
              <span>Resultado simulado</span>
              <strong>{simulatedPercentage}%</strong>
            </div>
          </div>

          <div className="difference-box">
            Diferencia:{" "}
            <strong>
              {differencePercentage > 0 ? "+" : ""}
              {differencePercentage} puntos porcentuales
            </strong>
          </div>

          <p>
            Clasificación simulada:{" "}
            <strong>
              {result.simulated.classification === 1
                ? "Por encima del umbral"
                : "Por debajo del umbral"}
            </strong>
          </p>

          <div className="warning-box">
            Esta simulación representa únicamente cómo responde el modelo ante
            cambios en sus variables de entrada. No demuestra causalidad, no
            predice el efecto clínico real de una intervención y no constituye
            una recomendación médica.
          </div>
        </div>
      )}
    </section>
  );
}

export default SimulationPanel;
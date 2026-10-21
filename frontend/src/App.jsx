import { useState } from "react";
import "./App.css";

import HealthForm from "./components/HealthForm";
import PredictionResult from "./components/PredictionResult";
import { analyzeProfile } from "./services/api";
import ShapFactors from "./components/ShapFactors";
import Recommendations from "./components/Recommendations";
import SimulationPanel from "./components/SimulationPanel";
function App() {
  const [analysis, setAnalysis] = useState(null);
  const [originalProfile, setOriginalProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze(userData) {
    try {
      setLoading(true);
      setError("");
      setAnalysis(null);

      const result = await analyzeProfile(userData);

      setOriginalProfile(userData);
      setAnalysis(result);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>PULSO</h1>
          <p>
            Predicción explicable y educación preventiva cardiovascular
          </p>
        </div>
      </header>

      <main className="main-content">
        <section className="intro">
          <h2>Comprende mejor tus factores cardiovasculares</h2>

          <p>
            PULSO utiliza Machine Learning para generar una estimación
            educativa, explicar los factores que influyen en ella y explorar
            escenarios hipotéticos.
          </p>
        </section>

        <HealthForm
          onSubmit={handleAnalyze}
          loading={loading}
        />

        {error && (
          <section className="card error-card">
            <h2>No fue posible completar el análisis</h2>
            <p>{error}</p>
          </section>
        )}

        {analysis && (
          <>
            <PredictionResult prediction={analysis.prediction} />

            <ShapFactors shap={analysis.shap} />

            <Recommendations rag={analysis.rag} />
            <SimulationPanel
              originalProfile={originalProfile}
              originalPrediction={analysis.prediction}
            />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
import { useRef, useState } from "react";
import "./App.css";

import HealthForm from "./components/HealthForm";
import PredictionResult from "./components/PredictionResult";
import {
  analyzeProfile,
  requestRecommendations,
} from "./services/api";
import ShapFactors from "./components/ShapFactors";
import Recommendations from "./components/Recommendations";
import SimulationPanel from "./components/SimulationPanel";
function App() {
  const [analysis, setAnalysis] = useState(null);
  const [originalProfile, setOriginalProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [recommendationsLoading, setRecommendationsLoading] =
    useState(false);
  const [recommendationsError, setRecommendationsError] = useState("");
  const analysisVersion = useRef(0);
  const currentAnalysisId = useRef(null);
  const recommendationsRequest = useRef(null);

  async function handleAnalyze(userData) {
    const requestVersion = analysisVersion.current + 1;
    analysisVersion.current = requestVersion;
    currentAnalysisId.current = null;
    recommendationsRequest.current?.abort();

    try {
      setLoading(true);
      setError("");
      setAnalysis(null);
      setRecommendations(null);
      setRecommendationsLoading(false);
      setRecommendationsError("");

      const result = await analyzeProfile(userData);

      if (analysisVersion.current !== requestVersion) {
        return;
      }

      setOriginalProfile(userData);
      setAnalysis(result);
      currentAnalysisId.current = result.analysis_id;
    } catch (error) {
      if (analysisVersion.current !== requestVersion) {
        return;
      }
      setError(error.message);
    } finally {
      if (analysisVersion.current === requestVersion) {
        setLoading(false);
      }
    }
  }

  async function handleRecommendations() {
    if (!analysis || !originalProfile) {
      return;
    }

    const requestVersion = analysisVersion.current;
    const requestedAnalysisId = analysis.analysis_id;
    const controller = new AbortController();
    recommendationsRequest.current?.abort();
    recommendationsRequest.current = controller;

    try {
      setRecommendationsLoading(true);
      setRecommendationsError("");

      const result = await requestRecommendations({
        analysis_id: requestedAnalysisId,
      }, {
        signal: controller.signal,
      });

      if (
        analysisVersion.current !== requestVersion ||
        currentAnalysisId.current !== requestedAnalysisId
      ) {
        return;
      }
      setRecommendations(result);
    } catch (error) {
      if (
        error.name === "AbortError" ||
        analysisVersion.current !== requestVersion ||
        currentAnalysisId.current !== requestedAnalysisId
      ) {
        return;
      }
      setRecommendationsError(error.message);
    } finally {
      if (
        analysisVersion.current === requestVersion &&
        currentAnalysisId.current === requestedAnalysisId
      ) {
        setRecommendationsLoading(false);
      }
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

            <Recommendations
              rag={recommendations}
              loading={recommendationsLoading}
              error={recommendationsError}
              onRequest={handleRecommendations}
            />
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
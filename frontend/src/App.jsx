import { useEffect, useRef, useState } from "react";

import Footer from "./components/Footer";
import Header from "./components/Header";
import EvaluationPage from "./pages/EvaluationPage";
import HistoryPage from "./pages/HistoryPage";
import LoginPage from "./pages/LoginPage";
import ResultPage from "./pages/ResultPage";
import SimulationPage from "./pages/SimulationPage";
import {
  analyzeProfile,
  requestRecommendations,
} from "./services/api";
import { DEMO_FORM, formToPayload } from "./utils/health";

const PAGES_WITH_SCREEN = ["login", "evaluacion", "resultado", "historial", "simulacion"];

function App() {
  const [view, setView] = useState("login");
  const [form, setForm] = useState(DEMO_FORM);
  const [analysis, setAnalysis] = useState(null);
  const [originalProfile, setOriginalProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [recommendationsLoading, setRecommendationsLoading] =
    useState(false);
  const [recommendationsError, setRecommendationsError] = useState("");
  const analysisVersion = useRef(0);
  const currentAnalysisId = useRef(null);
  const recommendationsRequest = useRef(null);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view]);

  function navigate(path) {
    if (PAGES_WITH_SCREEN.includes(path)) {
      setView(path);
    }
  }

  function updateForm(name, value) {
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  function resetAnalysis() {
    analysisVersion.current += 1;
    currentAnalysisId.current = null;
    recommendationsRequest.current?.abort();
    setAnalysis(null);
    setOriginalProfile(null);
    setLoading(false);
    setRecommendations(null);
    setRecommendationsLoading(false);
    setRecommendationsError("");
  }

  // Muestra la pantalla de resultado con los datos de ejemplo de Stitch
  function handleQuickDemo() {
    resetAnalysis();
    setView("resultado");
  }

  async function handleAnalyze(notify) {
    const userData = formToPayload(form);
    const requestVersion = analysisVersion.current + 1;
    analysisVersion.current = requestVersion;
    currentAnalysisId.current = null;
    recommendationsRequest.current?.abort();

    try {
      setLoading(true);
      setAnalysisError("");
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
      setView("resultado");
    } catch (error) {
      if (analysisVersion.current !== requestVersion) {
        return;
      }
      // fetch lanza TypeError cuando no hay conexión con el servidor
      const message = error instanceof TypeError
        ? "No se pudo conectar con el servidor de PULSO. Verifica que el backend esté activo."
        : error.message;
      setAnalysisError(message);
      notify(message);
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

  if (view === "login") {
    return <LoginPage onLogin={() => setView("evaluacion")} />;
  }

  return (
    <>
      <Header
        active={view === "resultado" ? "evaluacion" : view}
        onNavigate={navigate}
        onQuickDemo={handleQuickDemo}
      />

      {view === "evaluacion" && (
        <EvaluationPage
          form={form}
          onChange={updateForm}
          onSubmit={handleAnalyze}
          loading={loading}
          error={analysisError}
        />
      )}

      {view === "resultado" && (
        <ResultPage
          analysis={analysis}
          profile={originalProfile}
          recommendations={recommendations}
          recommendationsLoading={recommendationsLoading}
          recommendationsError={recommendationsError}
          onRequestRecommendations={handleRecommendations}
          onNavigate={navigate}
        />
      )}

      {view === "historial" && <HistoryPage onNavigate={navigate} />}

      {view === "simulacion" && (
        <SimulationPage
          analysis={analysis}
          profile={originalProfile}
          onNavigate={navigate}
        />
      )}

      <Footer />
    </>
  );
}

export default App;

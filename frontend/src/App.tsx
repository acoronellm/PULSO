import { useEffect, useRef, useState } from "react";

import Footer from "./components/Footer";
import Header from "./components/Header";
import EvaluationPage from "./pages/EvaluationPage";
import ResultPage from "./pages/ResultPage";
import SimulationPage from "./pages/SimulationPage";
import {
  analyzeProfile,
  requestRecommendations,
} from "./services/api";
import type { ShowToast } from "./hooks/useToast";
import { errorText, isAbortError, type View } from "./types/app";
import type { AnalysisResponse, RagResponse, UserData } from "./types/pulso";
import { EMPTY_FORM, formToPayload, type FormField, type FormState } from "./utils/health";

// PULSO v1 no tiene cuentas ni historial: solo evaluación, resultado y simulación
const PAGES_WITH_SCREEN: View[] = ["evaluacion", "resultado", "simulacion"];

function App() {
  const [view, setView] = useState<View>("evaluacion");
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [originalProfile, setOriginalProfile] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");
  const [recommendations, setRecommendations] = useState<RagResponse | null>(null);
  const [recommendationsLoading, setRecommendationsLoading] =
    useState(false);
  const [recommendationsError, setRecommendationsError] = useState("");
  const analysisVersion = useRef(0);
  const currentAnalysisId = useRef<string | null>(null);
  const recommendationsRequest = useRef<AbortController | null>(null);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view]);

  function navigate(path: View) {
    if (!PAGES_WITH_SCREEN.includes(path)) {
      return;
    }
    // El resultado solo existe después de un análisis real
    if (path === "resultado" && !analysis) {
      return;
    }
    setView(path);
  }

  function updateForm<K extends FormField>(name: K, value: FormState[K]) {
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  async function handleAnalyze(notify: ShowToast) {
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
        : errorText(error);
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
        isAbortError(error) ||
        analysisVersion.current !== requestVersion ||
        currentAnalysisId.current !== requestedAnalysisId
      ) {
        return;
      }
      setRecommendationsError(errorText(error));
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
    <>
      <Header
        active={view}
        hasResult={Boolean(analysis)}
        onNavigate={navigate}
      />

      {view === "evaluacion" && (
        <EvaluationPage
          form={form}
          onChange={updateForm}
          onFillExample={(example: FormState) => setForm(example)}
          onSubmit={handleAnalyze}
          loading={loading}
          error={analysisError}
        />
      )}

      {view === "resultado" && analysis && originalProfile && (
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

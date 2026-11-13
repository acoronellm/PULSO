import { useEffect, useRef, useState } from "react";

import Footer from "./components/Footer";
import Header from "./components/Header";
import AuthPage from "./pages/AuthPage";
import EvaluationPage from "./pages/EvaluationPage";
import HistoryPage from "./pages/HistoryPage";
import ResultPage from "./pages/ResultPage";
import SimulationPage from "./pages/SimulationPage";
import {
  analyzeProfile,
  clearAccessToken,
  getAccessToken,
  getCurrentUser,
  login,
  register,
  requestRecommendations,
} from "./services/api";
import type { ShowToast } from "./hooks/useToast";
import { errorText, isAbortError, type View } from "./types/app";
import type { AnalysisResponse, AuthResponse, AuthUser, RagResponse, UserData } from "./types/pulso";
import { EMPTY_FORM, formToPayload, type FormField, type FormState } from "./utils/health";

const PAGES_WITH_SCREEN: View[] = ["evaluacion", "resultado", "simulacion", "historial"];

function App() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [authLoading, setAuthLoading] = useState(() => Boolean(getAccessToken()));
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
    let active = true;
    const savedToken = getAccessToken();
    if (!savedToken) {
      return;
    }

    void getCurrentUser()
      .then((authenticatedUser) => {
        if (active) setUser(authenticatedUser);
      })
      .catch(() => {
        clearAccessToken();
        if (active) setUser(null);
      })
      .finally(() => {
        if (active) setAuthLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    function handleUnauthorized() {
      analysisVersion.current += 1;
      currentAnalysisId.current = null;
      recommendationsRequest.current?.abort();
      setUser(null);
      setAnalysis(null);
      setOriginalProfile(null);
      setRecommendations(null);
      setLoading(false);
      setRecommendationsLoading(false);
      setView("evaluacion");
    }
    window.addEventListener("pulso:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("pulso:unauthorized", handleUnauthorized);
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view]);

  async function handleAuth(mode: "login" | "register", email: string, password: string) {
    const response: AuthResponse = mode === "login"
      ? await login({ email, password })
      : await register({ email, password });
    setUser(response.user);
    return response;
  }

  function handleLogout() {
    analysisVersion.current += 1;
    currentAnalysisId.current = null;
    recommendationsRequest.current?.abort();
    clearAccessToken();
    setUser(null);
    setAnalysis(null);
    setOriginalProfile(null);
    setRecommendations(null);
    setLoading(false);
    setRecommendationsLoading(false);
    setView("evaluacion");
  }

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

  if (authLoading) {
    return (
      <main aria-live="polite" className="min-h-screen flex items-center justify-center bg-surface-container-lowest font-label-md text-on-surface-variant">
        Verificando sesión...
      </main>
    );
  }

  if (!user) {
    return <AuthPage onSubmit={handleAuth} />;
  }

  return (
    <>
      <Header
        active={view}
        email={user.email}
        hasResult={Boolean(analysis)}
        onNavigate={navigate}
        onLogout={handleLogout}
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

      {view === "historial" && <HistoryPage />}

      <Footer />
    </>
  );
}

export default App;

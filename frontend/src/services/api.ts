import type {
  AnalysisResponse,
  RagRequest,
  RagResponse,
  RequestOptions,
  SimulationRequest,
  SimulationResponse,
  UserData,
} from "../types/pulso";

const API_URL: string = import.meta.env.VITE_API_URL || "";

interface ValidationError {
  msg: string;
}

interface ErrorBody {
  detail?: string | ValidationError[];
}

// FastAPI devuelve `detail` como texto o como lista de errores de validación (422)
function errorMessage(errorData: ErrorBody | null, fallback: string): string {
  const detail = errorData?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(" ") || fallback;
  }
  return detail || fallback;
}

async function postJson<T>(
  path: string,
  body: unknown,
  fallbackError: string,
  options: RequestOptions = {}
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    signal: options.signal,
  });

  if (!response.ok) {
    const errorData = (await response.json().catch(() => null)) as ErrorBody | null;
    throw new Error(errorMessage(errorData, fallbackError));
  }

  return response.json() as Promise<T>;
}

export function analyzeProfile(userData: UserData): Promise<AnalysisResponse> {
  return postJson<AnalysisResponse>(
    "/api/analyze",
    userData,
    "No fue posible analizar el perfil."
  );
}

export function requestRecommendations(
  context: RagRequest,
  options: RequestOptions = {}
): Promise<RagResponse> {
  return postJson<RagResponse>(
    "/api/rag",
    context,
    "No fue posible obtener recomendaciones preventivas.",
    options
  );
}

export function simulateScenario(
  payload: SimulationRequest,
  options: RequestOptions = {}
): Promise<SimulationResponse> {
  return postJson<SimulationResponse>(
    "/api/simulate",
    payload,
    "No fue posible realizar la simulación.",
    options
  );
}

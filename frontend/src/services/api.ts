import type {
  AuthResponse,
  AuthUser,
  AnalysisResponse,
  AnalysisHistoryResponse,
  RagRequest,
  RagResponse,
  RequestOptions,
  SimulationRequest,
  SimulationResponse,
  UserData,
} from "../types/pulso";

const API_URL: string = import.meta.env.VITE_API_URL || "";
const ACCESS_TOKEN_KEY = "pulso_access_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function clearAccessToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
}

function saveAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

function unauthorized(): void {
  clearAccessToken();
  window.dispatchEvent(new Event("pulso:unauthorized"));
}

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
  const token = getAccessToken();
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
    signal: options.signal,
  });

  if (!response.ok) {
    if (response.status === 401 && path !== "/api/auth/login" && path !== "/api/auth/register") {
      unauthorized();
    }
    const errorData = (await response.json().catch(() => null)) as ErrorBody | null;
    throw new Error(errorMessage(errorData, fallbackError));
  }

  return response.json() as Promise<T>;
}

async function getJson<T>(
  path: string,
  fallbackError: string,
  options: RequestOptions = {}
): Promise<T> {
  const token = getAccessToken();
  const response = await fetch(`${API_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    signal: options.signal,
  });
  if (!response.ok) {
    if (response.status === 401) {
      unauthorized();
    }
    const errorData = (await response.json().catch(() => null)) as ErrorBody | null;
    throw new Error(errorMessage(errorData, fallbackError));
  }
  return response.json() as Promise<T>;
}

async function authenticate(
  path: "/api/auth/login" | "/api/auth/register",
  credentials: { email: string; password: string }
): Promise<AuthResponse> {
  const result = await postJson<AuthResponse>(
    path,
    credentials,
    path.endsWith("login") ? "No fue posible iniciar sesión." : "No fue posible crear la cuenta."
  );
  saveAccessToken(result.access_token);
  return result;
}

export function login(credentials: { email: string; password: string }): Promise<AuthResponse> {
  return authenticate("/api/auth/login", credentials);
}

export function register(credentials: { email: string; password: string }): Promise<AuthResponse> {
  return authenticate("/api/auth/register", credentials);
}

export function getCurrentUser(): Promise<AuthUser> {
  return getJson<AuthUser>("/api/auth/me", "La sesión expiró. Inicia sesión de nuevo.");
}

export function analyzeProfile(userData: UserData): Promise<AnalysisResponse> {
  return postJson<AnalysisResponse>(
    "/api/analyze",
    userData,
    "No fue posible analizar el perfil."
  );
}

export function getAnalysisHistory(
  limit = 20,
  offset = 0,
  options: RequestOptions = {}
): Promise<AnalysisHistoryResponse> {
  const query = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return getJson<AnalysisHistoryResponse>(
    `/api/analyses?${query.toString()}`,
    "No fue posible cargar tu historial.",
    options
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

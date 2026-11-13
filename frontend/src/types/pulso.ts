// Contratos de la API de PULSO, tal como los define backend/app/interfaces/http/schemas.py

export type Binary = 0 | 1;

// Perfil enviado a /api/analyze (UserData)
export interface UserData {
  gender: 1 | 2;
  height: number;
  weight: number;
  ap_hi: number;
  ap_lo: number;
  smoke: Binary;
  alco: Binary;
  active: Binary;
  age_years: number;
  bmi: number;
}

export interface AuthUser {
  id: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: AuthUser;
}

export type Feature = keyof UserData;

export interface Prediction {
  probability: number;
  classification: Binary;
  threshold: number;
  model_version: string;
}

export interface ShapFactor {
  feature: Feature | string;
  value: number;
  shap_value: number;
  direction: "increase" | "decrease";
}

export interface AnalysisResponse {
  analysis_id: string;
  prediction: Prediction;
  shap: {
    top_factors: ShapFactor[];
  };
}

export interface AnalysisHistoryItem {
  analysis_id: string;
  created_at: string;
  prediction: Prediction;
}

export interface AnalysisHistoryResponse {
  items: AnalysisHistoryItem[];
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface RagRequest {
  analysis_id: string;
}

export interface RagSource {
  source_id: string;
  source: string;
  score: number;
  lines: {
    from: number;
    to: number;
  };
  // Aún no lo envía el RAG; se admite para la actualización con URLs documentales
  url?: string;
}

export interface RagRecommendation {
  factor: string;
  recommendation: string;
  source_ids?: string[];
  sources?: RagSource[];
}

export interface RagResponse {
  summary: string;
  recommendations: RagRecommendation[];
  considerations: string;
  note: string;
  insufficient_information: boolean;
}

// Variables que /api/simulate permite cambiar (SimulationChanges)
export interface SimulationChanges {
  weight?: number;
  ap_hi?: number;
  ap_lo?: number;
  smoke?: Binary;
  alco?: Binary;
  active?: Binary;
}

export interface SimulationRequest {
  original: UserData;
  changes: SimulationChanges;
}

export interface SimulationResult {
  probability: number;
  classification: Binary;
}

export interface SimulationResponse {
  original: SimulationResult;
  simulated: SimulationResult;
  probability_difference: number;
  applied_changes: Record<string, unknown>;
  model_version: string;
  threshold: number;
}

export interface RequestOptions {
  signal?: AbortSignal;
}

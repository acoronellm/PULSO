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

export interface RagRequest {
  analysis_id: string;
}

export interface RagSource {
  source_id: string;
  source: string;
  author?: string | null;
  publication_year?: number | null;
  source_url?: string | null;
  pdf_url?: string | null;
  score?: number | null;
  lines?: {
    from: number;
    to: number;
  } | null;
  // Compatibilidad con referencias anteriores.
  url?: string | null;
}

export interface RagRecommendation {
  factor: string;
  recommendation: string;
  source_ids?: string[];
  sources?: RagSource[];
}

export interface RagFactorExplanation {
  query_group: string;
  factor: string;
  features: string[];
  explanation: string;
  source_ids: string[];
  sources: RagSource[];
}

export interface RagResponse {
  summary: string;
  recommendations: RagRecommendation[];
  factor_explanations: RagFactorExplanation[];
  considerations: string;
  note: string;
  insufficient_information: boolean;
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

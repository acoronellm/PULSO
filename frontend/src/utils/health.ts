import type { Binary, UserData } from "../types/pulso";

// Valores del formulario de evaluación: los campos numéricos se guardan como texto
export interface FormState {
  edad: string;
  sexo: "mujer" | "hombre";
  estatura: string;
  peso: string;
  sistolica: string;
  diastolica: string;
  tabaco: boolean;
  alcohol: boolean;
  ejercicio: boolean;
}

export type FormField = keyof FormState;

// El formulario empieza vacío: PULSO v1 no guarda perfiles ni usa datos de demostración
export const EMPTY_FORM: FormState = {
  edad: "",
  sexo: "mujer",
  estatura: "",
  peso: "",
  sistolica: "",
  diastolica: "",
  tabaco: false,
  alcohol: false,
  ejercicio: false,
};

// Perfil sintético que la persona puede cargar explícitamente para probar la herramienta
export const EXAMPLE_FORM: FormState = {
  edad: "52",
  sexo: "mujer",
  estatura: "165",
  peso: "72.0",
  sistolica: "135",
  diastolica: "85",
  tabaco: false,
  alcohol: false,
  ejercicio: true,
};

export function calculateBmi(heightCm: number, weightKg: number): number {
  const meters = heightCm / 100;
  return weightKg / (meters * meters);
}

// Payload esperado por POST /api/analyze
function toBinary(value: boolean): Binary {
  return value ? 1 : 0;
}

export function formToPayload(form: FormState): UserData {
  const height = Number(form.estatura);
  const weight = Number(form.peso);

  return {
    gender: form.sexo === "mujer" ? 1 : 2,
    height,
    weight,
    ap_hi: Number(form.sistolica),
    ap_lo: Number(form.diastolica),
    smoke: toBinary(form.tabaco),
    alco: toBinary(form.alcohol),
    active: toBinary(form.ejercicio),
    age_years: Number(form.edad),
    bmi: Number(calculateBmi(height, weight).toFixed(2)),
  };
}

// Probabilidad con un decimal y coma decimal, por ejemplo 0.6337 -> "63,4"
export function formatProbability(probability: number): string {
  return (probability * 100).toFixed(1).replace(".", ",");
}

// Umbral sin decimales innecesarios, por ejemplo 0.38 -> "38" y 0.425 -> "42,5"
export function formatThreshold(threshold: number): string {
  return String(Number((threshold * 100).toFixed(1))).replace(".", ",");
}

export function genderLabel(gender: UserData["gender"]): string {
  return gender === 1 ? "Mujer" : "Hombre";
}

const FEATURE_NAMES: Record<string, string> = {
  ap_hi: "Presión sistólica",
  ap_lo: "Presión diastólica",
  weight: "Peso",
  height: "Altura",
  smoke: "Tabaquismo",
  alco: "Consumo de alcohol",
  active: "Actividad física",
  age_years: "Edad",
  bmi: "Índice de masa corporal",
  gender: "Sexo",
};

const FEATURE_ICONS: Record<string, string> = {
  ap_hi: "speed",
  ap_lo: "compress",
  weight: "scale",
  height: "height",
  smoke: "smoking_rooms",
  alco: "local_bar",
  active: "directions_walk",
  age_years: "cake",
  bmi: "balance",
  gender: "wc",
};

export function featureName(feature: string): string {
  return FEATURE_NAMES[feature] || feature;
}

export function featureIcon(feature: string): string {
  return FEATURE_ICONS[feature] || "insights";
}

export function featureValue(feature: string, value: number): string {
  if (feature === "smoke" || feature === "alco" || feature === "active") {
    return value === 1 ? "Sí" : "No";
  }
  if (feature === "gender") {
    return value === 1 ? "Mujer" : "Hombre";
  }
  if (feature === "ap_hi" || feature === "ap_lo") {
    return `${value} mmHg`;
  }
  if (feature === "weight") {
    return `${value} kg`;
  }
  if (feature === "height") {
    return `${value} cm`;
  }
  if (feature === "age_years") {
    return `${value} años`;
  }
  if (feature === "bmi") {
    return `${Number(value).toFixed(1)} kg/m²`;
  }
  return String(value);
}

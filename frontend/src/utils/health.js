// Valores del perfil demo de Stitch (Clara Méndez), como texto de los campos
export const DEMO_FORM = {
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

export const DEMO_PERCENT = 28;

export function calculateBmi(heightCm, weightKg) {
  const meters = heightCm / 100;
  return weightKg / (meters * meters);
}

// Payload esperado por POST /api/analyze
export function formToPayload(form) {
  const height = Number(form.estatura);
  const weight = Number(form.peso);

  return {
    gender: form.sexo === "mujer" ? 1 : 2,
    height,
    weight,
    ap_hi: Number(form.sistolica),
    ap_lo: Number(form.diastolica),
    smoke: form.tabaco ? 1 : 0,
    alco: form.alcohol ? 1 : 0,
    active: form.ejercicio ? 1 : 0,
    age_years: Number(form.edad),
    bmi: Number(calculateBmi(height, weight).toFixed(2)),
  };
}

export function toPercent(probability) {
  return Math.round(probability * 100);
}

const FEATURE_NAMES = {
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

const FEATURE_ICONS = {
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

export function featureName(feature) {
  return FEATURE_NAMES[feature] || feature;
}

export function featureIcon(feature) {
  return FEATURE_ICONS[feature] || "insights";
}

export function featureValue(feature, value) {
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
  return value;
}

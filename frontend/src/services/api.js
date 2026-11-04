const API_URL = import.meta.env.VITE_API_URL || "";

// FastAPI devuelve `detail` como texto o como lista de errores de validación (422)
function errorMessage(errorData, fallback) {
  const detail = errorData?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(" ") || fallback;
  }
  return detail || fallback;
}

export async function analyzeProfile(userData) {
  const response = await fetch(`${API_URL}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorMessage(errorData, "No fue posible analizar el perfil.")
    );
  }

  return response.json();
}

export async function requestRecommendations(context, options = {}) {
  const response = await fetch(`${API_URL}/api/rag`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(context),
    signal: options.signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorMessage(errorData, "No fue posible obtener recomendaciones preventivas.")
    );
  }

  return response.json();
}

export async function simulateScenario(payload) {
  const response = await fetch(`${API_URL}/api/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorMessage(errorData, "No fue posible realizar la simulación.")
    );
  }

  return response.json();
}
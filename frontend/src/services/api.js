const API_URL = import.meta.env.VITE_API_URL || "";

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
      errorData?.detail || "No fue posible analizar el perfil."
    );
  }

  return response.json();
}

export async function requestRecommendations(context) {
  const response = await fetch(`${API_URL}/api/rag`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(context),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.detail ||
        "No fue posible obtener recomendaciones preventivas."
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
      errorData?.detail || "No fue posible realizar la simulación."
    );
  }

  return response.json();
}
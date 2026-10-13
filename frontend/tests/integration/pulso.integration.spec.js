import { test, expect } from "@playwright/test";


async function fillHealthForm(page) {
  await page.getByLabel("Sexo").selectOption("1");

  await page.getByLabel("Edad").fill("50");

  await page.getByLabel("Altura (cm)").fill("172");

  await page.getByLabel("Peso (kg)").fill("72");

  await page
    .getByLabel("Presión sistólica (mmHg)")
    .fill("120");

  await page
    .getByLabel("Presión diastólica (mmHg)")
    .fill("80");

  await page.getByLabel("¿Fuma?").selectOption("0");

  await page
    .getByLabel("¿Consume alcohol?")
    .selectOption("0");

  await page
    .getByLabel("¿Realiza actividad física?")
    .selectOption("1");
}


async function performAnalysis(page) {
  await fillHealthForm(page);

  const responsePromise = page.waitForResponse(
    (response) =>
      response.url().includes("/api/analyze") &&
      response.request().method() === "POST"
  );

  await page
    .getByRole("button", {
      name: "Analizar mi perfil",
    })
    .click();

  const response = await responsePromise;

  return response;
}


test(
  "PI-05 - realiza un análisis completo desde el frontend",
  async ({ page }) => {
    await page.goto("/");

    await expect(
      page.getByRole("heading", {
        name: "PULSO",
      })
    ).toBeVisible();

    const response = await performAnalysis(page);

    expect(response.status()).toBe(200);

    const body = await response.json();

    expect(body).toHaveProperty("prediction");
    expect(body).toHaveProperty("shap");
    expect(body).toHaveProperty("rag");

    expect(
      body.prediction.probability
    ).toBeGreaterThanOrEqual(0);

    expect(
      body.prediction.probability
    ).toBeLessThanOrEqual(1);

    expect(
      [0, 1]
    ).toContain(
      body.prediction.classification
    );

    expect(body.prediction.threshold).toBe(0.38);

    expect(body.prediction.model_version).toBe("v1");

    expect(
      Array.isArray(body.shap.top_factors)
    ).toBeTruthy();

    expect(
      body.shap.top_factors.length
    ).toBeGreaterThan(0);

    expect(
      typeof body.rag.summary
    ).toBe("string");

    expect(
      Array.isArray(body.rag.recommendations)
    ).toBeTruthy();

    await expect(
      page.getByRole("heading", {
        name: "Explora un escenario hipotético",
      })
    ).toBeVisible();
  }
);


test(
  "PI-06 - realiza una simulación desde el frontend",
  async ({ page }) => {
    await page.goto("/");

    const analysisResponse =
      await performAnalysis(page);

    expect(
      analysisResponse.status()
    ).toBe(200);

    await expect(
      page.getByRole("heading", {
        name: "Explora un escenario hipotético",
      })
    ).toBeVisible();

    await page
      .getByLabel("Nuevo peso (kg)")
      .fill("68");

    await page
      .getByLabel("Nueva presión sistólica")
      .fill("110");

    const simulationResponsePromise =
      page.waitForResponse(
        (response) =>
          response.url().includes("/api/simulate") &&
          response.request().method() === "POST"
      );

    await page
      .getByRole("button", {
        name: "Simular escenario",
      })
      .click();

    const simulationResponse =
      await simulationResponsePromise;

    expect(
      simulationResponse.status()
    ).toBe(200);

    const body =
      await simulationResponse.json();

    expect(body).toHaveProperty("original");
    expect(body).toHaveProperty("simulated");

    expect(body).toHaveProperty(
      "probability_difference"
    );

    expect(body).toHaveProperty(
      "applied_changes"
    );

    expect(
      body.applied_changes.weight
    ).toBe(68);

    expect(
      body.applied_changes.ap_hi
    ).toBe(110);

    expect(
      body.threshold
    ).toBe(0.38);

    expect(
      body.model_version
    ).toBe("v1");

    await expect(
      page.getByText("Resultado original")
    ).toBeVisible();

    await expect(
      page.getByText("Resultado simulado")
    ).toBeVisible();

    await expect(
      page.getByText(/Diferencia:/)
    ).toBeVisible();

    await expect(
      page.getByText(/Clasificación simulada:/)
    ).toBeVisible();
  }
);


test(
  "PI-07 - bloquea una presión arterial inconsistente antes de enviarla",
  async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("Edad").fill("50");

    await page
      .getByLabel("Altura (cm)")
      .fill("172");

    await page
      .getByLabel("Peso (kg)")
      .fill("72");

    await page
      .getByLabel("Presión sistólica (mmHg)")
      .fill("80");

    await page
      .getByLabel("Presión diastólica (mmHg)")
      .fill("90");

    let analyzeRequestDetected = false;

    page.on("request", (request) => {
      if (
        request.url().includes("/api/analyze") &&
        request.method() === "POST"
      ) {
        analyzeRequestDetected = true;
      }
    });

    await page
      .getByRole("button", {
        name: "Analizar mi perfil",
      })
      .click();

    await expect(
      page.getByText(
        "La presión sistólica debe ser mayor que la presión diastólica."
      )
    ).toBeVisible();

    await page.waitForTimeout(500);

    expect(
      analyzeRequestDetected
    ).toBeFalsy();
  }
);
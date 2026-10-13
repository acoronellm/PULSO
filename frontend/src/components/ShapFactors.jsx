function getReadableFeatureName(feature) {
  const names = {
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

  return names[feature] || feature;
}

function getReadableValue(feature, value) {
  if (feature === "smoke") {
    return value === 1 ? "Sí" : "No";
  }

  if (feature === "alco") {
    return value === 1 ? "Sí" : "No";
  }

  if (feature === "active") {
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
    return Number(value).toFixed(1);
  }

  return value;
}

function ShapFactors({ shap }) {
  if (!shap?.top_factors?.length) {
    return null;
  }

  return (
    <section className="card">
      <h2>Factores que más influyeron en el resultado</h2>

      <p className="section-description">
        Estos factores tuvieron la mayor influencia en la salida generada por
        el modelo para este perfil.
      </p>

      <div className="factor-list">
        {shap.top_factors.map((factor, index) => (
          <article className="factor-item" key={`${factor.feature}-${index}`}>
            <div>
              <h3>{getReadableFeatureName(factor.feature)}</h3>

              <p>
                Valor ingresado:{" "}
                <strong>
                  {getReadableValue(factor.feature, factor.value)}
                </strong>
              </p>
            </div>

            <span
              className={
                factor.direction === "increase"
                  ? "direction increase"
                  : "direction decrease"
              }
            >
              {factor.direction === "increase"
                ? "↑ Aumentó la salida del modelo"
                : "↓ Disminuyó la salida del modelo"}
            </span>
          </article>
        ))}
      </div>

      <div className="info-box">
        La influencia mostrada corresponde al comportamiento matemático del
        modelo y no representa por sí sola una relación causal o un efecto
        clínico.
      </div>
    </section>
  );
}

export default ShapFactors;
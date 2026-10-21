import { useState } from "react";

const initialForm = {
  gender: "1",
  age_years: "",
  height: "",
  weight: "",
  ap_hi: "",
  ap_lo: "",
  smoke: "0",
  alco: "0",
  active: "1",
};

function HealthForm({ onSubmit, loading }) {
  const [form, setForm] = useState(initialForm);
  const [validationError, setValidationError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    setValidationError("");

    const height = Number(form.height);
    const weight = Number(form.weight);
    const apHi = Number(form.ap_hi);
    const apLo = Number(form.ap_lo);

    if (apHi <= apLo) {
      setValidationError(
        "La presión sistólica debe ser mayor que la presión diastólica."
      );
      return;
    }

    const heightMeters = height / 100;
    const bmi = weight / (heightMeters * heightMeters);

    const payload = {
      gender: Number(form.gender),
      height,
      weight,
      ap_hi: apHi,
      ap_lo: apLo,
      smoke: Number(form.smoke),
      alco: Number(form.alco),
      active: Number(form.active),
      age_years: Number(form.age_years),
      bmi: Number(bmi.toFixed(2)),
    };

    onSubmit(payload);
  }

  return (
    <section className="card">
      <h2>Conoce tu perfil cardiovascular</h2>

      <p className="section-description">
        Ingresa la información solicitada para obtener una estimación educativa
        generada por PULSO.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Sexo
            <select
              name="gender"
              value={form.gender}
              onChange={handleChange}
            >
              <option value="1">Mujer</option>
              <option value="2">Hombre</option>
            </select>
          </label>

          <label>
            Edad
            <input
              type="number"
              name="age_years"
              value={form.age_years}
              onChange={handleChange}
              min="18"
              max="100"
              required
            />
          </label>

          <label>
            Altura (cm)
            <input
              type="number"
              name="height"
              value={form.height}
              onChange={handleChange}
              min="120"
              max="220"
              required
            />
          </label>

          <label>
            Peso (kg)
            <input
              type="number"
              name="weight"
              value={form.weight}
              onChange={handleChange}
              min="30"
              max="200"
              step="0.1"
              required
            />
          </label>

          <label>
            Presión sistólica (mmHg)
            <input
              type="number"
              name="ap_hi"
              value={form.ap_hi}
              onChange={handleChange}
              min="70"
              max="250"
              required
            />
          </label>

          <label>
            Presión diastólica (mmHg)
            <input
              type="number"
              name="ap_lo"
              value={form.ap_lo}
              onChange={handleChange}
              min="40"
              max="150"
              required
            />
          </label>

          <label>
            ¿Fuma?
            <select
              name="smoke"
              value={form.smoke}
              onChange={handleChange}
            >
              <option value="0">No</option>
              <option value="1">Sí</option>
            </select>
          </label>

          <label>
            ¿Consume alcohol?
            <select
              name="alco"
              value={form.alco}
              onChange={handleChange}
            >
              <option value="0">No</option>
              <option value="1">Sí</option>
            </select>
          </label>

          <label>
            ¿Realiza actividad física?
            <select
              name="active"
              value={form.active}
              onChange={handleChange}
            >
              <option value="1">Sí</option>
              <option value="0">No</option>
            </select>
          </label>
        </div>

        {validationError && (
          <p className="error-message">{validationError}</p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "Analizando..." : "Analizar mi perfil"}
        </button>
      </form>
    </section>
  );
}

export default HealthForm;
import { useState } from "react";

import useToast from "../hooks/useToast";
import { EXAMPLE_FORM, calculateBmi } from "../utils/health";

const INPUT =
  "w-full h-12 px-space-md rounded-xl bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm font-title-md font-semibold text-on-surface outline-none hover:border-primary/60 focus:bg-surface-container-lowest focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all text-left [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none";
const SEX_ACTIVE =
  "flex items-center justify-center gap-space-xs rounded-xl font-label-md transition-all font-semibold bg-surface-container text-primary shadow-sm ring-2 ring-primary";
const SEX_INACTIVE =
  "flex items-center justify-center gap-space-xs rounded-xl font-label-md transition-all font-medium bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm text-on-surface-variant hover:border-primary/60 hover:bg-surface-container";
const HABIT_ACTIVE =
  "py-2 rounded-lg font-label-md text-primary font-bold bg-surface-container shadow-sm ring-2 ring-primary transition-all flex items-center justify-center gap-1";
const HABIT_INACTIVE =
  "py-2 rounded-lg font-label-md text-on-surface-variant bg-surface-container-lowest border-[1.5px] border-outline-variant hover:border-primary/60 transition-all flex items-center justify-center gap-1";

const HABITS = [
  { key: "tabaco", icon: "smoking_rooms", title: "Tabaquismo", hint: "¿Fumas actualmente?" },
  { key: "alcohol", icon: "local_bar", title: "Consumo de alcohol", hint: "¿Consumes alcohol habitualmente?" },
  { key: "ejercicio", icon: "directions_run", title: "Actividad física", hint: "¿Realizas actividad física con regularidad?" },
];

function HabitButtons({ habit, value, onChange }) {
  return (
    <div className="grid grid-cols-2 gap-space-xs mt-2">
      <button aria-pressed={value} className={value ? HABIT_ACTIVE : HABIT_INACTIVE} id={`${habit}-si`} onClick={() => onChange(habit, true)} type="button">
        {value && (
          <span className="material-symbols-outlined text-[14px]">
            check
          </span>
        )}
        <span>
          Sí
        </span>
      </button>
      <button aria-pressed={!value} className={!value ? HABIT_ACTIVE : HABIT_INACTIVE} id={`${habit}-no`} onClick={() => onChange(habit, false)} type="button">
        {!value && (
          <span className="material-symbols-outlined text-[14px]">
            check
          </span>
        )}
        <span>
          No
        </span>
      </button>
    </div>
  );
}

function NumberField({ id, name, label, unit, min, max, step, value, onChange, help }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="font-label-md text-on-surface font-medium" htmlFor={id}>
        {label}
      </label>
      <div className="relative">
        <input className={INPUT} id={id} max={max} min={min} name={name} onChange={onChange} required step={step} type="number" value={value} />
        <span className="absolute right-space-md top-1/2 -translate-y-1/2 font-label-md text-on-surface-variant pointer-events-none">
          {unit}
        </span>
      </div>
      {help && (
        <span className="font-label-sm text-on-surface-variant">
          {help}
        </span>
      )}
    </div>
  );
}

function SectionTitle({ number, title, subtitle }) {
  return (
    <div className="flex items-center gap-space-sm">
      <span className="w-8 h-8 rounded-lg bg-surface-container text-primary flex items-center justify-center font-semibold text-label-md">
        {number}
      </span>
      <div>
        <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
          {title}
        </h2>
        {subtitle && (
          <p className="font-label-sm text-on-surface-variant">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

export default function EvaluationPage({ form, onChange, onFillExample, onSubmit, loading, error }) {
  const { toast, toastClasses, showToast } = useToast(3500);
  const [validationError, setValidationError] = useState("");
  const visibleError = validationError || error;

  const estatura = parseFloat(form.estatura);
  const peso = parseFloat(form.peso);
  const bmiValid = estatura > 80 && peso > 20;
  const bmi = bmiValid ? calculateBmi(estatura, peso).toFixed(1) : null;

  function handleInput(event) {
    onChange(event.target.name, event.target.value);
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (Number(form.sistolica) <= Number(form.diastolica)) {
      setValidationError("La presión sistólica debe ser mayor que la diastólica.");
      return;
    }
    setValidationError("");
    showToast("Calculando la estimación del modelo...");
    onSubmit(showToast);
  }

  function fillExample() {
    setValidationError("");
    onFillExample(EXAMPLE_FORM);
    showToast("Se cargó un perfil de ejemplo con datos ficticios.");
  }

  const summary = [
    ["Edad", form.edad ? `${form.edad} años` : "--"],
    ["Sexo", form.sexo === "mujer" ? "Mujer" : "Hombre"],
    ["Estatura / Peso", bmiValid ? `${estatura} cm / ${peso} kg` : "--"],
    ["Presión arterial", form.sistolica && form.diastolica ? `${form.sistolica} / ${form.diastolica} mmHg` : "--"],
    ["IMC", bmi ? `${bmi} kg/m²` : "--"],
  ];

  return (
    <main className="w-full pt-24 bg-surface min-h-[calc(100vh-140px)]">
      <div className="w-full max-w-7xl mx-auto px-margin-mobile md:px-margin pb-space-xl">
        <div className="pt-space-md pb-space-lg flex flex-col md:flex-row md:items-end justify-between gap-space-md">
          <div>
            <div className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded-full bg-surface-container text-primary font-label-sm mb-space-xs">
              <span className="material-symbols-outlined text-[16px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                ecg_heart
              </span>
              <span>
                Evaluación educativa · 10 variables del modelo
              </span>
            </div>
            <h1 className="font-display-hero text-headline-lg-mobile md:text-headline-lg font-bold text-on-surface tracking-tight">
              Completa tu evaluación
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mt-1">
              Ingresa tus datos para obtener la estimación del modelo PULSO v1, los factores que más influyeron y recomendaciones educativas.
            </p>
          </div>
          <button className="flex items-center gap-space-sm bg-surface-container-lowest px-space-md py-space-sm rounded-xl shadow-sm border border-outline-variant/20 shrink-0 hover:border-primary/40 transition-colors text-left" onClick={fillExample} type="button">
            <div className="w-9 h-9 rounded-full bg-surface-container flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[20px]">
                science
              </span>
            </div>
            <div>
              <div className="font-label-sm text-on-surface font-semibold">
                Usar datos de ejemplo
              </div>
              <div className="font-label-sm text-[11px] text-on-surface-variant">
                Perfil ficticio para probar la herramienta
              </div>
            </div>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
          <div className="lg:col-span-8 flex flex-col gap-space-lg">
            <form className="bg-surface-container-lowest rounded-xl shadow-md p-space-lg md:p-space-xl flex flex-col gap-space-xl" id="evaluationForm" onSubmit={handleSubmit}>
              <section className="flex flex-col gap-space-md">
                <SectionTitle number="01" title="Datos personales" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                  <NumberField help="Edad en años cumplidos" id="inputEdad" label="Edad actual" max="110" min="18" name="edad" onChange={handleInput} unit="años" value={form.edad} />
                  <div className="flex flex-col gap-1.5">
                    <span className="font-label-md text-on-surface font-medium">
                      Sexo
                    </span>
                    <div className="grid grid-cols-2 gap-space-sm h-12">
                      <button aria-pressed={form.sexo === "mujer"} className={form.sexo === "mujer" ? SEX_ACTIVE : SEX_INACTIVE} onClick={() => onChange("sexo", "mujer")} type="button">
                        <span className="material-symbols-outlined text-[18px]">
                          female
                        </span>
                        <span>
                          Mujer
                        </span>
                      </button>
                      <button aria-pressed={form.sexo === "hombre"} className={form.sexo === "hombre" ? SEX_ACTIVE : SEX_INACTIVE} onClick={() => onChange("sexo", "hombre")} type="button">
                        <span className="material-symbols-outlined text-[18px]">
                          male
                        </span>
                        <span>
                          Hombre
                        </span>
                      </button>
                    </div>
                    <span className="font-label-sm text-on-surface-variant">
                      Variable utilizada por el modelo
                    </span>
                  </div>
                </div>
              </section>

              <div className="w-full h-px bg-surface-container"></div>

              <section className="flex flex-col gap-space-md">
                <SectionTitle number="02" subtitle="El IMC se calcula automáticamente con tu estatura y peso" title="Medidas físicas" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                  <NumberField id="inputEstatura" label="Estatura" max="220" min="120" name="estatura" onChange={handleInput} unit="cm" value={form.estatura} />
                  <NumberField id="inputPeso" label="Peso" max="200" min="30" name="peso" onChange={handleInput} step="0.1" unit="kg" value={form.peso} />
                </div>
                <div className="bg-surface-container-low rounded-xl p-space-md flex items-start gap-space-sm">
                  <div className="w-12 h-12 rounded-xl bg-surface-container-lowest flex items-center justify-center text-primary shadow-sm shrink-0">
                    <span className="material-symbols-outlined text-[26px]">
                      monitor_weight
                    </span>
                  </div>
                  <div>
                    <div className="font-label-sm text-on-surface-variant font-medium">
                      Índice de Masa Corporal (IMC) calculado
                    </div>
                    <div className="flex items-baseline gap-space-xs mt-0.5">
                      <span className="font-metric-numeral text-headline-lg font-bold text-on-surface tracking-tight" id="bmiValue">
                        {bmi ?? "--"}
                      </span>
                      <span className="font-label-md text-on-surface-variant">
                        kg/m²
                      </span>
                    </div>
                  </div>
                </div>
              </section>

              <div className="w-full h-px bg-surface-container"></div>

              <section className="flex flex-col gap-space-md">
                <SectionTitle number="03" subtitle="Valores de tu última medición en mmHg" title="Presión arterial y hábitos" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                  <NumberField help="El valor superior de la medición" id="inputSys" label="Presión sistólica (máxima)" max="250" min="70" name="sistolica" onChange={handleInput} unit="mmHg" value={form.sistolica} />
                  <NumberField help="El valor inferior de la medición" id="inputDia" label="Presión diastólica (mínima)" max="150" min="40" name="diastolica" onChange={handleInput} unit="mmHg" value={form.diastolica} />
                </div>
                <div className="flex flex-col gap-space-md pt-space-xs">
                  <div className="font-title-md text-body-lg font-semibold text-on-surface">
                    Hábitos
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
                    {HABITS.map((habit) => (
                      <div className="p-space-md rounded-xl bg-surface-container-low flex flex-col justify-between gap-space-sm" key={habit.key}>
                        <div className="flex items-center gap-space-sm">
                          <div className="w-8 h-8 rounded-lg bg-surface-container-lowest flex items-center justify-center text-primary shadow-sm shrink-0">
                            <span className="material-symbols-outlined text-[18px]">
                              {habit.icon}
                            </span>
                          </div>
                          <div>
                            <div className="font-label-md font-semibold text-on-surface">
                              {habit.title}
                            </div>
                            <div className="font-label-sm text-on-surface-variant text-[11px]">
                              {habit.hint}
                            </div>
                          </div>
                        </div>
                        <HabitButtons habit={habit.key} onChange={onChange} value={form[habit.key]} />
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              <div className="bg-surface-container-low rounded-xl p-space-md flex items-start gap-space-md">
                <div className="w-8 h-8 rounded-full bg-secondary-fixed flex items-center justify-center text-secondary shrink-0 mt-0.5">
                  <span className="material-symbols-outlined text-[18px]">
                    info
                  </span>
                </div>
                <div className="text-on-surface-variant font-label-md leading-relaxed">
                  <strong className="font-semibold text-on-surface block mb-0.5">
                    ¿Qué datos usa el modelo?
                  </strong>
                  PULSO v1 usa solo estas variables: edad, sexo, estatura, peso, IMC, presión arterial, tabaquismo, alcohol y actividad física. No incluye colesterol, glucosa ni otros exámenes clínicos.
                </div>
              </div>

              {visibleError && (
                <div className="bg-error-container text-on-error-container rounded-xl p-space-md flex items-start gap-space-sm" role="alert">
                  <span className="material-symbols-outlined text-[20px] shrink-0">
                    error
                  </span>
                  <div className="font-label-md">
                    <strong className="font-semibold block">
                      No pudimos calcular tu resultado
                    </strong>
                    {visibleError}
                  </div>
                </div>
              )}

              <div className="pt-space-md flex justify-end">
                <button className="px-space-lg h-12 rounded-xl bg-primary-container hover:bg-primary text-on-primary transition-all duration-200 font-label-md font-bold flex items-center justify-center gap-space-sm shadow-md hover:shadow-xl hover:shadow-primary/20 shrink-0 w-full sm:w-auto group disabled:opacity-70" disabled={loading} type="submit">
                  <span className="material-symbols-outlined text-[20px] text-on-primary group-hover:scale-110 transition-transform" style={{ fontVariationSettings: "'FILL' 1" }}>
                    favorite
                  </span>
                  <span>
                    {loading ? "Calculando..." : "Ver mi resultado"}
                  </span>
                  <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>
              </div>
            </form>
          </div>

          <div className="lg:col-span-4 flex flex-col gap-space-md">
            <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-md flex flex-col gap-space-md">
              <div className="flex items-center gap-space-sm">
                <div className="w-10 h-10 rounded-xl bg-primary-fixed flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[20px]">
                    fact_check
                  </span>
                </div>
                <div className="font-title-md text-on-surface font-semibold">
                  Resumen de tus datos
                </div>
              </div>
              <div className="bg-surface-container-low rounded-xl p-space-sm flex flex-col gap-space-xs text-on-surface-variant font-label-sm">
                {summary.map(([label, value]) => (
                  <div className="flex justify-between py-1 px-1" key={label}>
                    <span>
                      {label}:
                    </span>
                    <span className="font-semibold text-on-surface">
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-md flex flex-col gap-space-sm">
              <div className="flex items-center gap-space-sm">
                <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[18px]">
                    tips_and_updates
                  </span>
                </div>
                <h3 className="font-label-md font-semibold text-on-surface">
                  ¿Cómo medir tu presión correctamente?
                </h3>
              </div>
              <ul className="flex flex-col gap-space-xs font-label-sm text-on-surface-variant mt-1">
                {[
                  "Reposa 5 minutos sentado antes del registro.",
                  "No tomes café ni fumes en los 30 minutos previos.",
                  "Apoya el brazo a la altura de tu corazón.",
                ].map((tip) => (
                  <li className="flex items-start gap-space-xs" key={tip}>
                    <span className="material-symbols-outlined text-[14px] text-secondary mt-0.5">
                      check_circle
                    </span>
                    <span>
                      {tip}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm relative overflow-hidden">
              <div className="relative z-10 flex flex-col gap-space-xs">
                <span className="font-label-sm uppercase font-semibold tracking-wider text-secondary">
                  Sobre el modelo
                </span>
                <div className="font-title-md text-on-surface font-semibold">
                  PULSO v1 · XGBoost
                </div>
                <p className="font-label-sm text-on-surface-variant">
                  Estima la probabilidad de pertenecer a la clase cardio = 1 del conjunto de datos de entrenamiento. Es una herramienta educativa, no un diagnóstico.
                </p>
              </div>
              <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-surface-container rounded-full opacity-60 pointer-events-none"></div>
            </div>
          </div>
        </div>

        <div className={`fixed bottom-6 right-6 bg-inverse-surface text-inverse-on-surface px-space-md py-space-sm rounded-xl shadow-xl flex items-center gap-space-sm transition-all duration-300 ${toastClasses} z-50`} role="status">
          <span className="material-symbols-outlined text-[20px] text-secondary-fixed">
            check_circle
          </span>
          <span className="font-label-md font-medium">
            {toast.message}
          </span>
        </div>
      </div>
    </main>
  );
}

import { useCallback, useState } from "react";

import InfoModal from "../components/InfoModal";
import { simulateScenario } from "../services/api";
import {
  calculateBmi,
  formatProbability,
  formatThreshold,
  genderLabel,
} from "../utils/health";
import { IMAGES } from "../utils/images";

// Consejos educativos generales: no forman parte del cálculo de XGBoost
const MICRO_HABITS = [
  {
    short: "Menos sal, más sabor",
    tagline: "Hierbas, limón y especias",
    title: "Cocinar con menos sal",
    category: "Alimentación",
    icon: "eco",
    image: IMAGES.food,
    bar: "bg-primary-container",
    tile: "bg-primary-fixed text-primary",
    accent: "text-primary",
    detail: "Sustituir la sal añadida por limón, orégano, ajo u otras especias es un consejo frecuente en las guías de alimentación saludable. El consumo de sal no es una variable del modelo PULSO, por lo que no cambia la simulación.",
    benefit: "Consejo educativo general · no modifica el cálculo del modelo",
    benefitIcon: "school",
  },
  {
    short: "Pausas activas",
    tagline: "Levantarte y moverte durante el día",
    title: "Pausas activas durante el día",
    category: "Movimiento",
    icon: "timer",
    image: IMAGES.walking,
    bar: "bg-primary-container",
    tile: "bg-primary-fixed text-primary",
    accent: "text-primary",
    detail: "Interrumpir los periodos largos sentado con caminatas cortas es una recomendación habitual para mantenerse activo. Consulta a tu equipo de salud antes de iniciar actividad física intensa.",
    benefit: "Consejo educativo general · consulta a un profesional",
    benefitIcon: "school",
  },
  {
    short: "Descanso reparador",
    tagline: "Dormir de 7 a 8 horas",
    title: "Descanso reparador",
    category: "Descanso",
    icon: "bedtime",
    image: null,
    bar: "bg-primary-container",
    tile: "bg-primary-fixed text-primary",
    accent: "text-primary",
    detail: "Mantener horarios de sueño regulares forma parte de los hábitos de vida saludables que suelen recomendarse. El sueño no es una variable del modelo PULSO.",
    benefit: "Consejo educativo general · no modifica el cálculo del modelo",
    benefitIcon: "school",
  },
];

const HABIT_TOGGLES = [
  { key: "active", icon: "directions_run", title: "Actividad física regular", hint: "Variable del modelo: actividad física (sí/no)" },
  { key: "smoke", icon: "smoking_rooms", title: "Tabaquismo", hint: "Variable del modelo: fuma (sí/no)" },
  { key: "alco", icon: "local_bar", title: "Consumo de alcohol", hint: "Variable del modelo: consume alcohol (sí/no)" },
];

function differenceText(points) {
  if (points < 0) {
    return `En este escenario hipotético la probabilidad estimada por el modelo disminuye ${Math.abs(points).toFixed(1)} puntos porcentuales.`;
  }
  if (points > 0) {
    return `En este escenario hipotético la probabilidad estimada por el modelo aumenta ${points.toFixed(1)} puntos porcentuales.`;
  }
  return "En este escenario hipotético la probabilidad estimada por el modelo no cambia.";
}

function EmptyState({ onNavigate }) {
  return (
    <main className="w-full pt-24 bg-surface min-h-[calc(100vh-140px)]">
      <div className="w-full px-margin-mobile md:px-margin max-w-3xl mx-auto py-space-xl">
        <div className="bg-surface-card rounded-xl shadow-sm p-space-lg flex flex-col items-center text-center gap-space-md">
          <div className="w-14 h-14 rounded-full bg-primary-fixed flex items-center justify-center text-primary">
            <span className="material-symbols-outlined text-[28px]">
              tune
            </span>
          </div>
          <h1 className="font-headline-md text-headline-md text-text-primary">
            Simulación de escenarios con PULSO v1
          </h1>
          <p className="font-body-lg text-body-lg text-text-secondary">
            Para simular escenarios primero necesitas calcular tu resultado. La simulación parte de los datos que ingreses en la evaluación.
          </p>
          <button className="px-5 py-2.5 rounded-xl bg-primary-container text-on-primary font-label-md font-semibold hover:bg-primary transition-colors flex items-center gap-1.5" onClick={() => onNavigate("evaluacion")} type="button">
            <span className="material-symbols-outlined text-[18px]">
              arrow_back
            </span>
            Ir a la evaluación
          </button>
        </div>
      </div>
    </main>
  );
}

const HEART_PATH =
  "M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z";

// Colores y latido de las tarjetas de Stitch: azul para el original, menta para el escenario
function ProbabilityCard({ label, probability, classification, highlight }) {
  return (
    <div className={`md:col-span-5 rounded-xl p-space-md flex flex-col items-center text-center space-y-space-sm relative overflow-hidden ${highlight ? "bg-gradient-to-b from-mint-vitality-subtle/70 to-surface-card shadow-sm" : "bg-surface-container-low"}`}>
      {highlight && (
        <div className="absolute -right-6 -top-6 w-24 h-24 rounded-full bg-secondary-container/40 blur-xl"></div>
      )}
      <div className={`absolute top-2 left-2 px-2 py-0.5 rounded font-label-sm ${highlight ? "bg-mint-vitality text-on-secondary font-semibold" : "bg-surface-card text-text-secondary"}`}>
        {label}
      </div>
      {highlight ? (
        <div className="w-28 h-28 rounded-full bg-secondary-container/30 flex items-center justify-center relative mt-3 shadow-inner">
          <div className="absolute inset-0 rounded-full bg-mint-vitality/20 animate-ping opacity-75"></div>
          <div className="w-24 h-24 rounded-full bg-mint-vitality-subtle flex items-center justify-center relative z-10">
            <svg aria-hidden="true" className="w-14 h-14 text-mint-vitality animate-pulse" fill="currentColor" viewBox="0 0 24 24">
              <path d={HEART_PATH}></path>
            </svg>
          </div>
        </div>
      ) : (
        <div className="w-28 h-28 rounded-full bg-primary-fixed/40 flex items-center justify-center relative mt-3">
          <div className="w-24 h-24 rounded-full bg-indigo-metric-subtle flex items-center justify-center">
            <svg aria-hidden="true" className="w-14 h-14 text-primary animate-pulse" fill="currentColor" viewBox="0 0 24 24">
              <path d={HEART_PATH}></path>
            </svg>
          </div>
        </div>
      )}
      <div>
        <span className={`font-metric-display text-metric-display block font-bold ${highlight ? "text-secondary" : "text-text-primary"}`}>
          {probability === null ? "-- %" : `${formatProbability(probability)} %`}
        </span>
        <span className={`font-label-md ${highlight ? "text-secondary font-semibold" : "text-text-secondary"}`}>
          {classification === null ? "Pendiente de calcular" : `Clase ${classification} asignada`}
        </span>
      </div>
    </div>
  );
}

// Barras con la paleta original de Stitch (azul, verde azulado y menta)
function ProbabilityBars({ original, simulated, threshold }) {
  const rows = [
    { label: "Perfil original", value: original, fill: "bg-primary-container" },
    { label: "Escenario simulado", value: simulated, fill: "bg-gradient-to-r from-secondary to-mint-vitality" },
  ];

  return (
    <div className="pt-space-xs space-y-space-sm">
      <div className="flex justify-between items-center text-text-secondary font-label-sm">
        <span>
          Escala de probabilidad del modelo
        </span>
        <span className="text-secondary font-semibold">
          {`Umbral ${formatThreshold(threshold)} %`}
        </span>
      </div>
      {rows.map(({ label, value, fill }) => (
        <div className="space-y-1" key={label}>
          <div className="flex justify-between font-label-sm text-text-muted">
            <span>
              {label}
            </span>
            <span className="text-text-primary font-semibold">
              {value === null ? "--" : `${formatProbability(value)} %`}
            </span>
          </div>
          <div className="relative w-full h-3 bg-surface-container rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-500 ${fill}`} style={{ width: `${(value ?? 0) * 100}%` }}></div>
            <div className="absolute top-0 bottom-0 w-0.5 bg-text-primary/60" style={{ left: `${threshold * 100}%` }}></div>
          </div>
        </div>
      ))}
      <div className="flex justify-between text-[10px] text-text-muted">
        <span>
          0 %
        </span>
        <span>
          La línea marca el umbral de clasificación
        </span>
        <span>
          100 %
        </span>
      </div>
    </div>
  );
}

export default function SimulationPage({ analysis, profile, onNavigate }) {
  const [scenario, setScenario] = useState(() => (profile
    ? {
        ap_hi: profile.ap_hi,
        ap_lo: profile.ap_lo,
        weight: profile.weight,
        active: profile.active,
        smoke: profile.smoke,
        alco: profile.alco,
      }
    : null));
  const [result, setResult] = useState(null);
  const [projecting, setProjecting] = useState(false);
  const [projectionError, setProjectionError] = useState("");
  const [openHabit, setOpenHabit] = useState(null);
  const closeHabit = useCallback(() => setOpenHabit(null), []);

  if (!analysis || !profile) {
    return <EmptyState onNavigate={onNavigate} />;
  }

  const ranges = {
    ap_hi: [Math.min(90, profile.ap_hi), Math.max(200, profile.ap_hi)],
    ap_lo: [Math.min(50, profile.ap_lo), Math.max(130, profile.ap_lo)],
    weight: [
      Math.max(30, Math.min(40, Math.floor(profile.weight))),
      Math.min(200, Math.max(150, Math.ceil(profile.weight))),
    ],
  };
  const bmi = calculateBmi(profile.height, scenario.weight).toFixed(1);
  const threshold = formatThreshold(result?.threshold ?? analysis.prediction.threshold);

  function update(name, value) {
    setScenario((previous) => ({ ...previous, [name]: value }));
    setResult(null);
    setProjectionError("");
  }

  function resetDefaults() {
    setScenario({
      ap_hi: profile.ap_hi,
      ap_lo: profile.ap_lo,
      weight: profile.weight,
      active: profile.active,
      smoke: profile.smoke,
      alco: profile.alco,
    });
    setResult(null);
    setProjectionError("");
  }

  async function handleProject() {
    if (scenario.ap_hi <= scenario.ap_lo) {
      setProjectionError("La presión sistólica debe ser mayor que la diastólica.");
      return;
    }

    try {
      setProjecting(true);
      setProjectionError("");
      const response = await simulateScenario({ original: profile, changes: scenario });
      setResult(response);
    } catch (error) {
      setProjectionError(error.message);
    } finally {
      setProjecting(false);
    }
  }

  const sliders = [
    { key: "ap_hi", icon: "speed", label: "Presión sistólica", unit: "mmHg", step: 1 },
    { key: "ap_lo", icon: "compress", label: "Presión diastólica", unit: "mmHg", step: 1 },
    { key: "weight", icon: "scale", label: "Peso", unit: "kg", step: 0.1 },
  ];

  return (
    <main className="w-full pt-24 bg-surface min-h-[calc(100vh-140px)]">
      <div className="w-full px-margin-mobile md:px-margin max-w-7xl mx-auto py-space-md space-y-space-lg">
        <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-surface-card via-surface-container-low to-surface-card p-space-md md:p-space-lg shadow-sm">
          <div className="absolute -left-8 -bottom-8 w-44 h-44 rounded-full bg-primary-fixed/30 blur-2xl pointer-events-none"></div>
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-space-md">
            <div className="space-y-space-xs max-w-2xl">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-metric-subtle text-indigo-metric font-label-sm">
                <span className="material-symbols-outlined text-[14px]">
                  tune
                </span>
                Escenario hipotético
              </span>
              <h1 className="font-headline-lg text-headline-lg text-text-primary tracking-tight">
                Simulación de escenarios con PULSO v1
              </h1>
              <p className="font-body-md text-text-secondary flex items-start gap-1.5">
                <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
                  info
                </span>
                <span>
                  Explora cómo cambia la salida del modelo XGBoost al modificar algunas características de tu perfil. No predice los efectos médicos reales de una intervención.
                </span>
              </p>
            </div>
            <div className="flex items-center gap-space-sm bg-surface-card px-space-md py-space-sm rounded-xl shadow-sm self-start md:self-auto shrink-0">
              <div className="w-9 h-9 rounded-full bg-surface-container-high flex items-center justify-center text-text-secondary">
                <span className="material-symbols-outlined text-[20px]">
                  {profile.gender === 1 ? "female" : "male"}
                </span>
              </div>
              <div className="flex flex-col">
                <span className="font-label-sm text-text-muted">
                  Perfil evaluado
                </span>
                <span className="font-title-md text-title-md text-text-primary">
                  {`${genderLabel(profile.gender)} · ${profile.age_years} años`}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
          <div className="lg:col-span-5 flex flex-col gap-space-md">
            <div className="bg-surface-card rounded-xl p-space-md md:p-space-lg shadow-sm space-y-space-md">
              <div className="flex items-center justify-between pb-space-xs">
                <div className="flex items-center gap-space-xs">
                  <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center text-primary">
                    <span className="material-symbols-outlined text-[18px]">
                      tune
                    </span>
                  </div>
                  <h2 className="font-title-md text-title-md text-text-primary">
                    Ajustes del escenario
                  </h2>
                </div>
                <button className="text-text-muted hover:text-text-primary font-label-sm flex items-center gap-1 transition-colors" onClick={resetDefaults} type="button">
                  <span className="material-symbols-outlined text-[15px]">
                    restart_alt
                  </span>
                  Restablecer
                </button>
              </div>

              <div className="space-y-space-md pt-space-xs">
                {sliders.map(({ key, icon, label, unit, step }) => (
                  <div className="space-y-space-xs bg-surface-container-low/70 p-space-sm rounded-xl" key={key}>
                    <div className="flex justify-between items-center">
                      <label className="font-label-md text-text-primary flex items-center gap-1.5" htmlFor={`slider-${key}`}>
                        <span className="material-symbols-outlined text-primary text-[18px]">
                          {icon}
                        </span>
                        {label}
                      </label>
                      <div className="flex items-center gap-space-xs">
                        <span className="font-title-md text-title-md text-text-primary font-bold">
                          {key === "weight" ? Number(scenario.weight).toFixed(1) : scenario[key]}{" "}
                          <span className="font-label-sm text-text-muted">
                            {unit}
                          </span>
                        </span>
                        {key === "weight" && (
                          <span className="px-2 py-0.5 rounded-full bg-surface-container text-primary font-label-sm font-semibold">
                            {`IMC ${bmi}`}
                          </span>
                        )}
                      </div>
                    </div>
                    <input className="w-full accent-primary-container cursor-pointer h-2 bg-surface-variant rounded-lg appearance-none" id={`slider-${key}`} max={ranges[key][1]} min={ranges[key][0]} onChange={(event) => update(key, Number(event.target.value))} step={step} type="range" value={scenario[key]} />
                    <div className="flex justify-between font-label-sm text-text-muted px-0.5">
                      <span>
                        {`${ranges[key][0]} ${unit}`}
                      </span>
                      <span>
                        {`Original: ${profile[key]} ${unit}`}
                      </span>
                      <span>
                        {`${ranges[key][1]} ${unit}`}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-space-xs space-y-space-sm">
                <span className="font-label-sm uppercase tracking-wider text-text-muted block">
                  Hábitos incluidos en el modelo
                </span>
                {HABIT_TOGGLES.map(({ key, icon, title, hint }) => (
                  <div className="flex items-center justify-between p-space-sm bg-surface-container-low/70 rounded-xl" key={key}>
                    <div className="flex items-center gap-space-sm">
                      <div className="w-9 h-9 rounded-full bg-primary-fixed flex items-center justify-center text-primary">
                        <span className="material-symbols-outlined text-[20px]">
                          {icon}
                        </span>
                      </div>
                      <div>
                        <p className="font-label-md text-text-primary font-semibold">
                          {title}
                        </p>
                        <p className="font-label-sm text-text-secondary">
                          {hint}
                        </p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <span className="sr-only">
                        {title}
                      </span>
                      <input checked={scenario[key] === 1} className="sr-only peer" onChange={(event) => update(key, event.target.checked ? 1 : 0)} type="checkbox" />
                      <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container"></div>
                    </label>
                  </div>
                ))}
              </div>

              <div className="pt-space-xs">
                <button className="w-full py-3 px-4 bg-primary-container text-on-primary rounded-xl font-label-md font-semibold flex items-center justify-center gap-2 shadow-sm hover:brightness-105 active:scale-[0.98] transition-all disabled:opacity-70" disabled={projecting} onClick={handleProject} type="button">
                  <span className="material-symbols-outlined text-[18px]">
                    auto_graph
                  </span>
                  {projecting ? "Calculando escenario..." : "Calcular escenario"}
                </button>
              </div>
            </div>

            <div className="bg-surface-card p-space-md rounded-xl flex items-start gap-space-sm shadow-sm">
              <span className="material-symbols-outlined text-primary text-[22px] shrink-0">
                restaurant
              </span>
              <p className="font-body-md text-text-secondary">
                El consumo de sal, el sueño y otros hábitos no son variables del modelo, por eso no aparecen en los ajustes. Puedes consultarlos como consejos educativos más abajo.
              </p>
            </div>
          </div>

          <div className="lg:col-span-7 flex flex-col gap-space-md">
            <div className="bg-surface-card rounded-xl p-space-md md:p-space-lg shadow-sm space-y-space-lg">
              <div className="flex items-center justify-between gap-space-sm">
                <div className="space-y-0.5">
                  <span className="font-label-sm uppercase tracking-wider text-text-muted">
                    Salida del modelo
                  </span>
                  <h2 className="font-headline-md text-headline-md text-text-primary">
                    Comparación de probabilidades
                  </h2>
                </div>
                <span className="px-3 py-1 rounded-full bg-surface-container text-primary font-label-sm font-semibold whitespace-nowrap">
                  {`PULSO ${result?.model_version ?? analysis.prediction.model_version} · XGBoost`}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-11 gap-space-md items-center">
                <ProbabilityCard
                  classification={result ? result.original.classification : analysis.prediction.classification}
                  label="Perfil original"
                  probability={result ? result.original.probability : analysis.prediction.probability}
                />
                <div className="md:col-span-1 flex flex-col items-center justify-center py-2 md:py-0 gap-1">
                  <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary shadow-md transform md:rotate-0 rotate-90">
                    <span className="material-symbols-outlined text-[20px]">
                      arrow_forward
                    </span>
                  </div>
                  <span className="font-label-sm text-primary font-bold whitespace-nowrap" data-testid="simulation-difference">
                    {result ? `${result.probability_difference > 0 ? "+" : ""}${(result.probability_difference * 100).toFixed(1)} pp` : "--"}
                  </span>
                </div>
                <ProbabilityCard
                  classification={result ? result.simulated.classification : null}
                  highlight
                  label="Escenario simulado"
                  probability={result ? result.simulated.probability : null}
                />
              </div>

              <div className="bg-surface-container-low p-space-md rounded-xl flex items-start gap-space-md">
                <div className="w-10 h-10 rounded-full bg-primary-fixed flex items-center justify-center text-primary shrink-0">
                  <span className="material-symbols-outlined text-[22px]">
                    insights
                  </span>
                </div>
                <div className="space-y-1">
                  <p className={projectionError ? "font-body-md text-error" : "font-body-md text-text-primary"} data-testid="simulation-description" role={projectionError ? "alert" : undefined}>
                    {projectionError || (result
                      ? differenceText(result.probability_difference * 100)
                      : "Ajusta los valores y pulsa «Calcular escenario» para obtener la salida del modelo con el servicio ML.")}
                  </p>
                  <p className="font-label-sm text-text-secondary">
                    {`Umbral de clasificación del modelo: ${threshold} %. Los cambios en la probabilidad son variaciones de la salida de XGBoost, no efectos clínicos garantizados.`}
                  </p>
                </div>
              </div>

              <ProbabilityBars
                original={result ? result.original.probability : analysis.prediction.probability}
                simulated={result ? result.simulated.probability : null}
                threshold={result?.threshold ?? analysis.prediction.threshold}
              />
            </div>

            <div className="bg-surface-card rounded-xl p-space-md shadow-sm flex flex-col sm:flex-row items-center justify-between gap-space-md">
              <div className="flex items-center gap-space-sm w-full sm:w-auto">
                <div className="w-10 h-10 rounded-full bg-primary-fixed flex items-center justify-center text-primary shrink-0">
                  <span className="material-symbols-outlined text-[20px]">
                    verified_user
                  </span>
                </div>
                <p className="font-label-sm text-text-secondary">
                  Esta simulación es una herramienta educativa. Antes de cambiar tratamientos o hábitos importantes, consulta a un profesional de la salud.
                </p>
              </div>
              <button className="whitespace-nowrap px-4 py-2.5 rounded-xl bg-surface-container text-text-secondary hover:bg-surface-container-high font-label-md transition-colors" onClick={() => onNavigate("resultado")} type="button">
                Volver al resultado
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-space-md pt-space-xs">
          <div>
            <span className="font-label-sm uppercase tracking-wider text-secondary font-semibold">
              Consejos educativos
            </span>
            <h2 className="font-headline-md text-headline-md text-text-primary">
              Hábitos que suman
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
            {MICRO_HABITS.map((habit) => (
              <button className="bg-surface-card rounded-xl p-space-md shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all flex items-center gap-space-sm relative overflow-hidden text-left group" key={habit.title} onClick={() => setOpenHabit(habit)} type="button">
                <div className={`absolute top-0 left-0 bottom-0 w-1.5 ${habit.bar}`}></div>
                <span className={`w-11 h-11 rounded-full flex items-center justify-center shrink-0 ml-1 ${habit.tile}`}>
                  <span className="material-symbols-outlined text-[22px]">
                    {habit.icon}
                  </span>
                </span>
                <div className="flex-1 min-w-0">
                  <p className="font-title-md text-title-md text-text-primary font-semibold">
                    {habit.short}
                  </p>
                  <p className="font-label-sm text-text-secondary">
                    {habit.tagline}
                  </p>
                </div>
                <span className="material-symbols-outlined text-text-muted group-hover:text-primary group-hover:translate-x-0.5 transition-all">
                  chevron_right
                </span>
              </button>
            ))}
          </div>
        </div>
        <InfoModal item={openHabit} onClose={closeHabit} />
      </div>
    </main>
  );
}

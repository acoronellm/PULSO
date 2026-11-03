import { useCallback, useState } from "react";

import InfoModal from "../components/InfoModal";
import useToast from "../hooks/useToast";
import { simulateScenario } from "../services/api";
import { DEMO_PERCENT, toPercent } from "../utils/health";
import { IMAGES } from "../utils/images";

const MICRO_HABITS = [
  {
    short: "Menos sal, más sabor",
    tagline: "Potasio y hierbas frescas",
    title: "El poder del potasio y hierbas frescas",
    category: "Nutrición celular",
    icon: "eco",
    image: IMAGES.food,
    bar: "bg-primary-container",
    tile: "bg-primary-fixed text-primary",
    accent: "text-primary",
    detail: "Sustituye la sal añadida por limón, orégano y ajo deshidratado. El potasio de las hojas verdes ayuda a reducir la retención de líquidos.",
    benefit: "Puede bajar 4-6 mmHg en unas 4 semanas",
    benefitIcon: "verified",
  },
  {
    short: "Pausas activas",
    tagline: "10 minutos cada 2 horas",
    title: "Pausas activas de 10 minutos",
    category: "Flujo vascular",
    icon: "timer",
    image: IMAGES.walking,
    bar: "bg-primary-container",
    tile: "bg-primary-fixed text-primary",
    accent: "text-primary",
    detail: "Levantarte y caminar un poco cada dos horas rompe el sedentarismo y favorece que tus arterias se relajen de forma natural.",
    benefit: "Previene la rigidez arterial durante el día",
    benefitIcon: "schedule",
  },
  {
    short: "Descanso reparador",
    tagline: "Dormir 7 a 8 horas",
    title: "Descanso reparador (7 - 8 horas)",
    category: "Reparación",
    icon: "bedtime",
    image: null,
    bar: "bg-primary-container",
    tile: "bg-primary-fixed text-primary",
    accent: "text-primary",
    detail: "Durante el sueño la presión baja de forma natural. Dormir bien ayuda a tu cuerpo a recuperarse y a empezar el día con un ritmo más estable.",
    benefit: "Ayuda a regular la variabilidad cardíaca",
    benefitIcon: "nights_stay",
  },
];

function bmiBadge(bmi) {
  if (bmi < 25) {
    return {
      className: "px-2 py-0.5 rounded-full bg-mint-vitality-subtle text-secondary font-label-sm font-semibold",
      text: `IMC ${bmi} · Saludable`,
    };
  }
  if (bmi < 30) {
    return {
      className: "px-2 py-0.5 rounded-full bg-amber-warning-subtle text-amber-warning font-label-sm font-semibold",
      text: `IMC ${bmi} · Sobrepeso`,
    };
  }
  return {
    className: "px-2 py-0.5 rounded-full bg-coral-alert-subtle text-coral-alert font-label-sm font-semibold",
    text: `IMC ${bmi} · Elevado`,
  };
}

// Fórmula ilustrativa del prototipo de Stitch (solo modo demo)
function demoProjection({ sys, dia, exercise, salt, smokeFree }, bmi) {
  let risk = DEMO_PERCENT;
  risk += (sys - 142) * 0.25;
  risk += (dia - 88) * 0.15;
  if (bmi < 25) risk -= 2.0;
  else if (bmi >= 30) risk += 2.5;
  if (exercise) risk -= 3.5;
  if (salt) risk -= 2.0;
  if (smokeFree) risk -= 2.5;
  return Math.max(12, Math.min(42, Math.round(risk)));
}

function deltaView(delta, sys, dia) {
  if (delta === null) {
    return {
      badgeClass: "font-label-md font-bold px-2 py-0.5 rounded-full bg-surface-container text-text-secondary",
      badgeText: "Escenario pendiente",
      smText: "--",
      smClass: "font-label-sm text-text-secondary font-bold whitespace-nowrap",
      description: "Ajusta los valores y pulsa «Proyectar resultados» para calcular el escenario con el modelo PULSO.",
    };
  }
  if (delta > 0) {
    return {
      badgeClass: "font-label-md font-bold px-2 py-0.5 rounded-full bg-mint-vitality text-on-secondary",
      badgeText: `-${delta}% de reducción estimada`,
      smText: `-${delta}%`,
      smClass: "font-label-sm text-secondary font-bold whitespace-nowrap",
      description: `Al optimizar tu presión a ${sys}/${dia} mmHg y sumar hábitos preventivos, se disipa una carga vascular considerable a largo plazo.`,
    };
  }
  if (delta < 0) {
    return {
      badgeClass: "font-label-md font-bold px-2 py-0.5 rounded-full bg-coral-alert text-on-secondary",
      badgeText: `+${Math.abs(delta)}% riesgo adicional`,
      smText: `+${Math.abs(delta)}%`,
      smClass: "font-label-sm text-coral-alert font-bold whitespace-nowrap",
      description: `Un valor tensional sostenido en ${sys}/${dia} mmHg incrementa el desgaste arterial. Pequeños pasos pueden revertir este avance.`,
    };
  }
  return {
    badgeClass: "font-label-md font-bold px-2 py-0.5 rounded-full bg-surface-container text-text-secondary",
    badgeText: "0% variación neta",
    smText: "0%",
    smClass: "font-label-sm text-text-secondary font-bold whitespace-nowrap",
    description: "Este escenario equivale a tu perfil actual sin cambios estadísticos proyectados.",
  };
}

export default function SimulationPage({ analysis, profile, onNavigate }) {
  const isDemo = !analysis;
  const heightM = isDemo ? 1.65 : profile.height / 100;
  const defaults = isDemo
    ? { sys: 120, dia: 78, weight: 66, exercise: true, salt: true, smokeFree: true }
    : {
        sys: profile.ap_hi,
        dia: profile.ap_lo,
        weight: profile.weight,
        exercise: profile.active === 1,
        salt: true,
        smokeFree: profile.smoke === 0,
      };
  const ranges = isDemo
    ? { sys: [110, 160], dia: [65, 100], weight: [55, 95] }
    : {
        sys: [Math.min(110, profile.ap_hi), Math.max(160, profile.ap_hi)],
        dia: [Math.min(65, profile.ap_lo), Math.max(100, profile.ap_lo)],
        weight: [
          Math.max(30, Math.min(55, Math.floor(profile.weight))),
          Math.min(200, Math.max(95, Math.ceil(profile.weight))),
        ],
      };

  const [scenario, setScenario] = useState(defaults);
  const [projection, setProjection] = useState(null);
  const [projecting, setProjecting] = useState(false);
  const [projectionError, setProjectionError] = useState("");
  const { toastClasses, showToast } = useToast(3200);
  const [openHabit, setOpenHabit] = useState(null);
  const closeHabit = useCallback(() => setOpenHabit(null), []);

  const bmi = (scenario.weight / (heightM * heightM)).toFixed(1);
  const badge = bmiBadge(bmi);
  const basePercent = isDemo ? DEMO_PERCENT : toPercent(analysis.prediction.probability);
  const projected = isDemo ? demoProjection(scenario, bmi) : projection;
  const delta = projected === null ? null : basePercent - projected;
  const view = deltaView(delta, scenario.sys, scenario.dia);

  function update(name, value) {
    setScenario((previous) => ({ ...previous, [name]: value }));
    setProjection(null);
    setProjectionError("");
  }

  function resetDefaults() {
    setScenario(defaults);
    setProjection(null);
    setProjectionError("");
  }

  async function handleProject() {
    if (isDemo) {
      showToast();
      return;
    }
    if (scenario.sys <= scenario.dia) {
      setProjectionError("La presión sistólica debe ser mayor que la diastólica.");
      return;
    }

    try {
      setProjecting(true);
      setProjectionError("");
      const result = await simulateScenario({
        original: profile,
        changes: {
          ap_hi: scenario.sys,
          ap_lo: scenario.dia,
          weight: scenario.weight,
          active: scenario.exercise ? 1 : 0,
          smoke: scenario.smokeFree ? 0 : 1,
        },
      });
      setProjection(toPercent(result.simulated.probability));
    } catch (error) {
      setProjectionError(error.message);
    } finally {
      setProjecting(false);
    }
  }

  return (
    <main className="w-full pt-24 bg-surface min-h-[calc(100vh-140px)]">
      <div className="flex flex-col w-full">
        <div className="w-full px-margin-mobile md:px-margin max-w-7xl mx-auto py-space-md space-y-space-lg">
          <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-surface-card via-surface-container-low to-surface-card p-space-md md:p-space-lg shadow-sm">
            <div className="absolute -right-8 -top-8 w-44 h-44 rounded-full bg-secondary-container/20 blur-2xl pointer-events-none"></div>
            <div className="absolute -left-8 -bottom-8 w-44 h-44 rounded-full bg-primary-fixed/30 blur-2xl pointer-events-none"></div>
            <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-space-md">
              <div className="space-y-space-xs max-w-2xl">
                <div className="flex items-center gap-space-xs flex-wrap">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-metric-subtle text-indigo-metric font-label-sm">
                    <span className="w-2 h-2 rounded-full bg-indigo-metric animate-pulse"></span>
                    {" "}Escenario hipotético de prevención
                  </span>
                  {" "}
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-surface-container text-text-secondary font-label-sm">
                    <span className="material-symbols-outlined text-[14px]">
                      tune
                    </span>
                    {" "}Simulador interactivo
                  </span>
                </div>
                <h1 className="font-headline-lg text-headline-lg text-text-primary tracking-tight">
                  Explora qué cambiaría si...
                </h1>
                <p className="font-body-md text-text-secondary flex items-start gap-1.5">
                  <span className="material-symbols-outlined text-amber-warning text-[18px] shrink-0 mt-0.5">
                    tips_and_updates
                  </span>
                  {" "}
                  <span>
                    Este escenario es hipotético y no garantiza un cambio médico absoluto. Proyecta de manera didáctica el beneficio vascular acumulado al adoptar hábitos protectores.
                  </span>
                </p>
              </div>
              <div className="flex items-center gap-space-sm bg-surface-card px-space-md py-space-sm rounded-xl shadow-sm self-start md:self-auto shrink-0">
                <div className="w-9 h-9 rounded-full bg-surface-container-high flex items-center justify-center text-text-secondary">
                  <span className="material-symbols-outlined text-[20px]">
{isDemo || profile.gender === 1 ? "female" : "male"}
</span>
                </div>
                <div className="flex flex-col">
                  <span className="font-label-sm text-text-muted">
                    Perfil fijo de referencia
                  </span>
                  {" "}
                  <span className="font-title-md text-title-md text-text-primary">
                    {isDemo ? "Clara · 52 años · Mujer" : `Clara · ${profile.age_years} años · ${profile.gender === 1 ? "Mujer" : "Hombre"}`}
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
                      Ajustes del Escenario
                    </h2>
                  </div>
                  {" "}
                  <button className="text-text-muted hover:text-text-primary font-label-sm flex items-center gap-1 transition-colors" id="btnReset" onClick={resetDefaults} type="button">
                    <span className="material-symbols-outlined text-[15px]">
                      restart_alt
                    </span>
                    {" "}Restablecer
                  </button>
                </div>
                <div className="space-y-space-md pt-space-xs">
                  <div className="space-y-space-xs bg-surface-container-low/70 p-space-sm rounded-xl">
                    <div className="flex justify-between items-center">
                      <span className="font-label-md text-text-primary flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-coral-alert text-[18px]">
                          speed
                        </span>
                        {" "}Presión Sistólica
                      </span>
                      {" "}
                      <span className="font-title-md text-title-md text-text-primary font-bold">
                        <span id="labelSystolic">
{scenario.sys}
</span>
                        {" "}
                        <span className="font-label-sm text-text-muted">
                          mmHg
                        </span>
                      </span>
                    </div>
                    {" "}
                    <input className="w-full accent-primary-container cursor-pointer h-2 bg-surface-variant rounded-lg appearance-none" id="sliderSystolic" max={ranges.sys[1]} min={ranges.sys[0]} onChange={(event) => update("sys", Number(event.target.value))} step="1" type="range" value={scenario.sys} />
                    {" "}
                    <div className="flex justify-between font-label-sm text-text-muted px-0.5">
                      <span className="text-mint-vitality font-semibold">
                        110 (Óptima)
                      </span>
                      {" "}
                      <span className="text-amber-warning font-semibold">
                        130 (Alerta)
                      </span>
                      {" "}
                      <span className="text-coral-alert font-semibold">
                        160 (Elevada)
                      </span>
                    </div>
                  </div>
                  <div className="space-y-space-xs bg-surface-container-low/70 p-space-sm rounded-xl">
                    <div className="flex justify-between items-center">
                      <span className="font-label-md text-text-primary flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-indigo-metric text-[18px]">
                          compress
                        </span>
                        {" "}Presión Diastólica
                      </span>
                      {" "}
                      <span className="font-title-md text-title-md text-text-primary font-bold">
                        <span id="labelDiastolic">
{scenario.dia}
</span>
                        {" "}
                        <span className="font-label-sm text-text-muted">
                          mmHg
                        </span>
                      </span>
                    </div>
                    {" "}
                    <input className="w-full accent-primary-container cursor-pointer h-2 bg-surface-variant rounded-lg appearance-none" id="sliderDiastolic" max={ranges.dia[1]} min={ranges.dia[0]} onChange={(event) => update("dia", Number(event.target.value))} step="1" type="range" value={scenario.dia} />
                    {" "}
                    <div className="flex justify-between font-label-sm text-text-muted px-0.5">
                      <span>
                        65 normal
                      </span>
                      {" "}
                      <span>
                        80 límite
                      </span>
                      {" "}
                      <span>
                        100 alta
                      </span>
                    </div>
                  </div>
                  <div className="bg-surface-container-low/70 p-space-sm rounded-xl space-y-space-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-label-md text-text-primary flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-tertiary-container text-[18px]">
                          scale
                        </span>
                        {" "}Peso simulado
                      </span>
                      {" "}
                      <div className="flex items-center gap-space-xs">
                        <span className="font-title-md text-title-md text-text-primary font-bold">
                          <span id="labelWeight">
{Number(scenario.weight).toFixed(0)}
</span>
                          {" "}
                          <span className="font-label-sm text-text-muted">
                            kg
                          </span>
                        </span>
                        {" "}
                        <span className={badge.className} id="badgeBmi">
{badge.text}
</span>
                      </div>
                    </div>
                    {" "}
                    <input className="w-full accent-primary-container cursor-pointer h-2 bg-surface-variant rounded-lg appearance-none" id="sliderWeight" max={ranges.weight[1]} min={ranges.weight[0]} onChange={(event) => update("weight", Number(event.target.value))} step="0.5" type="range" value={scenario.weight} />
                    {" "}
                    <div className="flex justify-between font-label-sm text-text-muted px-0.5">
                      <span>
                        {`${ranges.weight[0]} kg`}
                      </span>
                      {" "}
                      <span>
                        {`Estatura: ${heightM.toFixed(2)} m`}
                      </span>
                      {" "}
                      <span>
                        {`${ranges.weight[1]} kg`}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="pt-space-xs space-y-space-sm">
                  <span className="font-label-sm uppercase tracking-wider text-text-muted block">
                    Hábitos protectores clave
                  </span>
                  {" "}
                  <div className="flex items-center justify-between p-space-sm bg-mint-vitality-subtle/50 rounded-xl transition-all">
                    <div className="flex items-center gap-space-sm">
                      <div className="w-9 h-9 rounded-full bg-mint-vitality-subtle flex items-center justify-center text-mint-vitality">
                        <span className="material-symbols-outlined text-[20px]">
                          directions_run
                        </span>
                      </div>
                      <div>
                        <p className="font-label-md text-text-primary font-semibold">
                          Actividad física regular
                        </p>
                        <p className="font-label-sm text-text-secondary">
                          +30 min diarios de caminata
                        </p>
                      </div>
                    </div>
                    {" "}
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input checked={scenario.exercise} className="sr-only peer" id="toggleExercise" onChange={(event) => update("exercise", event.target.checked)} type="checkbox" />
                      {" "}
                      <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container"></div>
                    </label>
                  </div>
                  <div className="flex items-center justify-between p-space-sm bg-amber-warning-subtle/50 rounded-xl transition-all">
                    <div className="flex items-center gap-space-sm">
                      <div className="w-9 h-9 rounded-full bg-amber-warning-subtle flex items-center justify-center text-amber-warning">
                        <span className="material-symbols-outlined text-[20px]">
                          nutrition
                        </span>
                      </div>
                      <div>
                        <p className="font-label-md text-text-primary font-semibold">
                          Baja ingesta de sodio
                        </p>
                        <p className="font-label-sm text-text-secondary">
                          Cocina con hierbas y sin ultraprocesados
                        </p>
                      </div>
                    </div>
                    {" "}
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input checked={scenario.salt} className="sr-only peer" id="toggleSalt" onChange={(event) => update("salt", event.target.checked)} type="checkbox" />
                      {" "}
                      <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container"></div>
                    </label>
                  </div>
                  <div className="flex items-center justify-between p-space-sm bg-indigo-metric-subtle/50 rounded-xl transition-all">
                    <div className="flex items-center gap-space-sm">
                      <div className="w-9 h-9 rounded-full bg-indigo-metric-subtle flex items-center justify-center text-indigo-metric">
                        <span className="material-symbols-outlined text-[20px]">
                          smoke_free
                        </span>
                      </div>
                      <div>
                        <p className="font-label-md text-text-primary font-semibold">
                          Cero humo / No tabaquismo
                        </p>
                        <p className="font-label-sm text-text-secondary">
                          Arterias libres de nicotina activa
                        </p>
                      </div>
                    </div>
                    {" "}
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input checked={scenario.smokeFree} className="sr-only peer" id="toggleSmoke" onChange={(event) => update("smokeFree", event.target.checked)} type="checkbox" />
                      {" "}
                      <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container"></div>
                    </label>
                  </div>
                </div>
                <div className="pt-space-xs flex gap-space-sm">
                  <button className="w-full py-3 px-4 bg-primary-container text-on-primary rounded-xl font-label-md font-semibold flex items-center justify-center gap-2 shadow-sm hover:brightness-105 active:scale-[0.98] transition-all disabled:opacity-70" disabled={projecting} id="btnRecalculate" onClick={handleProject} type="button">
                    <span className="material-symbols-outlined text-[18px]">
                      auto_graph
                    </span>
                    {" "}{projecting ? "Proyectando..." : "Proyectar resultados"}
                  </button>
                </div>
              </div>
              <div className="bg-gradient-to-r from-surface-card to-surface-container-low p-space-md rounded-xl flex items-center gap-space-md shadow-sm">
                <div className="w-12 h-12 rounded-xl bg-secondary-container/40 flex items-center justify-center text-secondary shrink-0">
                  <span className="material-symbols-outlined text-[26px]">
                    vital_signs
                  </span>
                </div>
                <div>
                  <p className="font-title-md text-title-md text-text-primary">
                    Efecto multiplicador
                  </p>
                  <p className="font-body-md text-text-secondary">
                    Combinar actividad regular y bajo sodio potencia hasta un 40% el descenso natural de la presión.
                  </p>
                </div>
              </div>
            </div>
            <div className="lg:col-span-7 flex flex-col gap-space-md">
              <div className="bg-surface-card rounded-xl p-space-md md:p-space-lg shadow-sm space-y-space-lg">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="font-label-sm uppercase tracking-wider text-text-muted">
                      Proyección Vascular a 10 años
                    </span>
                    {" "}
                    <h2 className="font-headline-md text-headline-md text-text-primary">
                      Comparación de Riesgo Relativo
                    </h2>
                  </div>
                  {" "}
                  <span className="px-3 py-1 rounded-full bg-mint-vitality-subtle text-secondary font-label-sm font-semibold flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-mint-vitality"></span>
                    {" "}Modelo ESC SCORE2
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-11 gap-space-md items-center">
                  <div className="md:col-span-5 bg-surface-container-low rounded-xl p-space-md flex flex-col items-center text-center space-y-space-sm relative overflow-hidden">
                    <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-surface-card text-text-secondary font-label-sm">
                      Línea Base
                    </div>
                    <div className="w-28 h-28 rounded-full bg-primary-fixed/40 flex items-center justify-center relative mt-3">
                      <div className="w-24 h-24 rounded-full bg-indigo-metric-subtle flex items-center justify-center">
                        <svg className="w-14 h-14 text-primary animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"></path>
                        </svg>
                      </div>
                    </div>
                    <div>
                      <span className="font-metric-display text-metric-display text-text-primary block font-bold">
{`${basePercent}%`}
</span>
                      {" "}
                      <span className="font-label-md text-text-secondary">
                        Estimación actual
                      </span>
                    </div>
                    <div className="w-full bg-surface-card rounded-lg p-2 font-label-sm text-text-secondary flex justify-between">
                      <span>
                        {isDemo ? "Presión: 142/88" : `Presión: ${profile.ap_hi}/${profile.ap_lo}`}
                      </span>
                      {" "}
                      <span>
                        {isDemo ? "IMC: 27.8" : `IMC: ${profile.bmi.toFixed(1)}`}
                      </span>
                    </div>
                  </div>
                  <div className="md:col-span-1 flex flex-col items-center justify-center py-2 md:py-0">
                    <div className="flex flex-col items-center gap-1">
                      <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary shadow-md transform md:rotate-0 rotate-90">
                        <span className="material-symbols-outlined text-[20px]">
                          arrow_forward
                        </span>
                      </div>
                      <div className="hidden md:flex flex-col items-center">
                        <span className="h-6 w-0.5 bg-mint-vitality-border"></span>
                        {" "}
                        <span className={view.smClass} id="badgeDiffSm">
{view.smText}
</span>
                      </div>
                    </div>
                  </div>
                  <div className="md:col-span-5 bg-gradient-to-b from-mint-vitality-subtle/70 to-surface-card rounded-xl p-space-md flex flex-col items-center text-center space-y-space-sm relative overflow-hidden shadow-sm">
                    <div className="absolute -right-6 -top-6 w-24 h-24 rounded-full bg-secondary-container/40 blur-xl"></div>
                    <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-mint-vitality text-on-secondary font-label-sm font-semibold">
                      Simulado
                    </div>
                    <div className="w-28 h-28 rounded-full bg-secondary-container/30 flex items-center justify-center relative mt-3 shadow-inner">
                      <div className="absolute inset-0 rounded-full bg-mint-vitality/20 animate-ping opacity-75"></div>
                      <div className="w-24 h-24 rounded-full bg-mint-vitality-subtle flex items-center justify-center relative z-10">
                        <svg className="w-14 h-14 text-mint-vitality" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"></path>
                        </svg>
                      </div>
                    </div>
                    <div>
                      <span className="font-metric-display text-metric-display text-secondary block font-bold" id="projectedPercent">
{projected === null ? "--%" : `${projected}%`}
</span>
                      {" "}
                      <span className="font-label-md text-secondary font-semibold">
                        Estimación proyectada
                      </span>
                    </div>
                    <div className="w-full bg-surface-card rounded-lg p-2 font-label-sm text-text-primary flex justify-between shadow-xs">
                      <span id="summaryBP">
{`Presión: ${scenario.sys}/${scenario.dia}`}
</span>
                      {" "}
                      <span id="summaryBmi">
{`IMC: ${bmi}`}
</span>
                    </div>
                  </div>
                </div>
                <div className="bg-gradient-to-r from-mint-vitality-subtle via-surface-container-low to-surface-card p-space-md rounded-xl flex items-start gap-space-md">
                  <div className="w-10 h-10 rounded-full bg-mint-vitality flex items-center justify-center text-on-secondary shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-[22px]">
                      trending_down
                    </span>
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-space-xs flex-wrap">
                      <span className={view.badgeClass} id="deltaBadge">
{view.badgeText}
</span>
                      {" "}
                      <span className="font-label-md text-secondary font-semibold">
                        Impacto favorable proyectado
                      </span>
                    </div>
                    <p className={projectionError ? "font-body-md text-error" : "font-body-md text-text-secondary"} id="scenarioDescription">
{projectionError || view.description}
</p>
                  </div>
                </div>
                <div className="pt-space-xs space-y-space-xs">
                  <div className="flex justify-between items-center text-text-secondary font-label-sm">
                    <span>
                      Trayectoria de adherencia sugerida
                    </span>
                    {" "}
                    <span className="text-secondary font-semibold">
                      6 a 12 meses continuos
                    </span>
                  </div>
                  <div className="w-full h-3 bg-surface-container rounded-full overflow-hidden flex">
                    <div className="h-full bg-primary-container w-[40%]" title="Etapa 1: Adaptación de hábitos (40%)"></div>
                    <div className="h-full bg-secondary w-[35%]" title="Etapa 2: Estabilización hemodinámica (35%)"></div>
                    <div className="h-full bg-mint-vitality w-[25%]" title="Etapa 3: Reducción consolidada (25%)"></div>
                  </div>
                  <div className="flex justify-between text-[10px] text-text-muted">
                    <span>
                      Inicio progresivo
                    </span>
                    {" "}
                    <span>
                      Constancia metabólica
                    </span>
                    {" "}
                    <span>
                      Protección vascular plena
                    </span>
                  </div>
                </div>
              </div>
              <div className="bg-surface-card rounded-xl p-space-md shadow-sm flex flex-col sm:flex-row items-center justify-between gap-space-md">
                <div className="flex items-center gap-space-sm w-full sm:w-auto">
                  <div className="w-10 h-10 rounded-full bg-indigo-metric-subtle flex items-center justify-center text-indigo-metric shrink-0">
                    <span className="material-symbols-outlined text-[20px]">
                      bookmark_added
                    </span>
                  </div>
                  <div>
                    <p className="font-label-md text-text-primary font-semibold">
                      ¿Te motiva esta meta preventiva?
                    </p>
                    <p className="font-label-sm text-text-secondary">
                      Convierte este escenario en tus metas personales monitoreadas.
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-space-xs w-full sm:w-auto justify-end">
                  <button className="px-4 py-2.5 rounded-xl bg-surface-container text-text-secondary hover:bg-surface-container-high font-label-md transition-colors" onClick={() => onNavigate("resultado")} type="button">
                    Regresar
                  </button>
                  {" "}
                  <button className="whitespace-nowrap px-5 py-2.5 rounded-xl bg-primary-container text-on-primary hover:bg-primary font-label-md font-semibold flex items-center gap-1.5 shadow-sm transition-all" id="btnSaveGoal" onClick={() => showToast()} type="button">
                    <span className="material-symbols-outlined text-[18px]">
                      flag
                    </span>
                    {" "}Guardar objetivo
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="space-y-space-md pt-space-xs">
            <div>
              <span className="font-label-sm uppercase tracking-wider text-secondary font-semibold">
                Evidencia de alto impacto
              </span>
              <h2 className="font-headline-md text-headline-md text-text-primary">
                Micro-hábitos que suman
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
          <div className={`fixed bottom-6 right-6 z-50 bg-text-primary text-on-primary px-space-md py-space-sm rounded-xl shadow-lg flex items-center gap-space-sm transition-all duration-300 ${toastClasses}`} id="toastNotification">
            <span className="material-symbols-outlined text-mint-vitality text-[22px]">
              task_alt
            </span>
            {" "}
            <div className="flex flex-col">
              <span className="font-label-md font-semibold">
                Objetivo guardado
              </span>
              {" "}
              <span className="font-label-sm text-text-muted">
                Se sincronizó con tu plan semanal de prevención.
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

import { useEffect, useRef, useState } from "react";

import {
  DEMO_PERCENT,
  featureIcon,
  featureName,
  featureValue,
  toPercent,
} from "../utils/health";
import { IMAGES } from "../utils/images";
import WellnessPlan from "../components/WellnessPlan";

function bpLabel(sys, dia) {
  if (sys < 120 && dia < 80) return "Óptima";
  if (sys <= 129 && dia < 85) return "Normal";
  if (sys <= 139 || dia <= 89) return "Elevación leve";
  return "Elevada";
}

function bmiLabel(bmi) {
  if (bmi < 18.5) return "Bajo peso";
  if (bmi < 25) return "Saludable";
  if (bmi < 30) return "Sobrepeso leve";
  return "Elevado";
}

function formatDate(date) {
  const day = date.toLocaleDateString("es-ES", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  const time = date.toLocaleTimeString("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
  });
  return `${day} · ${time} hrs`;
}

// Tarjetas "Qué influyó" con los factores SHAP reales, mismo diseño de Stitch
function ShapFactorCards({ factors }) {
  if (!factors.length) {
    return (
      <p className="font-body-md text-body-md text-on-surface-variant md:col-span-3">
        El modelo no devolvió factores explicativos para este perfil.
      </p>
    );
  }

  return factors.slice(0, 3).map((factor, index) => {
    const up = factor.direction === "increase";
    return (
      <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between" key={`${factor.feature}-${index}`}>
        <div>
          <div className="flex items-center justify-between mb-space-sm">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${up ? "bg-tertiary-fixed text-on-tertiary-fixed" : "bg-secondary-container text-on-secondary-container"}`}>
              <span className="material-symbols-outlined text-[24px]">
                {featureIcon(factor.feature)}
              </span>
            </div>
            <span className={`px-2.5 py-1 rounded-full font-label-sm font-semibold ${up ? "bg-error-container text-on-error-container" : "bg-surface-container text-primary"}`}>
              {up ? "Aumentó la estimación" : "Disminuyó la estimación"}
            </span>
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <h3 className="font-headline-sm text-headline-sm font-bold text-on-surface">
              {featureName(factor.feature)}
            </h3>
            <span className={`font-label-md font-bold ${up ? "text-tertiary" : "text-secondary"}`}>
              {featureValue(factor.feature, factor.value)}
            </span>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant mt-2 leading-relaxed">
            {up
              ? "Este factor elevó la salida del modelo para tu perfil."
              : "Este factor redujo la salida del modelo para tu perfil."}{" "}
            No implica causa directa.
          </p>
        </div>
        <div className="mt-space-md pt-space-sm border-t border-surface-container flex items-center justify-between text-on-surface font-label-sm">
          <span className="text-on-surface-variant">
            Influencia en el modelo:
          </span>
          <span className={`${up ? "text-tertiary" : "text-secondary"} font-semibold flex items-center gap-1`}>
            <span className="material-symbols-outlined text-[16px]">
              {up ? "trending_up" : "trending_down"}
            </span>
            {index === 0 ? "Mayor peso" : `Factor ${index + 1}`}
          </span>
        </div>
      </div>
    );
  });
}

// Recomendaciones RAG bajo demanda con las tarjetas de Stitch
function RagRecommendations({ rag, loading, error, onRequest }) {
  if (!rag) {
    return (
      <div className="md:col-span-3 bg-surface-container-lowest rounded-xl shadow-sm p-space-lg flex flex-col sm:flex-row sm:items-center justify-between gap-space-md">
        <div className="flex items-start gap-space-sm">
          <div className="w-10 h-10 rounded-xl bg-secondary-container flex items-center justify-center text-on-secondary-container shrink-0">
            <span className="material-symbols-outlined text-[24px]">
              eco
            </span>
          </div>
          <div>
            <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
              Información preventiva personalizada
            </h3>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Solicita recomendaciones educativas basadas en este análisis y en sus factores explicativos.
            </p>
            {error && (
              <p className="font-label-md text-error mt-2">
                {error}
              </p>
            )}
          </div>
        </div>
        <button className="px-5 py-2.5 rounded-xl bg-primary-container hover:bg-primary text-on-primary font-label-md font-semibold transition-all shadow-md flex items-center justify-center gap-1.5 shrink-0 disabled:opacity-70" disabled={loading} onClick={onRequest} type="button">
          <span className="material-symbols-outlined text-[18px]">
            {loading ? "hourglass_top" : "auto_awesome"}
          </span>
          <span>
            {loading ? "Consultando recomendaciones..." : "Solicitar recomendaciones"}
          </span>
        </button>
      </div>
    );
  }

  return (
    <>
      {rag.summary && (
        <div className="md:col-span-3 bg-surface-container-lowest rounded-xl shadow-sm p-space-md">
          <span className="font-label-sm uppercase font-semibold text-secondary tracking-wider">
            Resumen
          </span>
          <p className="font-body-lg text-body-lg text-on-surface mt-1">
            {rag.summary}
          </p>
        </div>
      )}
      {rag.recommendations?.map((item, index) => (
        <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col" key={index}>
          <div className="p-space-md flex-1 flex flex-col justify-between">
            <div>
              <span className="inline-flex bg-surface-container px-2.5 py-1 rounded-full text-secondary font-label-sm font-semibold items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">
                  eco
                </span>
                {item.factor}
              </span>
              <p className="font-body-md text-body-md text-on-surface-variant mt-space-sm">
                {item.recommendation}
              </p>
            </div>
            <div className="mt-space-md bg-surface-container-low p-2.5 rounded-lg flex items-center gap-2 text-on-surface font-label-sm">
              <span className="material-symbols-outlined text-secondary text-[18px]">
                menu_book
              </span>
              <span>
                {item.sources?.length
                  ? `${item.sources.length} fuente(s) consultada(s)`
                  : "Sin fuentes asociadas"}
              </span>
            </div>
          </div>
        </div>
      ))}
      {(rag.considerations || rag.note) && (
        <div className="md:col-span-3 bg-surface-container-high/60 rounded-xl p-3.5 flex items-start gap-2.5 text-on-surface-variant">
          <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
            verified_user
          </span>
          <div className="font-label-sm text-label-sm leading-tight space-y-1">
            {rag.considerations && (
              <p>
                <strong className="text-on-surface font-semibold">
                  Consideraciones:
                </strong>{" "}
                {rag.considerations}
              </p>
            )}
            {rag.note && (
              <p>
                <strong className="text-on-surface font-semibold">
                  Importante:
                </strong>{" "}
                {rag.note}
              </p>
            )}
          </div>
        </div>
      )}
    </>
  );
}

function RagSources({ rag }) {
  const sources = (rag?.recommendations || []).flatMap((item) => item.sources || []);
  const unique = sources.filter(
    (source, index) => sources.findIndex((other) => other.source_id === source.source_id) === index
  );

  if (!unique.length) {
    return (
      <p className="font-body-md text-on-surface-variant">
        Solicita las recomendaciones para ver las fuentes documentales utilizadas.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md font-body-md text-on-surface-variant">
      {unique.map((source) => (
        <div className="flex items-start gap-2" key={source.source_id}>
          <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
            bookmark
          </span>
          <div>
            <strong className="text-on-surface font-medium block">
              {source.source}
            </strong>
            <p className="text-xs text-on-surface-variant">
              Referencia: {source.source_id}
              {source.lines && ` · Líneas ${source.lines.from}–${source.lines.to}`}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ResultPage({
  analysis,
  profile,
  recommendations,
  recommendationsLoading,
  recommendationsError,
  onRequestRecommendations,
  onNavigate,
}) {
  const isDemo = !analysis;
  const percent = isDemo ? DEMO_PERCENT : toPercent(analysis.prediction.probability);
  const age = isDemo ? 52 : profile.age_years;
  const bpText = isDemo ? "135/85" : `${profile.ap_hi}/${profile.ap_lo}`;
  const bmi = isDemo ? 26.4 : profile.bmi;
  const [reportDate] = useState(() => formatDate(new Date()));
  // 28% en Stitch equivale a y=132; el corazón ocupa de y=2 a y=175
  const liquidY = Math.max(2, 175 - (percent / DEMO_PERCENT) * 43);

  const [motionActive, setMotionActive] = useState(true);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const [planTab, setPlanTab] = useState("recetas");
  const planRef = useRef(null);
  const heartRef = useRef(null);
  const haloRef = useRef(null);
  const haloOuterRef = useRef(null);

  // Animación de latido suave del script de Stitch
  useEffect(() => {
    const setScale = (heart, halo, outer) => {
      if (heartRef.current) heartRef.current.style.transform = `scale(${heart})`;
      if (haloRef.current) haloRef.current.style.transform = `scale(${halo})`;
      if (haloOuterRef.current) haloOuterRef.current.style.transform = `scale(${outer})`;
    };

    if (!motionActive) {
      setScale(1, 1, 1);
      return undefined;
    }

    const timers = [];
    const interval = setInterval(() => {
      setScale(1.065, 1.25, 1.4);
      timers.push(setTimeout(() => {
        setScale(1.02, 1.1, 1.2);
        timers.push(setTimeout(() => setScale(1, 1, 1), 240));
      }, 160));
    }, 1100);

    return () => {
      clearInterval(interval);
      timers.forEach(clearTimeout);
    };
  }, [motionActive]);

  useEffect(() => {
    if (!saved) return undefined;
    const timer = setTimeout(() => setSaved(false), 3200);
    return () => clearTimeout(timer);
  }, [saved]);

  function openMeasureGuide() {
    setPlanTab("medir");
    planRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function handleLink(event, path) {
    event.preventDefault();
    onNavigate(path);
  }

  return (
    <main className="w-full pt-24 bg-surface min-h-[calc(100vh-140px)]">
      <div className="flex flex-col w-full">
        {/* Subtle Ambient Glow */}
        <div className="relative w-full max-w-7xl mx-auto px-gutter py-space-md">
          <div className="absolute top-10 left-1/2 -translate-x-1/2 w-96 h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none -z-10"></div>
          <div className="absolute top-40 left-1/3 w-72 h-72 bg-secondary/5 rounded-full blur-2xl pointer-events-none -z-10"></div>
          {/* Header Meta Context */}
          <header className="flex flex-col md:flex-row md:items-end justify-between gap-space-md mb-space-xl">
            <div className="flex flex-col">
              <div className="flex items-center gap-2 mb-space-xs">
                <span className="px-2.5 py-0.5 rounded-full bg-surface-container text-primary font-label-sm uppercase tracking-wider font-semibold">
                  Evaluación Personalizada
                </span>
                {" "}
                <span className="text-outline text-label-sm">
                  •
                </span>
                {" "}
                <span className="text-on-surface-variant font-label-md flex items-center gap-1">
                  <span className="material-symbols-outlined text-[16px] text-secondary">
                    calendar_today
                  </span>
                  {" "}{isDemo ? "24 de Mayo, 2025 · 09:42 hrs" : reportDate}
                </span>
              </div>
              <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
                Tu estimación cardiovascular personalizada
              </h1>
              <p className="font-body-lg text-body-lg text-on-surface-variant mt-1">
                Informe preventivo generado para{" "}
                <strong className="text-on-surface font-semibold">
                  Clara Méndez
                </strong>
                {" "}({age} años)
              </p>
            </div>
            {/* Quick Accessibility Motion Switch */}
            <div className="flex items-center gap-space-sm bg-surface-container-lowest p-1.5 rounded-xl shadow-sm border border-outline-variant/30">
              <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-all font-label-md" id="motion-toggle-btn" onClick={() => setMotionActive((value) => !value)} type="button">
                <span className={`material-symbols-outlined text-[18px] ${motionActive ? "text-secondary" : "text-outline"}`} id="motion-icon">
{motionActive ? "pulse_alert" : "motion_photos_pause"}
</span>
                {" "}
                <span id="motion-text">
{motionActive ? "Animación activa" : "Modo movimiento reducido"}
</span>
              </button>
            </div>
          </header>
          {/* Bento Grid Section */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter items-start">
            {/* HERO HEART CONTAINER (Columns 1 to 7) */}
            <section className="lg:col-span-7 flex flex-col bg-surface-container-lowest rounded-xl shadow-md p-space-lg relative overflow-hidden">
              {/* Top Action / Badge */}
              <div className="flex items-center justify-between z-10">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-secondary animate-ping"></span>
                  {" "}
                  <span className="font-label-md font-semibold text-secondary uppercase tracking-wider">
                    Latido basal estimado
                  </span>
                </div>
                {" "}
                <span className="font-label-sm text-on-surface-variant bg-surface-container-low px-3 py-1 rounded-full">
                  Proyección a 10 años
                </span>
              </div>
              {/* Central Vector Heart Visual */}
              <div className="relative flex flex-col items-center justify-center my-space-md py-4">
                {/* Animated Pulsing Waves Behind Heart */}
                <div className="absolute w-64 h-64 rounded-full bg-secondary-fixed/40 transition-transform duration-700 ease-out transform scale-110 pointer-events-none -z-0" id="heart-pulse-halo" ref={haloRef}></div>
                <div className="absolute w-80 h-80 rounded-full bg-surface-variant/40 transition-transform duration-1000 ease-out transform scale-125 pointer-events-none -z-0" id="heart-pulse-halo-outer" ref={haloOuterRef}></div>
                {/* Stylized Proportional SVG Heart */}
                <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center transition-transform duration-300" id="cardio-heart-wrapper" ref={heartRef}>
                  <svg className="w-full h-full drop-shadow-lg overflow-visible" viewBox="0 0 200 185" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      {/* Clip path shaped like an anatomical/stylized heart */}
                      <clipPath id="heart-clip-shape">
                        <path d="M100,175 C96,170 18,108 8,62 C0,26 30,2 66,2 C83,2 94,14 100,22 C106,14 117,2 134,2 C170,2 200,26 192,62 C182,108 104,170 100,175 Z"></path>
                      </clipPath>
                      {/* Liquid Heart Fill Gradient */}
                      <linearGradient id="heartLiquidGradient" x1="0%" x2="0%" y1="100%" y2="0%">
                        <stop offset="0%" stopColor="#006b5f"></stop>
                        <stop offset="60%" stopColor="#2563eb"></stop>
                        <stop offset="100%" stopColor="#4fdbc8"></stop>
                      </linearGradient>
                      {/* Subtle Inner Glow */}
                      <filter height="140%" id="softGlow" width="140%" x="-20%" y="-20%">
                        <feGaussianBlur result="blur" stdDeviation="4"></feGaussianBlur>
                        <feComposite in="SourceGraphic" in2="blur" operator="over"></feComposite>
                      </filter>
                    </defs>
                    {/* Outer Base Heart Shell (Background Track) */}
                    <path className="fill-surface-container" d="M100,175 C96,170 18,108 8,62 C0,26 30,2 66,2 C83,2 94,14 100,22 C106,14 117,2 134,2 C170,2 200,26 192,62 C182,108 104,170 100,175 Z"></path>
                    {/* Liquid Proportional Heart Fill Clipped (28% fill height from bottom = ~52px from bottom) */}
                    <g clipPath="url(#heart-clip-shape)">
                      {/* Background subtle wave */}
                      <rect className="fill-surface-container-high" height="185" width="200" x="0" y="0"></rect>
                      {/* Dynamic Liquid Rectangle representing 28% filled volume */}
                      <g className="transition-all duration-1000 ease-in-out" id="liquid-level">
                        <rect fill="url(#heartLiquidGradient)" height={192 - liquidY} width="200" x="0" y={liquidY}></rect>
                        {/* Organic Wave Edge at liquid line */}
                        <path d={`M 0,${liquidY} Q 50,${liquidY - 6} 100,${liquidY} T 200,${liquidY} L 200,190 L 0,190 Z`} fill="url(#heartLiquidGradient)" opacity="0.95"></path>
                      </g>
                    </g>
                    {/* Glossy / Sleek Contour Rim */}
                    <path d="M100,175 C96,170 18,108 8,62 C0,26 30,2 66,2 C83,2 94,14 100,22 C106,14 117,2 134,2 C170,2 200,26 192,62 C182,108 104,170 100,175 Z" fill="none" opacity="0.75" stroke="#ffffff" strokeWidth="3"></path>
                    {/* Heart Rhythm Pulse Trace Overlay inside heart */}
                    <path d="M 40,82 L 72,82 L 82,65 L 94,102 L 106,54 L 118,88 L 126,82 L 160,82" fill="none" filter="url(#softGlow)" opacity="0.85" stroke="#ffffff" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                  </svg>
                  {/* Digital Percentage Badge Inside the Heart */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none select-none">
                    <span className="font-headline-sm text-headline-sm font-semibold tracking-wide text-on-surface uppercase -mb-1">
                      Estimación
                    </span>
                    {" "}
                    <div className="flex items-baseline">
                      <span className="font-display-hero text-[58px] sm:text-[68px] leading-none font-bold text-on-surface tracking-tighter drop-shadow-sm">
{percent}
</span>
                      {" "}
                      <span className="font-headline-md text-headline-md text-primary font-bold ml-0.5">
                        %
                      </span>
                    </div>
                    {" "}
                    <span className="font-label-sm text-label-sm text-on-surface-variant font-medium bg-surface-container-lowest/80 backdrop-blur px-2.5 py-0.5 rounded-full shadow-sm mt-1">
{isDemo ? "Margen controlado" : analysis.prediction.classification === 1 ? "Por encima del umbral" : "Por debajo del umbral"}
</span>
                  </div>
                </div>
              </div>
              {/* CONTINUOUS SPECTRUM BAR (0% to 100%) */}
              <div className="w-full flex flex-col pt-space-xs px-space-sm sm:px-space-md">
                <div className="flex justify-between items-center text-on-surface-variant font-label-sm mb-10 font-medium">
                  <span className="flex items-center gap-1 text-secondary">
                    <span className="material-symbols-outlined text-[14px]">
                      spa
                    </span>
                    {" "}Parámetros Óptimos (0%)
                  </span>
                  {" "}
                  <span className="text-tertiary flex items-center gap-1">
                    Atención Prioritaria (100%){" "}
                    <span className="material-symbols-outlined text-[14px]">
                      priority_high
                    </span>
                  </span>
                </div>
                {/* Gradient Spectrum with Position Marker */}
                <div className="relative w-full h-4 rounded-full shadow-inner bg-surface-container overflow-visible">
                  {/* Continuous Gradient from #14B8A6 through #F59E0B to #F43F5E */}
                  <div className="w-full h-full rounded-full" style={{ background: "linear-gradient(90deg, #14B8A6 0%, #3B82F6 22%, #F59E0B 60%, #F43F5E 100%)" }}></div>
                  {/* Precision Marker Indicator for 28% */}
                  <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 flex flex-col items-center z-20 pointer-events-none" style={{ left: `${percent}%` }}>
                    {/* Pill Marker */}
                    <div className="w-5 h-5 rounded-full bg-surface-container-lowest shadow-md border-2 border-primary flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-primary"></div>
                    </div>
                    {/* Floating Tooltip Arrow */}
                    <div className="absolute -top-8 whitespace-nowrap px-2 py-0.5 rounded-md bg-on-surface text-surface-bright font-label-sm font-semibold shadow-sm flex items-center gap-1">
                      <span>
                        {`Tu punto: ${percent}%`}
                      </span>
                    </div>
                  </div>
                </div>
                {/* Descriptive non-stigmatizing spectrum scale note */}
                <div className="flex items-center justify-between text-on-surface-variant font-label-sm mt-2 px-1">
                  <span>
                    Rango de preservación
                  </span>
                  {" "}
                  <span className="text-primary font-medium">
                    Zona de optimización activa
                  </span>
                  {" "}
                  <span>
                    Rango de vigilancia
                  </span>
                </div>
              </div>
              {/* Accessible Explanatory Card */}
              <div className="mt-space-lg bg-surface-container-low rounded-xl p-space-md flex items-start gap-space-sm">
                <span className="material-symbols-outlined text-primary text-[22px] shrink-0 mt-0.5">
                  lightbulb
                </span>
                {" "}
                <div className="flex flex-col">
                  <h2 className="font-title-md text-title-md text-on-surface font-semibold">
                    ¿Cómo leer este porcentaje?
                  </h2>
                  <p className="font-body-md text-body-md text-on-surface-variant mt-1">
                    No es un diagnóstico: es una estimación orientativa que puedes mejorar con hábitos diarios.
                  </p>
                </div>
              </div>
            </section>
            {/* RESULTS & HUMAN NARRATIVE (Columns 8 to 12) */}
            <section className="lg:col-span-5 flex flex-col gap-space-md">
              {/* Tu Resultado Narrative Card */}
              <div className="bg-surface-container-lowest rounded-xl shadow-md p-space-lg">
                <div className="flex items-center gap-2 mb-space-sm">
                  <div className="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
                    <span className="material-symbols-outlined text-[20px]">
                      monitor_heart
                    </span>
                  </div>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                    Tu resultado
                  </h2>
                </div>
                <p className="font-body-lg text-body-lg text-on-surface font-medium leading-relaxed">
                  Tu estimación actual indica una{" "}
                  <span className="text-primary font-semibold">
                    ventana de oportunidad clave
                  </span>
                  {" "}para cuidar tus arterias y ritmo cardíaco a través de ajustes cotidianos en presión y actividad física.
                </p>
                {/* Distinct Clinical Disclaimer Card */}
                <div className="mt-space-md bg-surface-container-high/60 rounded-xl p-3.5 flex items-start gap-2.5 text-on-surface-variant">
                  <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
                    verified_user
                  </span>
                  {" "}
                  <p className="font-label-sm text-label-sm leading-tight">
                    <strong className="text-on-surface font-semibold">
                      Nota importante:
                    </strong>
                    {" "}Es orientativa y no reemplaza una valoración médica.
                  </p>
                </div>
              </div>
              {/* Vital Signs Quick Snapshot Widget */}
              <div className="bg-surface-container-lowest rounded-xl shadow-md p-space-md">
                <span className="font-label-sm uppercase font-semibold text-on-surface-variant tracking-wider block mb-space-xs">
                  Registro actual evaluado
                </span>
                {" "}
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-surface-container-low rounded-lg p-2.5">
                    <span className="font-label-sm text-on-surface-variant block">
                      Tensión Art.
                    </span>
                    {" "}
                    <span className="font-title-md text-on-surface font-bold">
{bpText}
</span>
                    {" "}
                    <span className="font-label-sm text-tertiary block text-[11px] font-medium">
{isDemo ? "Elevación leve" : bpLabel(profile.ap_hi, profile.ap_lo)}
</span>
                  </div>
                  <div className="bg-surface-container-low rounded-lg p-2.5">
                    <span className="font-label-sm text-on-surface-variant block">
                      IMC
                    </span>
                    {" "}
                    <span className="font-title-md text-on-surface font-bold">
{Number(bmi).toFixed(1)}
</span>
                    {" "}
                    <span className="font-label-sm text-secondary block text-[11px] font-medium">
{bmiLabel(bmi)}
</span>
                  </div>
                  <div className="bg-surface-container-low rounded-lg p-2.5">
                    <span className="font-label-sm text-on-surface-variant block">
                      Movimiento
                    </span>
                    {" "}
                    <span className="font-title-md text-on-surface font-bold">
{isDemo ? "2 d/sem" : profile.active === 1 ? "Activa" : "Baja"}
</span>
                    {" "}
                    <span className="font-label-sm text-primary block text-[11px] font-medium">
{isDemo || profile.active !== 1 ? "Ampliable" : "Constante"}
</span>
                  </div>
                </div>
              </div>
              {/* Acceso directo a la guía de medición */}
              <button className="relative bg-surface-container rounded-xl overflow-hidden p-space-md flex items-center justify-between gap-space-sm shadow-sm text-left hover:shadow-md transition-shadow group" onClick={openMeasureGuide} type="button">
                <div className="flex flex-col z-10">
                  <span className="font-label-sm font-semibold text-primary uppercase">
                    Guía de acompañamiento
                  </span>
                  <h3 className="font-title-md text-title-md text-on-surface font-semibold mt-1">
                    Aprende a medir tu tensión en calma
                  </h3>
                  <span className="font-label-md text-primary font-semibold mt-2 flex items-center gap-1">
                    Ver los 5 pasos
                    <span className="material-symbols-outlined text-[16px] group-hover:translate-x-1 transition-transform">
                      arrow_forward
                    </span>
                  </span>
                </div>
                <div className="w-24 h-24 rounded-lg overflow-hidden shrink-0 shadow-inner">
                  <img alt="" className="w-full h-full object-cover" src={IMAGES.measuring} />
                </div>
              </button>
            </section>
          </div>
          {/* INFLUENCE FACTORS SECTION */}
          <section className="mt-space-xl">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 mb-space-md">
              <div>
                <span className="font-label-sm uppercase font-semibold text-primary tracking-wider">
                  Desglose transparente
                </span>
                {" "}
                <h2 className="font-headline-md text-headline-md text-on-surface font-semibold">
                  Qué influyó en tu resultado
                </h2>
              </div>
              <p className="font-body-md text-on-surface-variant text-sm max-w-md">
                Los factores que más movieron tu resultado.
              </p>
            </div>
            {/* 3 Factor Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
{isDemo ? (
<>
              {/* Factor 1: Presión Arterial */}
              <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-space-sm">
                    <div className="w-10 h-10 rounded-xl bg-tertiary-fixed flex items-center justify-center text-on-tertiary-fixed">
                      <span className="material-symbols-outlined text-[24px]">
                        speed
                      </span>
                    </div>
                    {" "}
                    <span className="px-2.5 py-1 rounded-full bg-error-container text-on-error-container font-label-sm font-semibold">
                      Mayor peso en cálculo
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-1">
                    <h3 className="font-headline-sm text-headline-sm font-bold text-on-surface">
                      Presión arterial
                    </h3>
                    {" "}
                    <span className="font-label-md text-tertiary font-bold">
                      135/85 mmHg
                    </span>
                  </div>
                  <p className="font-body-md text-body-md text-on-surface-variant mt-2 leading-relaxed">
                    Fue lo que más pesó. Acercarla a 120/80 protege tus arterias.
                  </p>
                </div>
                <div className="mt-space-md pt-space-sm border-t border-surface-container flex items-center justify-between text-on-surface font-label-sm">
                  <span className="text-on-surface-variant">
                    Impacto en la reducción:
                  </span>
                  {" "}
                  <span className="text-secondary font-semibold flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">
                      trending_down
                    </span>
                    {" "}Hasta -6%
                  </span>
                </div>
              </div>
              {/* Factor 2: Actividad Física */}
              <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-space-sm">
                    <div className="w-10 h-10 rounded-xl bg-secondary-container flex items-center justify-center text-on-secondary-container">
                      <span className="material-symbols-outlined text-[24px]">
                        directions_walk
                      </span>
                    </div>
                    {" "}
                    <span className="px-2.5 py-1 rounded-full bg-surface-container text-primary font-label-sm font-semibold">
                      Frecuencia moderada
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-1">
                    <h3 className="font-headline-sm text-headline-sm font-bold text-on-surface">
                      Actividad física
                    </h3>
                    {" "}
                    <span className="font-label-md text-secondary font-bold">
                      2 sesiones / sem
                    </span>
                  </div>
                  <p className="font-body-md text-body-md text-on-surface-variant mt-2 leading-relaxed">
                    Moverte con regularidad ayuda a relajar tus vasos sanguíneos.
                  </p>
                </div>
                <div className="mt-space-md pt-space-sm border-t border-surface-container flex items-center justify-between text-on-surface font-label-sm">
                  <span className="text-on-surface-variant">
                    Margen de mejora:
                  </span>
                  {" "}
                  <span className="text-primary font-semibold flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">
                      add_circle
                    </span>
                    {" "}+30 min/día
                  </span>
                </div>
              </div>
              {/* Factor 3: Peso e IMC */}
              <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-space-sm">
                    <div className="w-10 h-10 rounded-xl bg-primary-fixed flex items-center justify-center text-on-primary-fixed">
                      <span className="material-symbols-outlined text-[24px]">
                        balance
                      </span>
                    </div>
                    {" "}
                    <span className="px-2.5 py-1 rounded-full bg-surface-container text-on-surface-variant font-label-sm font-semibold">
                      Zona de balance
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-1">
                    <h3 className="font-headline-sm text-headline-sm font-bold text-on-surface">
                      Peso e IMC
                    </h3>
                    {" "}
                    <span className="font-label-md text-on-surface font-bold">
                      26.4 kg/m²
                    </span>
                  </div>
                  <p className="font-body-md text-body-md text-on-surface-variant mt-2 leading-relaxed">
                    Un peso equilibrado le quita trabajo a tu corazón.
                  </p>
                </div>
                <div className="mt-space-md pt-space-sm border-t border-surface-container flex items-center justify-between text-on-surface font-label-sm">
                  <span className="text-on-surface-variant">
                    Efecto en tensión:
                  </span>
                  {" "}
                  <span className="text-secondary font-semibold flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">
                      check_circle
                    </span>
                    {" "}Estable
                  </span>
                </div>
              </div>
</>
) : (
<ShapFactorCards factors={analysis.shap?.top_factors || []} />
)}
            </div>
          </section>
          {/* RECOMMENDATIONS FOR YOU SECTION */}
          <section className="mt-space-xl scroll-mt-28" ref={planRef}>
            <div className="mb-space-md">
              <span className="font-label-sm uppercase font-semibold text-secondary tracking-wider">
                Plan de bienestar activo
              </span>
              <h2 className="font-headline-md text-headline-md text-on-surface font-semibold">
                Recomendaciones para ti
              </h2>
              <p className="font-body-lg text-body-lg text-on-surface-variant mt-1">
                Pequeñas acciones que protegen tu corazón.
              </p>
            </div>
            {!isDemo && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter mb-space-lg">
                <RagRecommendations
                  rag={recommendations}
                  loading={recommendationsLoading}
                  error={recommendationsError}
                  onRequest={onRequestRecommendations}
                />
              </div>
            )}
            <WellnessPlan activeTab={planTab} onTabChange={setPlanTab} />
          </section>
                    {/* SCIENTIFIC SOURCES ACCORDION SECTION */}
          <section className="mt-space-xl mb-32">
            <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-md overflow-hidden">
              <button aria-controls="sources-content" aria-expanded={sourcesOpen} className="w-full flex items-center justify-between text-left py-1 cursor-pointer select-none group" id="toggle-sources-btn" onClick={() => setSourcesOpen((value) => !value)} type="button">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-surface-container flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-on-primary transition-colors">
                    <span className="material-symbols-outlined text-[20px]">
                      menu_book
                    </span>
                  </div>
                  <div>
                    <span className="font-headline-sm text-title-md text-on-surface font-semibold block">
                      Consultar fuentes y bases científicas
                    </span>
                    {" "}
                    <span className="font-label-sm text-on-surface-variant">
                      Evidencia médica internacional y consensos cardiovasculares aplicados
                    </span>
                  </div>
                </div>
                {" "}
                <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-transform duration-300" id="sources-chevron" style={{ transform: sourcesOpen ? "rotate(180deg)" : "rotate(0deg)" }}>
                  expand_more
                </span>
              </button>
              {/* Collapsible Content */}
              <div className={`${sourcesOpen ? "" : "hidden "}mt-space-md pt-space-md border-t border-surface-container`} id="sources-content">
{isDemo ? (
<>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md font-body-md text-on-surface-variant">
                  <div className="space-y-3">
                    <div className="flex items-start gap-2">
                      <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
                        bookmark
                      </span>
                      {" "}
                      <div>
                        <strong className="text-on-surface font-medium block">
                          Guía Europea de Prevención Cardiovascular (ESC 2021)
                        </strong>
                        {" "}
                        <p className="text-xs text-on-surface-variant">
                          Modelos SCORE2/SCORE2-OP para cálculo de riesgo acumulado y estratificación en poblaciones europeas e hispanohablantes.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
                        bookmark
                      </span>
                      {" "}
                      <div>
                        <strong className="text-on-surface font-medium block">
                          AHA/ACC Guideline for the Prevention of Hypertension
                        </strong>
                        {" "}
                        <p className="text-xs text-on-surface-variant">
                          Evidencia de reducción de morbimortalidad vascular mediante metas de presión sistólica inferiores a 130 mmHg con estilo de vida.
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-start gap-2">
                      <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
                        bookmark
                      </span>
                      {" "}
                      <div>
                        <strong className="text-on-surface font-medium block">
                          Consenso Interamericano de Cardiología (SIAC)
                        </strong>
                        {" "}
                        <p className="text-xs text-on-surface-variant">
                          Lineamientos de salud cardiovascular enfocados en intervención comunitaria, adherencia dietética DASH y autocuidado empático.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
                        bookmark
                      </span>
                      {" "}
                      <div>
                        <strong className="text-on-surface font-medium block">
                          Organización Mundial de la Salud (OMS 2023)
                        </strong>
                        {" "}
                        <p className="text-xs text-on-surface-variant">
                          Informe global sobre hipertensión: la carrera contra un asesino silencioso y las intervenciones efectivas de bajo costo.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-surface-container-low rounded-lg text-xs text-on-surface-variant flex items-center justify-between">
                  <span>
                    Algoritmo de cálculo verificado clínicamente en Mayo 2025.
                  </span>
                  {" "}
                  <span className="font-semibold text-primary">
                    Versión de protocolo: v4.2.1-CLINICAL
                  </span>
                </div>
</>
) : (
<>
<RagSources rag={recommendations} />
<div className="mt-4 p-3 bg-surface-container-low rounded-lg text-xs text-on-surface-variant flex items-center justify-between">
<span>
Fuentes recuperadas por el módulo RAG de PULSO.
</span>
<span className="font-semibold text-primary">
{`Modelo PULSO ${analysis.prediction.model_version} · umbral ${analysis.prediction.threshold}`}
</span>
</div>
</>
)}
              </div>
            </div>
          </section>
        </div>
        {/* FLOATING / FIXED ACTION DOCK (STICKY BOTTOM BAR) */}
        <aside className="fixed bottom-0 left-0 right-0 z-40 bg-surface-container-lowest/95 backdrop-blur-md border-t border-outline-variant/30 py-3 shadow-[0_-4px_16px_rgba(23,43,77,0.08)]">
          <div className="max-w-7xl mx-auto px-gutter flex flex-col sm:flex-row items-center justify-between gap-3">
            {/* Left info chip */}
            <div className="hidden md:flex items-center gap-2 whitespace-nowrap">
              <span className="w-3 h-3 rounded-full bg-secondary"></span>
              {" "}
              <span className="font-label-md text-on-surface font-medium">
                {`Clara Méndez · ${percent}%`}
              </span>
              {" "}
              <span className="text-outline text-label-sm">
                •
              </span>
              {" "}
              <span className="font-label-sm text-on-surface-variant">
                Evaluación lista para almacenar
              </span>
            </div>
            {/* Action Buttons Cluster */}
            <div className="flex items-center gap-space-sm w-full sm:w-auto justify-end">
              {/* Edit parameters (Subtle ghost / contour) */}
              <a className="flex-1 sm:flex-initial whitespace-nowrap px-4 py-2.5 rounded-xl border border-outline-variant/60 hover:bg-surface-container-low text-on-surface font-label-md font-medium transition-colors text-center flex items-center justify-center gap-1.5" data-path="evaluacion" href="#" onClick={(event) => handleLink(event, "evaluacion")}>
                <span className="material-symbols-outlined text-[18px]">
                  edit_note
                </span>
                {" "}
                <span>
                  Editar mis datos
                </span>
              </a>
              {/* Explore Simulation What-if (Secondary Teal #14B8A6) */}
              <a className="flex-1 sm:flex-initial whitespace-nowrap px-4 py-2.5 rounded-xl bg-secondary hover:bg-secondary/90 text-on-secondary font-label-md font-semibold transition-all shadow-sm flex items-center justify-center gap-1.5 hover:-translate-y-0.5" data-path="simulacion" href="#" onClick={(event) => handleLink(event, "simulacion")}>
                <span className="material-symbols-outlined text-[18px]">
                  science
                </span>
                {" "}
                <span>
                  Explorar simulación
                </span>
              </a>
              {/* Save Evaluation (Primary Blue #2563EB) */}
              <button className={`flex-1 sm:flex-initial whitespace-nowrap px-5 py-2.5 rounded-xl ${saved ? "bg-secondary text-on-secondary" : "bg-primary-container hover:bg-primary"} text-on-primary font-label-md font-semibold transition-all shadow-md flex items-center justify-center gap-1.5 hover:-translate-y-0.5`} id="save-eval-btn" onClick={() => setSaved(true)} type="button">
                <span className="material-symbols-outlined text-[18px]" id="save-icon">
{saved ? "check_circle" : "bookmark_add"}
</span>
                {" "}
                <span id="save-label">
{saved ? "¡Guardado con éxito!" : "Guardar en mi historial"}
</span>
              </button>
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}

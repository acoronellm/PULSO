import { useEffect, useRef, useState } from "react";

import RagRecommendations, { RagSources } from "../components/RagRecommendations";
import WellnessPlan from "../components/WellnessPlan";
import {
  featureIcon,
  featureName,
  featureValue,
  formatProbability,
  formatThreshold,
  genderLabel,
} from "../utils/health";
import { IMAGES } from "../utils/images";
import {
  MODEL_DISCLAIMER,
  classLabel,
  classificationMessage,
} from "../utils/interpretation";

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

// Tarjetas con las características que más contribuyeron a la salida del modelo (SHAP)
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
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-primary-fixed text-primary">
              <span className="material-symbols-outlined text-[24px]">
                {featureIcon(factor.feature)}
              </span>
            </div>
            <span className="px-2.5 py-1 rounded-full font-label-sm font-semibold bg-surface-container text-primary">
              {up ? "Aumentó la salida del modelo" : "Disminuyó la salida del modelo"}
            </span>
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <h3 className="font-headline-sm text-headline-sm font-bold text-on-surface">
              {featureName(factor.feature)}
            </h3>
            <span className="font-label-md font-bold text-primary">
              {featureValue(factor.feature, factor.value)}
            </span>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant mt-2 leading-relaxed">
            Esta característica contribuyó a {up ? "aumentar" : "disminuir"} la probabilidad estimada por el modelo. No implica una relación causal médica.
          </p>
        </div>
        <div className="mt-space-md pt-space-sm border-t border-surface-container flex items-center justify-between text-on-surface font-label-sm">
          <span className="text-on-surface-variant">
            Contribución en el modelo:
          </span>
          <span className="text-primary font-semibold flex items-center gap-1">
            <span className="material-symbols-outlined text-[16px]">
              {up ? "trending_up" : "trending_down"}
            </span>
            {index === 0 ? "Mayor contribución" : `Posición ${index + 1}`}
          </span>
        </div>
      </div>
    );
  });
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
  const { prediction } = analysis;
  const probability = formatProbability(prediction.probability);
  const threshold = formatThreshold(prediction.threshold);
  const [reportDate] = useState(() => formatDate(new Date()));
  // El corazón ocupa de y=2 a y=175 en el SVG
  const liquidY = Math.max(2, 175 - prediction.probability * 173);

  const [motionActive, setMotionActive] = useState(true);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [planTab, setPlanTab] = useState("recetas");
  const planRef = useRef(null);
  const heartRef = useRef(null);
  const haloRef = useRef(null);
  const haloOuterRef = useRef(null);

  // Animación de latido suave (se puede desactivar por accesibilidad)
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
      <div className="relative w-full max-w-7xl mx-auto px-gutter py-space-md">
        <div className="absolute top-10 left-1/2 -translate-x-1/2 w-96 h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none -z-10"></div>

        <header className="flex flex-col md:flex-row md:items-end justify-between gap-space-md mb-space-xl">
          <div className="flex flex-col">
            <div className="flex items-center gap-2 mb-space-xs">
              <span className="px-2.5 py-0.5 rounded-full bg-surface-container text-primary font-label-sm uppercase tracking-wider font-semibold">
                {`Modelo PULSO ${prediction.model_version}`}
              </span>
              <span className="text-outline text-label-sm">
                •
              </span>
              <span className="text-on-surface-variant font-label-md flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px] text-secondary">
                  calendar_today
                </span>
                {reportDate}
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
              Resultado del modelo PULSO
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant mt-1">
              {`Perfil evaluado: ${genderLabel(profile.gender)} · ${profile.age_years} años`}
            </p>
          </div>
          <div className="flex items-center gap-space-sm bg-surface-container-lowest p-1.5 rounded-xl shadow-sm border border-outline-variant/30">
            <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-all font-label-md" onClick={() => setMotionActive((value) => !value)} type="button">
              <span className={`material-symbols-outlined text-[18px] ${motionActive ? "text-secondary" : "text-outline"}`}>
                {motionActive ? "pulse_alert" : "motion_photos_pause"}
              </span>
              <span>
                {motionActive ? "Animación activa" : "Animación pausada"}
              </span>
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter items-start">
          <section className="lg:col-span-7 flex flex-col bg-surface-container-lowest rounded-xl shadow-md p-space-lg relative overflow-hidden">
            <div className="flex items-center justify-between z-10">
              <span className="font-label-md font-semibold text-secondary uppercase tracking-wider">
                Probabilidad estimada
              </span>
              <span className="font-label-sm text-on-surface-variant bg-surface-container-low px-3 py-1 rounded-full">
                Clase cardio = 1
              </span>
            </div>

            <div className="relative flex flex-col items-center justify-center my-space-md py-4">
              <div className="absolute w-64 h-64 rounded-full bg-secondary-fixed/40 transition-transform duration-700 ease-out transform scale-110 pointer-events-none -z-0" ref={haloRef}></div>
              <div className="absolute w-80 h-80 rounded-full bg-surface-variant/40 transition-transform duration-1000 ease-out transform scale-125 pointer-events-none -z-0" ref={haloOuterRef}></div>
              <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center transition-transform duration-300" ref={heartRef}>
                <svg aria-hidden="true" className="w-full h-full drop-shadow-lg overflow-visible" viewBox="0 0 200 185" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <clipPath id="heart-clip-shape">
                      <path d="M100,175 C96,170 18,108 8,62 C0,26 30,2 66,2 C83,2 94,14 100,22 C106,14 117,2 134,2 C170,2 200,26 192,62 C182,108 104,170 100,175 Z"></path>
                    </clipPath>
                    <linearGradient id="heartLiquidGradient" x1="0%" x2="0%" y1="100%" y2="0%">
                      <stop offset="0%" stopColor="#006b5f"></stop>
                      <stop offset="60%" stopColor="#2563eb"></stop>
                      <stop offset="100%" stopColor="#4fdbc8"></stop>
                    </linearGradient>
                    <filter height="140%" id="softGlow" width="140%" x="-20%" y="-20%">
                      <feGaussianBlur result="blur" stdDeviation="4"></feGaussianBlur>
                      <feComposite in="SourceGraphic" in2="blur" operator="over"></feComposite>
                    </filter>
                  </defs>
                  <path className="fill-surface-container" d="M100,175 C96,170 18,108 8,62 C0,26 30,2 66,2 C83,2 94,14 100,22 C106,14 117,2 134,2 C170,2 200,26 192,62 C182,108 104,170 100,175 Z"></path>
                  <g clipPath="url(#heart-clip-shape)">
                    <rect className="fill-surface-container-high" height="185" width="200" x="0" y="0"></rect>
                    <g className="transition-all duration-1000 ease-in-out">
                      <rect fill="url(#heartLiquidGradient)" height={192 - liquidY} width="200" x="0" y={liquidY}></rect>
                      <path d={`M 0,${liquidY} Q 50,${liquidY - 6} 100,${liquidY} T 200,${liquidY} L 200,190 L 0,190 Z`} fill="url(#heartLiquidGradient)" opacity="0.95"></path>
                    </g>
                  </g>
                  <path d="M100,175 C96,170 18,108 8,62 C0,26 30,2 66,2 C83,2 94,14 100,22 C106,14 117,2 134,2 C170,2 200,26 192,62 C182,108 104,170 100,175 Z" fill="none" opacity="0.75" stroke="#ffffff" strokeWidth="3"></path>
                  <path d="M 40,82 L 72,82 L 82,65 L 94,102 L 106,54 L 118,88 L 126,82 L 160,82" fill="none" filter="url(#softGlow)" opacity="0.85" stroke="#ffffff" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none select-none">
                  <span className="font-headline-sm text-headline-sm font-semibold tracking-wide text-on-surface uppercase -mb-1">
                    Probabilidad
                  </span>
                  <div className="flex items-baseline">
                    <span className="font-display-hero text-[52px] sm:text-[60px] leading-none font-bold text-on-surface tracking-tighter drop-shadow-sm" data-testid="probability-value">
                      {probability}
                    </span>
                    <span className="font-headline-md text-headline-md text-primary font-bold ml-0.5">
                      %
                    </span>
                  </div>
                  <span className="font-label-sm text-label-sm text-on-surface-variant font-medium bg-surface-container-lowest/80 backdrop-blur px-2.5 py-0.5 rounded-full shadow-sm mt-1">
                    {classLabel(prediction.classification)}
                  </span>
                </div>
              </div>
            </div>

            {/* Probabilidad frente al umbral de clasificación del modelo */}
            <div className="w-full flex flex-col pt-space-xs px-space-sm sm:px-space-md">
              <div className="flex justify-between items-center text-on-surface-variant font-label-sm mb-10 font-medium">
                <span>
                  0 %
                </span>
                <span>
                  100 %
                </span>
              </div>
              <div className="relative w-full h-4 rounded-full shadow-inner bg-surface-container overflow-visible">
                <div className="h-full rounded-full bg-primary-container" style={{ width: `${prediction.probability * 100}%` }}></div>
                <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 flex flex-col items-center z-20 pointer-events-none" style={{ left: `${prediction.probability * 100}%` }}>
                  <div className="w-5 h-5 rounded-full bg-surface-container-lowest shadow-md border-2 border-primary flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                  </div>
                  <div className="absolute -top-8 whitespace-nowrap px-2 py-0.5 rounded-md bg-on-surface text-surface-bright font-label-sm font-semibold shadow-sm">
                    {`Probabilidad: ${probability} %`}
                  </div>
                </div>
                <div className="absolute -top-1.5 -bottom-1.5 w-0.5 bg-on-surface-variant z-10" style={{ left: `${prediction.threshold * 100}%` }}></div>
              </div>
              <div className="relative h-6 mt-2">
                <span className="absolute -translate-x-1/2 whitespace-nowrap text-on-surface-variant font-label-sm font-semibold" style={{ left: `${prediction.threshold * 100}%` }}>
                  {`Umbral: ${threshold} %`}
                </span>
              </div>
            </div>

            <div className="mt-space-md bg-surface-container-low rounded-xl p-space-md flex items-start gap-space-sm">
              <span className="material-symbols-outlined text-primary text-[22px] shrink-0 mt-0.5">
                lightbulb
              </span>
              <div className="flex flex-col">
                <h2 className="font-title-md text-title-md text-on-surface font-semibold">
                  ¿Qué significa este porcentaje?
                </h2>
                <p className="font-body-md text-body-md text-on-surface-variant mt-1">
                  Es la salida del clasificador XGBoost para la clase cardio = 1, que en los datos de entrenamiento representa la presencia de enfermedad cardiovascular registrada. No es un pronóstico ni un nivel de riesgo clínico.
                </p>
              </div>
            </div>
          </section>

          <section className="lg:col-span-5 flex flex-col gap-space-md">
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
              <p className="font-body-lg text-body-lg text-on-surface font-medium leading-relaxed" data-testid="classification-message">
                {classificationMessage(prediction)}
              </p>
              <div className="mt-space-md bg-surface-container-high/60 rounded-xl p-3.5 flex items-start gap-2.5 text-on-surface-variant">
                <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">
                  verified_user
                </span>
                <p className="font-label-sm text-label-sm leading-snug" data-testid="model-disclaimer">
                  {MODEL_DISCLAIMER}
                </p>
              </div>
            </div>

            <div className="bg-surface-container-lowest rounded-xl shadow-md p-space-md">
              <span className="font-label-sm uppercase font-semibold text-on-surface-variant tracking-wider block mb-space-xs">
                Datos evaluados
              </span>
              <div className="grid grid-cols-3 gap-2 text-center">
                {[
                  ["Presión art.", `${profile.ap_hi}/${profile.ap_lo}`, "mmHg"],
                  ["IMC", Number(profile.bmi).toFixed(1), "kg/m²"],
                  ["Actividad", profile.active === 1 ? "Sí" : "No", "regular"],
                ].map(([label, value, unit]) => (
                  <div className="bg-surface-container-low rounded-lg p-2.5" key={label}>
                    <span className="font-label-sm text-on-surface-variant block">
                      {label}
                    </span>
                    <span className="font-title-md text-on-surface font-bold">
                      {value}
                    </span>
                    <span className="font-label-sm text-on-surface-variant block text-[11px] font-medium">
                      {unit}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <button className="relative bg-surface-container rounded-xl overflow-hidden p-space-md flex items-center justify-between gap-space-sm shadow-sm text-left hover:shadow-md transition-shadow group" onClick={openMeasureGuide} type="button">
              <div className="flex flex-col z-10">
                <span className="font-label-sm font-semibold text-primary uppercase">
                  Guía educativa
                </span>
                <h3 className="font-title-md text-title-md text-on-surface font-semibold mt-1">
                  Aprende a medir tu presión en calma
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

        <section className="mt-space-xl">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 mb-space-md">
            <div>
              <span className="font-label-sm uppercase font-semibold text-primary tracking-wider">
                Explicación SHAP
              </span>
              <h2 className="font-headline-md text-headline-md text-on-surface font-semibold">
                Qué influyó en la salida del modelo
              </h2>
            </div>
            <p className="font-body-md text-on-surface-variant text-sm max-w-md">
              Características que más contribuyeron a la probabilidad estimada, sin atribuir causalidad médica.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            <ShapFactorCards factors={analysis.shap?.top_factors || []} />
          </div>
        </section>

        <section className="mt-space-xl scroll-mt-28" ref={planRef}>
          <div className="mb-space-md">
            <span className="font-label-sm uppercase font-semibold text-secondary tracking-wider">
              Información preventiva
            </span>
            <h2 className="font-headline-md text-headline-md text-on-surface font-semibold">
              Recomendaciones educativas
            </h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant mt-1">
              Información preventiva respaldada por documentación. No reemplaza la orientación de un profesional de la salud.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter mb-space-lg">
            <RagRecommendations
              error={recommendationsError}
              loading={recommendationsLoading}
              onRequest={onRequestRecommendations}
              rag={recommendations}
            />
          </div>
          <WellnessPlan activeTab={planTab} onTabChange={setPlanTab} />
        </section>

        <section className="mt-space-xl mb-32">
          <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-md overflow-hidden">
            <button aria-controls="sources-content" aria-expanded={sourcesOpen} className="w-full flex items-center justify-between text-left py-1 cursor-pointer select-none group" onClick={() => setSourcesOpen((value) => !value)} type="button">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-surface-container flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-on-primary transition-colors">
                  <span className="material-symbols-outlined text-[20px]">
                    menu_book
                  </span>
                </div>
                <div>
                  <span className="font-headline-sm text-title-md text-on-surface font-semibold block">
                    Fuentes documentales consultadas
                  </span>
                  <span className="font-label-sm text-on-surface-variant">
                    Documentos recuperados por el módulo RAG para las recomendaciones
                  </span>
                </div>
              </div>
              <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-transform duration-300" style={{ transform: sourcesOpen ? "rotate(180deg)" : "rotate(0deg)" }}>
                expand_more
              </span>
            </button>
            <div className={`${sourcesOpen ? "" : "hidden "}mt-space-md pt-space-md border-t border-surface-container`} id="sources-content">
              <RagSources rag={recommendations} />
              <div className="mt-4 p-3 bg-surface-container-low rounded-lg text-xs text-on-surface-variant flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span>
                  Las fuentes provienen de la respuesta del módulo RAG.
                </span>
                <span className="font-semibold text-primary">
                  {`Modelo PULSO ${prediction.model_version} · umbral ${threshold} %`}
                </span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <aside className="fixed bottom-0 left-0 right-0 z-40 bg-surface-container-lowest/95 backdrop-blur-md border-t border-outline-variant/30 py-3 shadow-[0_-4px_16px_rgba(23,43,77,0.08)]">
        <div className="max-w-7xl mx-auto px-gutter flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="hidden md:flex items-center gap-2 whitespace-nowrap">
            <span className="w-3 h-3 rounded-full bg-primary"></span>
            <span className="font-label-md text-on-surface font-medium">
              {`Probabilidad estimada: ${probability} % · ${classLabel(prediction.classification)}`}
            </span>
          </div>
          <div className="flex items-center gap-space-sm w-full sm:w-auto justify-end">
            <a className="flex-1 sm:flex-initial whitespace-nowrap px-4 py-2.5 rounded-xl border border-outline-variant/60 hover:bg-surface-container-low text-on-surface font-label-md font-medium transition-colors text-center flex items-center justify-center gap-1.5" href="#" onClick={(event) => handleLink(event, "evaluacion")}>
              <span className="material-symbols-outlined text-[18px]">
                edit_note
              </span>
              <span>
                Editar mis datos
              </span>
            </a>
            <a className="flex-1 sm:flex-initial whitespace-nowrap px-4 py-2.5 rounded-xl bg-primary-container hover:bg-primary text-on-primary font-label-md font-semibold transition-all shadow-sm flex items-center justify-center gap-1.5 hover:-translate-y-0.5" href="#" onClick={(event) => handleLink(event, "simulacion")}>
              <span className="material-symbols-outlined text-[18px]">
                science
              </span>
              <span>
                Simular escenarios
              </span>
            </a>
          </div>
        </div>
      </aside>
    </main>
  );
}

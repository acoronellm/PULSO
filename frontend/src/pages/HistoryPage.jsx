import { useState } from "react";

export default function HistoryPage({ onNavigate }) {
  const [isEmpty, setIsEmpty] = useState(false);

  return (
    <main className="w-full pt-24 bg-surface min-h-[calc(100vh-140px)]">
      <div className="flex flex-col w-full">
        <div className="w-full max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-surface-container-lowest p-6 sm:p-8 rounded-2xl shadow-sm relative overflow-hidden">
            <div className="absolute -right-16 -top-16 w-64 h-64 bg-mint-vitality-subtle/50 rounded-full blur-3xl pointer-events-none"></div>
            <div className="absolute right-48 -bottom-20 w-48 h-48 bg-indigo-metric-subtle/60 rounded-full blur-2xl pointer-events-none"></div>
            <div className="relative z-10 space-y-2">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-mint-vitality-subtle text-secondary">
                  <span className="w-1.5 h-1.5 rounded-full bg-mint-vitality mr-1.5 animate-pulse"></span>
                  {" "}Monitoreo activo
                </span>
                {" "}
                <span className="text-text-muted text-label-sm font-label-sm">
                  • Actualizado hace 3 días
                </span>
              </div>
              <h1 className="text-headline-lg font-headline-lg text-text-primary tracking-tight">
                Hola de nuevo, Clara Méndez
              </h1>
              <p className="text-body-lg font-body-lg text-text-secondary max-w-xl">
                Llevas{" "}
                <span className="font-headline-sm text-primary font-bold">
                  3 evaluaciones completadas
                </span>
                . Tu constancia refleja una evolución muy positiva en tu bienestar cardiovascular.
              </p>
            </div>
            <div className="relative z-10 flex flex-wrap items-center gap-3">
              <button className="inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-surface-container hover:bg-surface-container-high text-text-secondary hover:text-text-primary transition-all text-label-md font-label-md shadow-sm" id="toggleEmptyStateBtn" onClick={() => setIsEmpty((value) => !value)} type="button">
                <span className="material-symbols-outlined text-[18px]">
                  visibility
                </span>
                {" "}
                <span id="toggleEmptyText">
{isEmpty ? "Ver datos con historial" : "Simular nuevo usuario"}
</span>
              </button>
              {" "}
              <button className="inline-flex items-center gap-2.5 px-6 py-3 rounded-xl bg-primary-container text-on-primary hover:bg-primary transition-all shadow-md hover:shadow-lg active:scale-95 text-label-md font-label-md group" onClick={() => onNavigate("evaluacion")} type="button">
                <span className="material-symbols-outlined text-[20px] transition-transform group-hover:rotate-90">
                  add_circle
                </span>
                {" "}
                <span>
                  + Nueva evaluación
                </span>
              </button>
            </div>
          </div>
          <div className={`${isEmpty ? "hidden " : ""}space-y-8 transition-opacity duration-300`} id="dataFilledView">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              <div className="p-5 rounded-2xl bg-surface-card shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between group">
                <div className="absolute inset-x-0 top-0 h-1.5 bg-primary-container"></div>
                <div className="flex items-center justify-between">
                  <span className="text-label-md font-label-md text-text-secondary">
                    Última estimación
                  </span>
                  {" "}
                  <div className="w-10 h-10 rounded-xl bg-primary-fixed flex items-center justify-center text-primary">
                    <span className="material-symbols-outlined text-[20px]">
                      monitor_heart
                    </span>
                  </div>
                </div>
                <div className="mt-4 mb-2">
                  <div className="flex items-baseline gap-1">
                    <span className="text-metric-display font-metric-display text-text-primary">
                      28
                    </span>
                    {" "}
                    <span className="text-headline-sm font-headline-sm text-text-secondary">
                      %
                    </span>
                  </div>
                </div>
                <div className="pt-2 flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-primary-fixed/60 text-primary">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary-container mr-1.5"></span>
                    {" "}Margen controlado
                  </span>
                  {" "}
                  <span className="text-label-sm font-label-sm text-text-muted">
                    24 May 2025
                  </span>
                </div>
              </div>
              <div className="p-5 rounded-2xl bg-surface-card shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between group">
                <div className="absolute inset-x-0 top-0 h-1.5 bg-mint-vitality"></div>
                <div className="flex items-center justify-between">
                  <span className="text-label-md font-label-md text-text-secondary">
                    Tendencia general
                  </span>
                  {" "}
                  <div className="w-10 h-10 rounded-xl bg-mint-vitality-subtle flex items-center justify-center text-mint-vitality">
                    <span className="material-symbols-outlined text-[20px]">
                      trending_down
                    </span>
                  </div>
                </div>
                <div className="mt-4 mb-2">
                  <div className="flex items-baseline gap-1">
                    <span className="text-metric-display font-metric-display text-mint-vitality">
                      -4
                    </span>
                    {" "}
                    <span className="text-headline-sm font-headline-sm text-mint-vitality">
                      %
                    </span>
                  </div>
                </div>
                <div className="pt-2 flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-mint-vitality-subtle text-secondary">
                    <span className="material-symbols-outlined text-[14px] mr-1">
                      check_circle
                    </span>
                    {" "}Progreso favorable
                  </span>
                  {" "}
                  <span className="text-label-sm font-label-sm text-text-muted">
                    vs. primer registro
                  </span>
                </div>
              </div>
              <div className="p-5 rounded-2xl bg-surface-card shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between group">
                <div className="absolute inset-x-0 top-0 h-1.5 bg-amber-warning"></div>
                <div className="flex items-center justify-between">
                  <span className="text-label-md font-label-md text-text-secondary">
                    Presión media
                  </span>
                  {" "}
                  <div className="w-10 h-10 rounded-xl bg-amber-warning-subtle flex items-center justify-center text-amber-warning">
                    <span className="material-symbols-outlined text-[20px]">
                      speed
                    </span>
                  </div>
                </div>
                <div className="mt-4 mb-2">
                  <div className="flex items-baseline gap-1">
                    <span className="text-headline-lg font-headline-lg text-text-primary">
                      135/85
                    </span>
                    {" "}
                    <span className="text-label-sm font-label-sm text-text-muted">
                      mmHg
                    </span>
                  </div>
                </div>
                <div className="pt-2 flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-amber-warning-subtle text-amber-warning">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-warning mr-1.5"></span>
                    {" "}En observación
                  </span>
                  {" "}
                  <span className="text-label-sm font-label-sm text-text-muted">
                    Ritmo estable
                  </span>
                </div>
              </div>
              <div className="p-5 rounded-2xl bg-surface-card shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between group">
                <div className="absolute inset-x-0 top-0 h-1.5 bg-indigo-metric"></div>
                <div className="flex items-center justify-between">
                  <span className="text-label-md font-label-md text-text-secondary">
                    Hábito más constante
                  </span>
                  {" "}
                  <div className="w-10 h-10 rounded-xl bg-indigo-metric-subtle flex items-center justify-center text-indigo-metric">
                    <span className="material-symbols-outlined text-[20px]">
                      directions_walk
                    </span>
                  </div>
                </div>
                <div className="mt-4 mb-2">
                  <div className="flex items-baseline gap-1">
                    <span className="text-headline-md font-headline-md text-text-primary">
                      5 días
                    </span>
                    {" "}
                    <span className="text-body-md font-body-md text-text-secondary">
                      / sem
                    </span>
                  </div>
                  <p className="text-body-md font-body-md text-text-muted truncate">
                    Caminatas moderadas
                  </p>
                </div>
                <div className="pt-2 flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-indigo-metric-subtle text-tertiary">
                    <span className="material-symbols-outlined text-[14px] mr-1">
                      military_tech
                    </span>
                    {" "}Objetivo cumplido
                  </span>
                  {" "}
                  <span className="text-label-sm font-label-sm text-text-muted">
                    100% meta
                  </span>
                </div>
              </div>
            </div>
            <div className="bg-surface-card rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-headline-md font-headline-md text-text-primary">
                      Evolución de estimación de riesgo
                    </h2>
                    {" "}
                    <span className="px-2 py-0.5 rounded-full text-label-sm font-label-sm bg-mint-vitality-subtle text-secondary font-medium">
                      Curva en descenso
                    </span>
                  </div>
                  <p className="text-body-md font-body-md text-text-secondary mt-1">
                    Seguimiento acumulado de tus mediciones periódicas realizadas en 2025.
                  </p>
                </div>
                <div className="flex items-center gap-3 bg-surface-container-low px-3 py-1.5 rounded-xl">
                  <div className="flex items-center gap-1.5 text-label-sm font-label-sm text-text-secondary">
                    <span className="w-2.5 h-2.5 rounded-full bg-primary-container"></span>
                    {" "}Estimación de riesgo
                  </div>
                  <div className="flex items-center gap-1.5 text-label-sm font-label-sm text-text-secondary">
                    <span className="w-2.5 h-2.5 rounded-full bg-mint-vitality"></span>
                    {" "}Rango meta (≤25%)
                  </div>
                </div>
              </div>
              <div className="relative w-full h-64 sm:h-72 bg-gradient-to-b from-surface-container-low/40 to-transparent rounded-xl p-4 flex flex-col justify-end">
                <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 700 220">
                  <defs>
                    <linearGradient id="areaGradient" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#0052d4" stopOpacity="0.25"></stop>
                      <stop offset="100%" stopColor="#0052d4" stopOpacity="0.0"></stop>
                    </linearGradient>
                    <linearGradient id="lineGradient" x1="0" x2="1" y1="0" y2="0">
                      <stop offset="0%" stopColor="#6366F1"></stop>
                      <stop offset="50%" stopColor="#0052d4"></stop>
                      <stop offset="100%" stopColor="#10B981"></stop>
                    </linearGradient>
                  </defs>
                  <line stroke="#E2E2E4" strokeDasharray="4 4" strokeWidth="1" x1="0" x2="700" y1="40" y2="40"></line>
                  <line stroke="#E2E2E4" strokeDasharray="4 4" strokeWidth="1" x1="0" x2="700" y1="100" y2="100"></line>
                  <line stroke="#E2E2E4" strokeDasharray="4 4" strokeWidth="1" x1="0" x2="700" y1="160" y2="160"></line>
                  <path d="M 100 60 Q 350 100 600 130 L 600 200 L 100 200 Z" fill="url(#areaGradient)"></path>
                  <path d="M 100 60 Q 350 100 600 130" fill="none" stroke="url(#lineGradient)" strokeLinecap="round" strokeWidth="4"></path>
                  <g className="cursor-pointer group" transform="translate(100, 60)">
                    <circle className="shadow-md" fill="#FFFFFF" r="9"></circle>
                    <circle fill="#6366F1" r="6"></circle>
                    <foreignObject className="overflow-visible pointer-events-none" height="45" width="90" x="-45" y="-55">
                      <div className="bg-inverse-surface text-on-primary text-center rounded-lg px-2 py-1 shadow-md">
                        <div className="text-label-sm font-label-sm font-bold">
                          32%
                        </div>
                        <div className="text-[10px] opacity-80">
                          10 Ene
                        </div>
                      </div>
                    </foreignObject>
                  </g>
                  <g className="cursor-pointer group" transform="translate(350, 95)">
                    <circle className="shadow-md" fill="#FFFFFF" r="9"></circle>
                    <circle fill="#0052d4" r="6"></circle>
                    <foreignObject className="overflow-visible pointer-events-none" height="45" width="90" x="-45" y="-55">
                      <div className="bg-inverse-surface text-on-primary text-center rounded-lg px-2 py-1 shadow-md">
                        <div className="text-label-sm font-label-sm font-bold">
                          30%
                        </div>
                        <div className="text-[10px] opacity-80">
                          15 Mar
                        </div>
                      </div>
                    </foreignObject>
                  </g>
                  <g className="cursor-pointer group" transform="translate(600, 130)">
                    <circle className="animate-pulse" fill="#A7F3D0" r="11"></circle>
                    <circle fill="#FFFFFF" r="8"></circle>
                    <circle fill="#10B981" r="5"></circle>
                    <foreignObject className="overflow-visible pointer-events-none" height="45" width="90" x="-45" y="-55">
                      <div className="bg-mint-vitality text-on-primary text-center rounded-lg px-2 py-1 shadow-md">
                        <div className="text-label-sm font-label-sm font-bold">
                          28% Actual
                        </div>
                        <div className="text-[10px] opacity-90">
                          24 May
                        </div>
                      </div>
                    </foreignObject>
                  </g>
                </svg>
                {" "}
                <div className="flex justify-between items-center px-12 pt-2 text-label-md font-label-md text-text-secondary">
                  <span className="text-center font-medium">
                    Enero 2025
                  </span>
                  {" "}
                  <span className="text-center font-medium">
                    Marzo 2025
                  </span>
                  {" "}
                  <span className="text-center font-semibold text-secondary">
                    Mayo 2025
                  </span>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 rounded-xl bg-surface-container-low text-text-secondary">
                <span className="material-symbols-outlined text-primary text-[20px] shrink-0 mt-0.5">
                  lightbulb
                </span>
                {" "}
                <p className="text-body-md font-body-md">
                  <span className="font-medium text-text-primary">
                    Nota sobre tu progreso:
                  </span>
                  {" "}La estimación orientativa refleja ajustes saludables en tus hábitos cotidianos (alimentación reducida en sodio y actividad aeróbica regular). No representa un diagnóstico, sino una brújula de constancia.
                </p>
              </div>
            </div>
            <div className="bg-surface-card rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h2 className="text-headline-md font-headline-md text-text-primary">
                    Historial detallado de registros
                  </h2>
                  <p className="text-body-md font-body-md text-text-secondary">
                    Accede a las métricas biométricas capturadas en cada periodo.
                  </p>
                </div>
                {" "}
                <span className="text-label-md font-label-md text-text-muted">
                  3 registros almacenados
                </span>
              </div>
              <div className="space-y-4">
                <div className="p-5 rounded-2xl bg-surface-container-lowest hover:bg-surface-container-low/50 transition-all shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-6 group">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-mint-vitality-subtle text-mint-vitality flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[24px]">
                        verified
                      </span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-title-md font-title-md text-text-primary">
                          Evaluación periódica Mayo
                        </span>
                        {" "}
                        <span className="px-2 py-0.5 rounded-full text-label-sm font-label-sm bg-mint-vitality-subtle text-secondary font-semibold">
                          Más reciente
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-label-md font-label-md text-text-secondary">
                        <span className="flex items-center gap-1">
                          <span className="material-symbols-outlined text-[16px]">
                            calendar_today
                          </span>
                          {" "}24 Mayo 2025
                        </span>
                        {" "}
                        <span>
                          •
                        </span>
                        {" "}
                        <span>
                          Doctor asignado: Dr. Arismendi
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-6 sm:gap-10 py-2 sm:py-0 border-y lg:border-none border-surface-container">
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        Estimación
                      </span>
                      {" "}
                      <span className="text-headline-sm font-headline-sm text-mint-vitality font-bold">
                        28%
                      </span>
                    </div>
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        Presión art.
                      </span>
                      {" "}
                      <span className="text-title-md font-title-md text-text-primary">
                        135/85
                      </span>
                    </div>
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        IMC
                      </span>
                      {" "}
                      <span className="text-title-md font-title-md text-text-primary">
                        26.4
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between lg:justify-end gap-3">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-indigo-metric-subtle text-tertiary">
                      Hábitos activos
                    </span>
                    {" "}
                    <button className="px-4 py-2.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-primary font-label-md text-label-md transition-colors flex items-center gap-1.5">
                      <span>
                        Ver detalle
                      </span>
                      {" "}
                      <span className="material-symbols-outlined text-[16px]">
                        arrow_forward
                      </span>
                    </button>
                  </div>
                </div>
                <div className="p-5 rounded-2xl bg-surface-container-lowest hover:bg-surface-container-low/50 transition-all shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-6 group">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary-fixed text-primary flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[24px]">
                        history_edu
                      </span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-title-md font-title-md text-text-primary">
                          Evaluación intermedia Marzo
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-label-md font-label-md text-text-secondary">
                        <span className="flex items-center gap-1">
                          <span className="material-symbols-outlined text-[16px]">
                            calendar_today
                          </span>
                          {" "}15 Marzo 2025
                        </span>
                        {" "}
                        <span>
                          •
                        </span>
                        {" "}
                        <span>
                          Autocontrol rutinario
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-6 sm:gap-10 py-2 sm:py-0 border-y lg:border-none border-surface-container">
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        Estimación
                      </span>
                      {" "}
                      <span className="text-headline-sm font-headline-sm text-primary font-bold">
                        30%
                      </span>
                    </div>
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        Presión art.
                      </span>
                      {" "}
                      <span className="text-title-md font-title-md text-text-primary">
                        138/88
                      </span>
                    </div>
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        IMC
                      </span>
                      {" "}
                      <span className="text-title-md font-title-md text-text-primary">
                        26.8
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between lg:justify-end gap-3">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-amber-warning-subtle text-amber-warning">
                      Leve tensión
                    </span>
                    {" "}
                    <button className="px-4 py-2.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-text-secondary hover:text-text-primary font-label-md text-label-md transition-colors flex items-center gap-1.5">
                      <span>
                        Ver detalle
                      </span>
                      {" "}
                      <span className="material-symbols-outlined text-[16px]">
                        arrow_forward
                      </span>
                    </button>
                  </div>
                </div>
                <div className="p-5 rounded-2xl bg-surface-container-lowest hover:bg-surface-container-low/50 transition-all shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-6 group">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-coral-alert-subtle text-coral-alert flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[24px]">
                        flag
                      </span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-title-md font-title-md text-text-primary">
                          Evaluación inicial Enero
                        </span>
                        {" "}
                        <span className="px-2 py-0.5 rounded-full text-label-sm font-label-sm bg-surface-container text-text-secondary">
                          Punto de partida
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-label-md font-label-md text-text-secondary">
                        <span className="flex items-center gap-1">
                          <span className="material-symbols-outlined text-[16px]">
                            calendar_today
                          </span>
                          {" "}10 Enero 2025
                        </span>
                        {" "}
                        <span>
                          •
                        </span>
                        {" "}
                        <span>
                          Primer ingreso a plataforma
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-6 sm:gap-10 py-2 sm:py-0 border-y lg:border-none border-surface-container">
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        Estimación
                      </span>
                      {" "}
                      <span className="text-headline-sm font-headline-sm text-coral-alert font-bold">
                        32%
                      </span>
                    </div>
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        Presión art.
                      </span>
                      {" "}
                      <span className="text-title-md font-title-md text-text-primary">
                        142/90
                      </span>
                    </div>
                    <div>
                      <span className="text-label-sm font-label-sm text-text-muted block">
                        IMC
                      </span>
                      {" "}
                      <span className="text-title-md font-title-md text-text-primary">
                        27.2
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between lg:justify-end gap-3">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-label-sm font-label-sm bg-coral-alert-subtle text-coral-alert">
                      Observación alta
                    </span>
                    {" "}
                    <button className="px-4 py-2.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-text-secondary hover:text-text-primary font-label-md text-label-md transition-colors flex items-center gap-1.5">
                      <span>
                        Ver detalle
                      </span>
                      {" "}
                      <span className="material-symbols-outlined text-[16px]">
                        arrow_forward
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className={`${isEmpty ? "" : "hidden "}space-y-8 transition-opacity duration-300`} id="dataEmptyView">
            <div className="bg-surface-card rounded-2xl p-10 sm:p-16 text-center max-w-2xl mx-auto shadow-sm space-y-6 relative overflow-hidden">
              <div className="absolute -left-12 -top-12 w-40 h-40 bg-coral-alert-subtle/50 rounded-full blur-2xl"></div>
              <div className="absolute -right-12 -bottom-12 w-40 h-40 bg-mint-vitality-subtle/50 rounded-full blur-2xl"></div>
              <div className="relative z-10 w-24 h-24 mx-auto rounded-3xl bg-mint-vitality-subtle text-mint-vitality flex items-center justify-center shadow-inner">
                <span className="material-symbols-outlined text-[54px] animate-pulse">
                  favorite
                </span>
              </div>
              <div className="relative z-10 space-y-3">
                <h2 className="text-headline-lg font-headline-lg text-text-primary">
                  ¡Tu corazón tiene una historia que contar!
                </h2>
                <p className="text-body-lg font-body-lg text-text-secondary leading-relaxed">
                  Aún no has registrado tu primera evaluación cardiovascular. Toma apenas 3 minutos contestar unas preguntas básicas sobre tus hábitos y valores de tensión para empezar tu gráfico de evolución.
                </p>
              </div>
              <div className="relative z-10 pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
                <button className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-primary-container text-on-primary font-label-md text-label-md shadow-md hover:bg-primary transition-all flex items-center justify-center gap-2" onClick={() => onNavigate("evaluacion")} type="button">
                  <span className="material-symbols-outlined text-[20px]">
                    play_arrow
                  </span>
                  {" "}Comenzar mi primera evaluación
                </button>
                {" "}
                <button className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-surface-container text-text-secondary hover:text-text-primary font-label-md text-label-md transition-colors">
                  Explorar cómo funciona
                </button>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-mint-vitality text-[22px]">
                health_and_safety
              </span>
              {" "}
              <h3 className="text-headline-sm font-headline-sm text-text-primary">
                Tips y recordatorios para tu próxima medición
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="p-6 rounded-2xl bg-mint-vitality-subtle/70 shadow-sm flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-surface-card text-mint-vitality flex items-center justify-center shrink-0 shadow-sm">
                  <span className="material-symbols-outlined text-[26px]">
                    nutrition
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-title-md font-title-md text-text-primary">
                      Nutrición cardioprotectora
                    </span>
                    {" "}
                    <span className="px-2 py-0.5 rounded-full text-label-sm font-label-sm bg-surface-card text-secondary font-semibold">
                      Consejo diario
                    </span>
                  </div>
                  <p className="text-body-md font-body-md text-text-secondary">
                    Prueba añadir semillas de chía o linaza y una pizca de cúrcuma a tus ensaladas o batidos. Su aporte de antioxidantes y ácidos grasos favorece la elasticidad de los vasos arteriales.
                  </p>
                </div>
              </div>
              <div className="p-6 rounded-2xl bg-indigo-metric-subtle/70 shadow-sm flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-surface-card text-indigo-metric flex items-center justify-center shrink-0 shadow-sm">
                  <span className="material-symbols-outlined text-[26px]">
                    airline_seat_recline_normal
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-title-md font-title-md text-text-primary">
                      Toma de presión fidedigna
                    </span>
                    {" "}
                    <span className="px-2 py-0.5 rounded-full text-label-sm font-label-sm bg-surface-card text-tertiary font-semibold">
                      Técnica recomendada
                    </span>
                  </div>
                  <p className="text-body-md font-body-md text-text-secondary">
                    Mide tu tensión siempre sentado, con la espalda apoyada, piernas sin cruzar y tras 5 minutos de reposo tranquilo. El brazalete debe colocarse justo a la altura del corazón.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

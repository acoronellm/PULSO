import { IMAGES } from "../utils/images";

// Contenido de ejemplo: más adelante lo personalizará el RAG según cada perfil
const TABS = [
  {
    id: "recetas",
    label: "Recetas",
    icon: "restaurant",
    accent: "text-secondary",
    tile: "bg-mint-vitality-subtle text-mint-vitality",
    image: IMAGES.food,
    title: "Cocina con menos sal",
    subtitle: "Sabor con hierbas, limón y especias.",
    items: [
      {
        icon: "eco",
        title: "Ensalada de garbanzos con limón",
        tags: ["15 min", "Alta en fibra"],
      },
      {
        icon: "set_meal",
        title: "Salmón al horno con verduras",
        tags: ["30 min", "Omega-3"],
      },
      {
        icon: "breakfast_dining",
        title: "Avena con frutos rojos",
        tags: ["10 min", "Sin azúcar añadida"],
      },
    ],
  },
  {
    id: "ejercicios",
    label: "Ejercicios",
    icon: "directions_run",
    accent: "text-primary",
    tile: "bg-indigo-metric-subtle text-indigo-metric",
    image: IMAGES.walking,
    title: "Muévete a tu ritmo",
    subtitle: "Meta orientativa: 150 min por semana.",
    items: [
      {
        icon: "directions_walk",
        title: "Caminata a paso ágil",
        tags: ["30 min", "5 días/sem"],
      },
      {
        icon: "directions_bike",
        title: "Bicicleta o elíptica suave",
        tags: ["20 min", "Bajo impacto"],
      },
      {
        icon: "self_improvement",
        title: "Estiramientos y respiración",
        tags: ["10 min", "Diario"],
      },
    ],
    note: "Si tu presión está muy elevada, consulta antes de hacer ejercicio intenso.",
  },
  {
    id: "medir",
    label: "Medir mi presión",
    icon: "monitor_heart",
    accent: "text-tertiary",
    tile: "bg-coral-alert-subtle text-coral-alert",
    image: IMAGES.measuring,
    title: "Mide en calma",
    subtitle: "Una buena toma da un dato confiable.",
    steps: [
      { icon: "chair", text: "Reposa 5 minutos sentado" },
      { icon: "no_drinks", text: "Sin café ni tabaco 30 min antes" },
      { icon: "airline_seat_recline_normal", text: "Espalda apoyada, pies en el suelo" },
      { icon: "back_hand", text: "Brazo a la altura del corazón" },
      { icon: "timer", text: "Dos tomas con 1 min de pausa" },
    ],
  },
];

const TAB_ACTIVE =
  "flex items-center gap-1.5 px-4 py-2 rounded-lg font-label-md font-semibold bg-surface-container-lowest text-primary shadow-sm transition-all";
const TAB_INACTIVE =
  "flex items-center gap-1.5 px-4 py-2 rounded-lg font-label-md text-on-surface-variant hover:text-on-surface transition-all";

export default function WellnessPlan({ activeTab, onTabChange }) {
  const tab = TABS.find((item) => item.id === activeTab) || TABS[0];

  return (
    <div className="flex flex-col gap-space-md">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
        <div className="inline-flex p-1 bg-surface-container-low rounded-xl self-start" role="tablist">
          {TABS.map((item) => (
            <button
              aria-selected={item.id === tab.id}
              className={item.id === tab.id ? TAB_ACTIVE : TAB_INACTIVE}
              key={item.id}
              onClick={() => onTabChange(item.id)}
              role="tab"
              type="button"
            >
              <span className="material-symbols-outlined text-[18px]">
                {item.icon}
              </span>
              {item.label}
            </button>
          ))}
        </div>
        <span className="font-label-sm text-on-surface-variant flex items-center gap-1">
          <span className="material-symbols-outlined text-[14px]">
            auto_awesome
          </span>
          Ejemplos · pronto personalizados para ti
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md items-stretch">
        <div className="lg:col-span-5 relative rounded-xl overflow-hidden min-h-[220px] shadow-sm">
          <img alt="" className="absolute inset-0 w-full h-full object-cover" src={tab.image} />
          <div className="absolute inset-0 bg-gradient-to-t from-on-surface/80 via-on-surface/20 to-transparent"></div>
          <div className="absolute bottom-0 left-0 right-0 p-space-md text-on-primary">
            <h3 className="font-headline-sm text-headline-sm font-semibold">
              {tab.title}
            </h3>
            <p className="font-body-md text-body-md opacity-90">
              {tab.subtitle}
            </p>
          </div>
        </div>

        <div className="lg:col-span-7 flex flex-col gap-space-sm">
          {tab.items?.map((item) => (
            <div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm hover:shadow-md transition-shadow flex items-center gap-space-md" key={item.title}>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${tab.tile}`}>
                <span className="material-symbols-outlined text-[26px]">
                  {item.icon}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-title-md text-title-md text-on-surface font-semibold">
                  {item.title}
                </p>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {item.tags.map((tag) => (
                    <span className="px-2 py-0.5 rounded-full bg-surface-container-low text-on-surface-variant font-label-sm" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}

          {tab.steps && (
            <div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm grid grid-cols-1 sm:grid-cols-2 gap-space-sm h-full content-center">
              {tab.steps.map((step, index) => (
                <div className="flex items-center gap-space-sm" key={step.text}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${tab.tile}`}>
                    <span className="material-symbols-outlined text-[20px]">
                      {step.icon}
                    </span>
                  </div>
                  <p className="font-body-md text-body-md text-on-surface">
                    <span className={`font-semibold ${tab.accent}`}>{index + 1}.</span> {step.text}
                  </p>
                </div>
              ))}
            </div>
          )}

          {tab.note && (
            <p className="font-label-sm text-on-surface-variant flex items-center gap-1.5 px-1">
              <span className="material-symbols-outlined text-[16px] text-amber-warning">
                info
              </span>
              {tab.note}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

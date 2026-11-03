const INACTIVE_LINK =
  "whitespace-nowrap px-space-md py-space-sm rounded-lg font-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors duration-150";

// Clases del enlace activo tal como las aplica cada pantalla de Stitch
const ACTIVE_LINK = {
  evaluacion:
    "whitespace-nowrap px-space-md py-space-sm transition-colors duration-150 bg-surface-container text-primary font-semibold rounded-lg",
  historial:
    "whitespace-nowrap px-space-md py-space-sm font-label-md transition-colors duration-150 bg-surface-container text-primary font-semibold rounded-lg",
  simulacion:
    "whitespace-nowrap px-space-md py-space-sm rounded-lg font-label-md text-primary font-semibold bg-surface-container transition-colors duration-150",
};

const NAV_ITEMS = [
  { path: "evaluacion", label: "Mi evaluación" },
  { path: "historial", label: "Mi historial" },
  { path: "simulacion", label: "Simulación" },
  { path: "guias-educativas", label: "Guías clínicas" },
];

export default function Header({ active, onNavigate, onQuickDemo }) {
  function handleLink(event, path) {
    event.preventDefault();
    onNavigate(path);
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest border-b border-outline-variant/30 shadow-[0_2px_8px_-2px_rgba(23,43,77,0.05),0_1px_3px_-1px_rgba(23,43,77,0.03)]">
      <div className="bg-surface-container-low text-on-surface-variant font-label-sm text-center py-1 px-margin border-b border-outline-variant/20 flex items-center justify-center gap-space-xs">
        <span className="material-symbols-outlined text-[14px] text-primary">
          info
        </span>
        <span>
          Plataforma de orientación y prevención cardiovascular · Demostración interactiva
        </span>
      </div>
      <div className="h-16 w-full px-margin flex items-center justify-between gap-space-md">
        <div className="flex items-center gap-space-sm shrink-0">
          <img alt="Logotipo PULSO" className="h-8 w-auto object-contain" src="https://lh3.googleusercontent.com/aida/AEtjO1XwgTO4nbsy2yHBWuF1SONimt8APRJzs4rvjrLwZ82qbV_J7pClIRL1eOEPA9hN3zcWIpvlQw2sAkQ5pOvVO5v421faJXO9_F6Oa_OVSy0rWXM7zgIWz4KXde7RdtRAG7Yz0s_WRR0yqF-Ob0t6s-5cm8RRmYCblgug_4hUQbkKAdDPOSEnNE5ZTbGpFJWdh-JgsWhvvPpkkI0fh8KO9QXmdSGMBKVJGoz5Cf9pLdWF" />
          <div className="flex flex-col">
            <span className="font-title-md text-title-md font-bold tracking-tight text-primary leading-none">
              PULSO
            </span>
            <span className="font-label-sm text-[10px] text-on-surface-variant tracking-wider uppercase font-semibold leading-none mt-1">
              Cardio Salus
            </span>
          </div>
        </div>
        <nav className="hidden lg:flex items-center gap-1" data-active-classes="bg-surface-container text-primary font-semibold rounded-lg">
          {NAV_ITEMS.map(({ path, label }) => (
            <a
              aria-current={active === path ? "page" : undefined}
              className={ACTIVE_LINK[active] && active === path ? ACTIVE_LINK[active] : INACTIVE_LINK}
              data-path={path}
              href="#"
              key={path}
              onClick={(event) => handleLink(event, path)}
            >
              {label}
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-space-sm shrink-0">
          <button className="hidden xl:flex items-center gap-1.5 px-space-sm py-1.5 rounded-lg border border-outline-variant/40 bg-surface text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-sm transition-colors" onClick={onQuickDemo} title="Activar demostración rápida de parámetros" type="button">
            <span className="material-symbols-outlined text-[16px] text-secondary">
              bolt
            </span>
            <span>
              Demo Rápida
            </span>
          </button>
          <button className="p-1.5 rounded-lg border border-outline-variant/30 text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors flex items-center justify-center" title="Accesibilidad: Alternar movimiento reducido" type="button">
            <span className="material-symbols-outlined text-[18px]">
              motion_photos_pause
            </span>
          </button>
          <div className="h-6 w-px bg-outline-variant/40 mx-space-xs hidden sm:block"></div>
          <div className="flex items-center gap-space-sm">
            <div className="text-right hidden sm:flex flex-col">
              <span className="font-label-md font-semibold text-on-surface leading-tight">
                Clara Méndez
              </span>
              <span className="font-label-sm text-[11px] text-secondary font-medium leading-none">
                Paciente Demo · 52a
              </span>
            </div>
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shadow-sm">
              <span className="material-symbols-outlined text-on-primary text-[18px]">
                person
              </span>
            </div>
            <a className="p-1.5 text-on-surface-variant hover:text-error hover:bg-surface-container transition-colors rounded-lg flex items-center justify-center" data-path="login" href="#" onClick={(event) => handleLink(event, "login")} title="Cerrar sesión">
              <span className="material-symbols-outlined text-[20px]">
                logout
              </span>
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}

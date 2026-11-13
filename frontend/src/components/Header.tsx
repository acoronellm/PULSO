import type { Navigate, View } from "../types/app";
import Logo from "./Logo";

const INACTIVE_LINK =
  "whitespace-nowrap px-space-md py-space-sm rounded-lg font-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors duration-150";
const ACTIVE_LINK =
  "whitespace-nowrap px-space-md py-space-sm rounded-lg font-label-md text-primary font-semibold bg-surface-container transition-colors duration-150";
const DISABLED_LINK =
  "whitespace-nowrap px-space-md py-space-sm rounded-lg font-label-md text-outline cursor-not-allowed";

const NAV_ITEMS: { path: View; label: string; needsResult?: boolean }[] = [
  { path: "evaluacion", label: "Evaluación" },
  { path: "resultado", label: "Resultado", needsResult: true },
  { path: "simulacion", label: "Simulación" },
  { path: "historial", label: "Historial" },
];

interface HeaderProps {
  active: View;
  hasResult: boolean;
  onNavigate: Navigate;
  email: string;
  onLogout: () => void;
}

export default function Header({ active, hasResult, onNavigate, email, onLogout }: HeaderProps) {
  function handleLink(event: React.MouseEvent<HTMLAnchorElement>, path: View) {
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
          Herramienta educativa de orientación cardiovascular · No es un diagnóstico médico
        </span>
      </div>
      <div className="h-16 w-full px-margin-mobile md:px-margin flex items-center justify-between gap-space-md">
        <a className="flex items-center gap-space-sm shrink-0" href="#" onClick={(event) => handleLink(event, "evaluacion")}>
          <Logo />
          <div className="flex flex-col">
            <span className="font-title-md text-title-md font-bold tracking-tight text-primary leading-none">
              PULSO
            </span>
            <span className="font-label-sm text-[10px] text-on-surface-variant tracking-wider uppercase font-semibold leading-none mt-1">
              Modelo v1
            </span>
          </div>
        </a>
        <nav className="flex items-center gap-1">
          {NAV_ITEMS.map(({ path, label, needsResult }) => {
            const disabled = needsResult && !hasResult;
            return (
              <a
                aria-current={active === path ? "page" : undefined}
                aria-disabled={disabled || undefined}
                className={disabled ? DISABLED_LINK : active === path ? ACTIVE_LINK : INACTIVE_LINK}
                href="#"
                key={path}
                onClick={(event) => handleLink(event, path)}
                title={disabled ? "Disponible después de calcular tu resultado" : undefined}
              >
                {label}
              </a>
            );
          })}
          <span className="hidden lg:block mx-space-sm font-label-sm text-on-surface-variant">
            {email}
          </span>
          <button
            className={INACTIVE_LINK}
            onClick={onLogout}
            type="button"
          >
            Cerrar sesión
          </button>
        </nav>
      </div>
    </header>
  );
}

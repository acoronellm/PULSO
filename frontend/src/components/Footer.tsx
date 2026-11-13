import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="w-full bg-surface-container-lowest border-t border-outline-variant/30 py-space-lg">
      <div className="w-full px-margin-mobile md:px-margin flex flex-col md:flex-row items-center justify-between gap-space-md">
        <div className="flex items-center gap-space-sm">
          <Logo className="w-8 h-8 opacity-80" />
          <div className="flex flex-col">
            <span className="font-label-md text-on-surface font-semibold">
              PULSO · Orientación y prevención cardiovascular
            </span>
            <span className="font-label-sm text-on-surface-variant">
              Proyecto educativo basado en Machine Learning explicable
            </span>
          </div>
        </div>
        <div className="max-w-2xl text-center md:text-right">
          <p className="font-label-sm text-on-surface-variant bg-surface-container-low px-space-md py-space-sm rounded-lg border border-outline-variant/30 inline-block">
            <span className="material-symbols-outlined text-[14px] align-middle mr-1 text-primary">
              verified_user
            </span>
            PULSO no realiza diagnósticos ni reemplaza una valoración médica profesional. Consulta a un profesional de la salud ante cualquier duda.
          </p>
          <div className="mt-space-xs text-on-surface-variant/80 font-label-sm">
            Los datos del perfil no se guardan; solo el resultado se conserva en tu historial.
          </div>
        </div>
      </div>
    </footer>
  );
}

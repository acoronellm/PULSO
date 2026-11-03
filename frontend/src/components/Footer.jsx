export default function Footer() {
  return (
    <footer className="w-full bg-surface-container-lowest border-t border-outline-variant/30 py-space-lg">
      <div className="w-full px-margin flex flex-col md:flex-row items-center justify-between gap-space-md">
        <div className="flex items-center gap-space-sm">
          <img alt="Logotipo PULSO" className="h-6 w-auto object-contain opacity-70" src="https://lh3.googleusercontent.com/aida/AEtjO1XwgTO4nbsy2yHBWuF1SONimt8APRJzs4rvjrLwZ82qbV_J7pClIRL1eOEPA9hN3zcWIpvlQw2sAkQ5pOvVO5v421faJXO9_F6Oa_OVSy0rWXM7zgIWz4KXde7RdtRAG7Yz0s_WRR0yqF-Ob0t6s-5cm8RRmYCblgug_4hUQbkKAdDPOSEnNE5ZTbGpFJWdh-JgsWhvvPpkkI0fh8KO9QXmdSGMBKVJGoz5Cf9pLdWF" />
          <div className="flex flex-col">
            <span className="font-label-md text-on-surface font-semibold">
              PULSO · Prevención & Riesgo Cardiovascular
            </span>
            <span className="font-label-sm text-on-surface-variant">
              Herramienta clínica de autocuidado y monitoreo de tensión arterial
            </span>
          </div>
        </div>
        <div className="max-w-2xl text-center md:text-right">
          <p className="font-label-sm text-on-surface-variant bg-surface-container-low px-space-md py-space-sm rounded-lg border border-outline-variant/30 inline-block">
            <span className="material-symbols-outlined text-[14px] align-middle mr-1 text-primary">
              verified_user
            </span>
            Esta estimación es orientativa y no reemplaza una valoración médica profesional. Consulte a su médico ante cualquier duda.
          </p>
          <div className="mt-space-xs text-on-surface-variant/80 font-label-sm">
            © 2025 Plataforma PULSO. Desarrollado según directrices clínicas internacionales de salud vascular.
          </div>
        </div>
      </div>
    </footer>
  );
}

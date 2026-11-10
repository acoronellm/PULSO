import { useEffect } from "react";

export interface InfoItem {
  title: string;
  category: string;
  icon: string;
  image: string | null;
  bar: string;
  tile: string;
  accent: string;
  detail: string;
  benefit: string;
  benefitIcon: string;
}

interface InfoModalProps {
  item: InfoItem | null;
  onClose: () => void;
}

// Ventana emergente para mostrar el detalle sin recargar la página
export default function InfoModal({ item, onClose }: InfoModalProps) {
  useEffect(() => {
    if (!item) return undefined;

    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }

    document.addEventListener("keydown", handleKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handleKey);
      document.body.style.overflow = "";
    };
  }, [item, onClose]);

  if (!item) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-margin-mobile" onClick={onClose}>
      <div className="absolute inset-0 bg-on-surface/40 backdrop-blur-sm"></div>
      <div
        aria-labelledby="info-modal-title"
        aria-modal="true"
        className="relative w-full max-w-lg bg-surface-card rounded-xl shadow-xl overflow-hidden"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
      >
        <div className={`h-1.5 ${item.bar}`}></div>
        {item.image && (
          <img alt="" className="w-full h-44 object-cover" src={item.image} />
        )}
        <div className="p-space-lg flex flex-col gap-space-md">
          <div className="flex items-start justify-between gap-space-sm">
            <div className="flex items-center gap-space-sm">
              <span className={`w-11 h-11 rounded-full flex items-center justify-center shrink-0 ${item.tile}`}>
                <span className="material-symbols-outlined text-[24px]">
                  {item.icon}
                </span>
              </span>
              <div>
                <span className={`font-label-sm font-semibold ${item.accent}`}>
                  {item.category}
                </span>
                <h3 className="font-headline-sm text-headline-sm text-text-primary" id="info-modal-title">
                  {item.title}
                </h3>
              </div>
            </div>
            <button aria-label="Cerrar" className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-container-low transition-colors" onClick={onClose} type="button">
              <span className="material-symbols-outlined text-[22px]">
                close
              </span>
            </button>
          </div>
          <p className="font-body-lg text-body-lg text-text-secondary">
            {item.detail}
          </p>
          <div className="bg-surface-container-low rounded-lg p-3 flex items-center gap-2">
            <span className={`material-symbols-outlined text-[20px] ${item.accent}`}>
              {item.benefitIcon}
            </span>
            <span className="font-label-md text-text-primary font-semibold">
              {item.benefit}
            </span>
          </div>
          <button className="self-end px-5 py-2.5 rounded-xl bg-primary-container text-on-primary font-label-md font-semibold hover:bg-primary transition-colors" onClick={onClose} type="button">
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}

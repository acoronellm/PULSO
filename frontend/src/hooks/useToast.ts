import { useEffect, useRef, useState } from "react";

export interface ToastState {
  visible: boolean;
  message: string;
}

export type ShowToast = (message?: string) => void;

// Replica el toast de Stitch: aparece y se oculta tras `duration` ms
export default function useToast(duration: number) {
  const [toast, setToast] = useState<ToastState>({ visible: false, message: "" });
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => () => clearTimeout(timer.current), []);

  const showToast: ShowToast = (message = "") => {
    clearTimeout(timer.current);
    setToast({ visible: true, message });
    timer.current = setTimeout(() => {
      setToast((previous) => ({ ...previous, visible: false }));
    }, duration);
  };

  const toastClasses = toast.visible
    ? "opacity-100 translate-y-0"
    : "opacity-0 translate-y-4 pointer-events-none";

  return { toast, toastClasses, showToast };
}

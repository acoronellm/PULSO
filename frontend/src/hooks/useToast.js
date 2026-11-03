import { useEffect, useRef, useState } from "react";

// Replica el toast de Stitch: aparece y se oculta tras `duration` ms
export default function useToast(duration) {
  const [toast, setToast] = useState({ visible: false, message: "" });
  const timer = useRef(null);

  useEffect(() => () => clearTimeout(timer.current), []);

  function showToast(message = "") {
    clearTimeout(timer.current);
    setToast({ visible: true, message });
    timer.current = setTimeout(() => {
      setToast((previous) => ({ ...previous, visible: false }));
    }, duration);
  }

  const toastClasses = toast.visible
    ? "opacity-100 translate-y-0"
    : "opacity-0 translate-y-4 pointer-events-none";

  return { toast, toastClasses, showToast };
}

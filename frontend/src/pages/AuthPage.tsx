import { useState, type FormEvent } from "react";

import Footer from "../components/Footer";
import Logo from "../components/Logo";
import type { AuthResponse } from "../types/pulso";

interface AuthPageProps {
  onSubmit: (mode: "login" | "register", email: string, password: string) => Promise<AuthResponse>;
}

const INPUT =
  "w-full h-12 px-space-md rounded-xl bg-surface-container-low border-[1.5px] border-outline-variant font-label-md text-on-surface outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all";

export default function AuthPage({ onSubmit }: AuthPageProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const registering = mode === "register";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (registering && password !== confirmation) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    try {
      setSubmitting(true);
      await onSubmit(mode, email, password);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "No fue posible autenticarte.");
    } finally {
      setSubmitting(false);
    }
  }

  function changeMode(nextMode: "login" | "register") {
    setMode(nextMode);
    setError("");
  }

  return (
    <>
      <main className="min-h-screen flex flex-col bg-surface-container-lowest">
        <div className="flex items-center justify-between px-margin-mobile md:px-margin h-20 border-b border-outline-variant/30">
          <div className="flex items-center gap-space-sm">
            <Logo className="w-10 h-10" />
            <div>
              <div className="font-title-md font-bold text-primary">PULSO</div>
              <div className="font-label-sm text-on-surface-variant">Orientación cardiovascular</div>
            </div>
          </div>
          <span className="hidden sm:block font-label-sm text-on-surface-variant">
            Tu espacio educativo de salud
          </span>
        </div>

        <div className="flex flex-1 items-center justify-center px-4 py-space-xl">
          <section aria-labelledby="auth-title" className="w-full max-w-md rounded-3xl border border-outline-variant/40 bg-surface-container-lowest p-6 sm:p-9 shadow-xl">
            <div className="mb-space-lg">
              <p className="font-label-sm font-semibold uppercase tracking-wider text-primary">
                Acceso seguro
              </p>
              <h1 className="mt-2 font-title-md text-on-surface text-3xl font-bold" id="auth-title">
                {registering ? "Crea tu cuenta" : "Bienvenido a PULSO"}
              </h1>
              <p className="mt-2 font-body-md text-on-surface-variant">
                {registering
                  ? "Regístrate para comenzar tu evaluación cardiovascular."
                  : "Inicia sesión para continuar con tu evaluación."}
              </p>
            </div>

            <div aria-label="Tipo de acceso" className="mb-space-lg grid grid-cols-2 gap-2 rounded-xl bg-surface-container-low p-1" role="group">
              <button
                aria-pressed={!registering}
                className={`rounded-lg py-2.5 font-label-md font-semibold transition-colors ${!registering ? "bg-surface-container-lowest text-primary shadow-sm" : "text-on-surface-variant"}`}
                onClick={() => changeMode("login")}
                type="button"
              >
                Iniciar sesión
              </button>
              <button
                aria-pressed={registering}
                className={`rounded-lg py-2.5 font-label-md font-semibold transition-colors ${registering ? "bg-surface-container-lowest text-primary shadow-sm" : "text-on-surface-variant"}`}
                onClick={() => changeMode("register")}
                type="button"
              >
                Crear cuenta
              </button>
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <div className="space-y-1.5">
                <label className="font-label-md font-medium text-on-surface" htmlFor="auth-email">Correo electrónico</label>
                <input
                  autoComplete="email"
                  className={INPUT}
                  id="auth-email"
                  maxLength={254}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                  type="email"
                  value={email}
                />
              </div>
              <div className="space-y-1.5">
                <label className="font-label-md font-medium text-on-surface" htmlFor="auth-password">Contraseña</label>
                <input
                  autoComplete={registering ? "new-password" : "current-password"}
                  className={INPUT}
                  id="auth-password"
                  maxLength={128}
                  minLength={registering ? 12 : 1}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  type="password"
                  value={password}
                />
                {registering && (
                  <p className="font-label-sm text-on-surface-variant">Usa al menos 12 caracteres.</p>
                )}
              </div>
              {registering && (
                <div className="space-y-1.5">
                  <label className="font-label-md font-medium text-on-surface" htmlFor="auth-confirmation">Confirma tu contraseña</label>
                  <input
                    autoComplete="new-password"
                    className={INPUT}
                    id="auth-confirmation"
                    maxLength={128}
                    minLength={12}
                    onChange={(event) => setConfirmation(event.target.value)}
                    required
                    type="password"
                    value={confirmation}
                  />
                </div>
              )}
              {error && (
                <p aria-live="polite" className="rounded-lg bg-error-container px-3 py-2 font-label-md text-on-error-container" role="alert">
                  {error}
                </p>
              )}
              <button
                className="w-full rounded-xl bg-primary px-space-md py-3.5 font-label-md font-bold text-on-primary shadow-sm transition-opacity hover:opacity-90 disabled:cursor-wait disabled:opacity-60"
                disabled={submitting}
                type="submit"
              >
                {submitting ? "Un momento..." : registering ? "Crear cuenta" : "Iniciar sesión"}
              </button>
            </form>

            <p className="mt-space-lg text-center font-label-sm text-on-surface-variant">
              PULSO ofrece información educativa; no es un diagnóstico médico.
            </p>
          </section>
        </div>
        <Footer />
      </main>
    </>
  );
}

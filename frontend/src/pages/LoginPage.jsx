import { useState } from "react";

const ACTIVE_TAB =
  "flex-1 py-space-sm px-space-md rounded-lg font-label-md text-label-md transition-all duration-200 text-center bg-surface-container-lowest text-primary-container shadow-sm font-semibold";
const INACTIVE_TAB =
  "flex-1 py-space-sm px-space-md rounded-lg font-label-md text-label-md transition-all duration-200 text-center text-on-surface-variant hover:text-on-surface font-medium";

export default function LoginPage({ onLogin }) {
  const [tab, setTab] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);

  function fillDemoUser() {
    setEmail("clara.mendez@ejemplo.com");
    setPassword("PulsoSalud2025");
  }

  function handleFormSubmit(event, type) {
    event.preventDefault();
    if (type === "login") {
      onLogin();
    } else {
      setTab("login");
    }
  }

  return (
    <main className="w-full min-h-screen bg-surface flex flex-col justify-center items-center p-gutter">
      <div className="flex flex-col w-full max-w-6xl mx-auto my-auto items-center justify-center p-space-sm sm:p-gutter">
        <div className="w-full bg-surface-container-lowest rounded-xl shadow-xl overflow-hidden flex flex-col lg:flex-row">
          <div className="lg:w-[45%] bg-gradient-to-br from-surface-container-low via-surface-container to-surface-container-lowest p-gutter lg:p-space-xl flex flex-col justify-between relative overflow-hidden">
            <div className="absolute -right-24 -bottom-24 w-80 h-80 rounded-full bg-secondary-fixed/20 blur-3xl pointer-events-none"></div>
            <div className="absolute -left-16 top-12 w-64 h-64 rounded-full bg-primary-fixed/40 blur-2xl pointer-events-none"></div>
            <div className="relative z-10 flex flex-col gap-space-lg">
              <div className="flex items-center gap-space-sm">
                <div className="w-12 h-12 rounded-xl bg-primary-container flex items-center justify-center text-on-primary shadow-md">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" viewBox="0 0 24 24">
                    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path>
                    <path d="M3.22 12H7l2-4 3 8 2.5-5 1.5 2h4.78" stroke="white" strokeWidth="2"></path>
                  </svg>
                </div>
                <div>
                  <span className="font-headline-md text-headline-md tracking-wider text-primary font-bold block leading-none">
                    PULSO
                  </span>
                  {" "}
                  <span className="font-label-sm text-label-sm text-secondary font-medium tracking-normal">
                    Acompañamiento cardiovascular
                  </span>
                </div>
              </div>
              <div className="space-y-space-sm pt-space-xs">
                <h1 className="font-headline-lg text-headline-lg text-on-background leading-snug">
                  Comprender tu salud cardiovascular es el primer paso para protegerla.
                </h1>
                <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">
                  Una plataforma clara, cálida y sin tecnicismos pensada para acompañar tu bienestar cotidiano con tranquilidad y confianza.
                </p>
              </div>
              <div className="flex flex-col gap-space-md pt-space-xs">
                <div className="flex items-start gap-space-md p-space-sm rounded-lg bg-surface-container-lowest/80 shadow-sm backdrop-blur-sm">
                  <div className="w-10 h-10 rounded-lg bg-secondary-fixed flex items-center justify-center text-on-secondary-fixed shrink-0">
                    <span className="material-symbols-outlined text-secondary" style={{ fontVariationSettings: "'FILL' 1" }}>
                      favorite
                    </span>
                  </div>
                  <div>
                    <p className="font-title-md text-title-md text-on-surface font-semibold">
                      Orientación preventiva personalizada
                    </p>
                    <p className="font-body-md text-body-md text-on-surface-variant">
                      Recomendaciones amables construidas a tu ritmo para cuidar tu corazón.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-space-md p-space-sm rounded-lg bg-surface-container-lowest/80 shadow-sm backdrop-blur-sm">
                  <div className="w-10 h-10 rounded-lg bg-primary-fixed flex items-center justify-center text-primary shrink-0">
                    <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                      vital_signs
                    </span>
                  </div>
                  <div>
                    <p className="font-title-md text-title-md text-on-surface font-semibold">
                      Simulaciones claras de hábitos
                    </p>
                    <p className="font-body-md text-body-md text-on-surface-variant">
                      Visualiza fácilmente cómo pequeñas caminatas o descansos suman a tu vitalidad.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-space-md p-space-sm rounded-lg bg-surface-container-lowest/80 shadow-sm backdrop-blur-sm">
                  <div className="w-10 h-10 rounded-lg bg-surface-variant flex items-center justify-center text-primary-container shrink-0">
                    <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                      verified_user
                    </span>
                  </div>
                  <div>
                    <p className="font-title-md text-title-md text-on-surface font-semibold">
                      Tus datos siempre seguros y privados
                    </p>
                    <p className="font-body-md text-body-md text-on-surface-variant">
                      Toda tu información bajo estricta custodia médica y confidencialidad total.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="pt-space-xl relative z-10">
              <div className="inline-flex items-center gap-space-xs px-space-md py-space-xs rounded-full bg-secondary/10 text-secondary font-label-md text-label-md">
                <span className="material-symbols-outlined text-[16px]">
                  info
                </span>
                {" "}
                <span>
                  Prototipo de demostración interactiva · Datos ficticios seguros
                </span>
              </div>
            </div>
          </div>
          <div className="lg:w-[55%] bg-surface-container-lowest p-gutter lg:p-space-xl flex flex-col justify-between">
            <div>
              <div className="flex p-space-xs bg-surface-container-low rounded-xl mb-space-lg">
                <button className={tab === "login" ? ACTIVE_TAB : INACTIVE_TAB} id="tab-login" onClick={() => setTab("login")}>
                  Iniciar sesión
                </button>
                {" "}
                <button className={tab === "register" ? ACTIVE_TAB : INACTIVE_TAB} id="tab-register" onClick={() => setTab("register")}>
                  Crear cuenta
                </button>
                {" "}
                <button className={tab === "recover" ? ACTIVE_TAB : INACTIVE_TAB} id="tab-recover" onClick={() => setTab("recover")}>
                  Recuperar acceso
                </button>
              </div>
              <div className={tab === "login" ? "space-y-space-md" : "space-y-space-md hidden"} id="view-login">
                <div className="space-y-space-xs">
                  <h2 className="font-headline-sm text-headline-sm text-on-surface">
                    Bienvenido de vuelta
                  </h2>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Ingresa tus datos para continuar con tu seguimiento diario.
                  </p>
                </div>
                <form className="space-y-space-md pt-space-xs" onSubmit={(event) => handleFormSubmit(event, "login")}>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                      Correo electrónico
                    </label>
                    {" "}
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-3 text-outline pointer-events-none text-[20px]">
                        mail
                      </span>
                      {" "}
                      <input className="w-full h-12 pl-10 pr-4 bg-surface-container-low text-on-surface rounded-xl font-body-md text-body-md outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline" id="login-email" onChange={(event) => setEmail(event.target.value)} placeholder="clara.mendez@ejemplo.com" required type="email" value={email} />
                    </div>
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                      Contraseña
                    </label>
                    {" "}
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-3 text-outline pointer-events-none text-[20px]">
                        lock
                      </span>
                      {" "}
                      <input className="w-full h-12 pl-10 pr-12 bg-surface-container-low text-on-surface rounded-xl font-body-md text-body-md outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline" id="login-password" onChange={(event) => setPassword(event.target.value)} placeholder="Ingresa tu contraseña" required type={showLoginPassword ? "text" : "password"} value={password} />
                      {" "}
                      <button className="absolute right-3 text-outline hover:text-on-surface flex items-center justify-center p-1" onClick={() => setShowLoginPassword((value) => !value)} type="button">
                        <span className="material-symbols-outlined text-[20px]" id="pwd-icon-login">
                          {showLoginPassword ? "visibility_off" : "visibility"}
                        </span>
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center justify-between pt-space-xs">
                    <label className="flex items-center gap-space-xs cursor-pointer select-none">
                      <input className="w-5 h-5 rounded text-primary-container accent-primary-container focus:ring-0 cursor-pointer" type="checkbox" />
                      {" "}
                      <span className="font-body-md text-body-md text-on-surface-variant">
                        Recordar mis datos en este equipo
                      </span>
                    </label>
                    {" "}
                    <button className="font-label-md text-label-md text-primary font-medium hover:underline" onClick={() => setTab("recover")} type="button">
                      ¿Olvidaste tu contraseña?
                    </button>
                  </div>
                  <div className="pt-space-sm space-y-space-sm">
                    <button className="w-full h-12 bg-primary-container text-on-primary rounded-xl font-headline-sm text-title-md font-semibold shadow-md hover:opacity-95 transition-all flex items-center justify-center gap-space-xs" type="submit">
                      <span>
                        Ingresar a PULSO
                      </span>
                      {" "}
                      <span className="material-symbols-outlined text-[20px]">
                        arrow_forward
                      </span>
                    </button>
                    {" "}
                    <button className="w-full h-12 bg-secondary-fixed text-on-secondary-fixed rounded-xl font-headline-sm text-title-md font-semibold hover:opacity-90 transition-all flex items-center justify-center gap-space-xs shadow-sm" onClick={fillDemoUser} type="button">
                      <span className="material-symbols-outlined text-[20px]">
                        account_circle
                      </span>
                      {" "}
                      <span>
                        Entrar con usuario demo (Clara Méndez)
                      </span>
                    </button>
                  </div>
                </form>
              </div>
              <div className={tab === "register" ? "space-y-space-md" : "space-y-space-md hidden"} id="view-register">
                <div className="space-y-space-xs">
                  <h2 className="font-headline-sm text-headline-sm text-on-surface">
                    Comienza tu cuidado hoy
                  </h2>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Crea tu espacio de salud personalizado en menos de un minuto.
                  </p>
                </div>
                <form className="space-y-space-sm pt-space-xs" onSubmit={(event) => handleFormSubmit(event, "register")}>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                      Nombre completo
                    </label>
                    {" "}
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-3 text-outline pointer-events-none text-[20px]">
                        person
                      </span>
                      {" "}
                      <input className="w-full h-12 pl-10 pr-4 bg-surface-container-low text-on-surface rounded-xl font-body-md text-body-md outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline" placeholder="Clara Méndez" required type="text" />
                    </div>
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                      Correo electrónico
                    </label>
                    {" "}
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-3 text-outline pointer-events-none text-[20px]">
                        mail
                      </span>
                      {" "}
                      <input className="w-full h-12 pl-10 pr-4 bg-surface-container-low text-on-surface rounded-xl font-body-md text-body-md outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline" placeholder="clara.mendez@ejemplo.com" required type="email" />
                    </div>
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                      Contraseña
                    </label>
                    {" "}
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-3 text-outline pointer-events-none text-[20px]">
                        lock
                      </span>
                      {" "}
                      <input className="w-full h-12 pl-10 pr-12 bg-surface-container-low text-on-surface rounded-xl font-body-md text-body-md outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline" id="reg-password" placeholder="Mínimo 8 caracteres" required type={showRegisterPassword ? "text" : "password"} />
                      {" "}
                      <button className="absolute right-3 text-outline hover:text-on-surface flex items-center justify-center p-1" onClick={() => setShowRegisterPassword((value) => !value)} type="button">
                        <span className="material-symbols-outlined text-[20px]" id="pwd-icon-reg">
                          {showRegisterPassword ? "visibility_off" : "visibility"}
                        </span>
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                      Confirmar contraseña
                    </label>
                    {" "}
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-3 text-outline pointer-events-none text-[20px]">
                        lock_reset
                      </span>
                      {" "}
                      <input className="w-full h-12 pl-10 pr-4 bg-surface-container-low text-on-surface rounded-xl font-body-md text-body-md outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline" id="reg-password-confirm" placeholder="Repite tu contraseña" required type="password" />
                    </div>
                  </div>
                  <div className="pt-space-xs">
                    <label className="flex items-start gap-space-xs cursor-pointer select-none">
                      <input className="w-5 h-5 rounded text-primary-container accent-primary-container mt-0.5 cursor-pointer" required type="checkbox" />
                      {" "}
                      <span className="font-body-md text-body-md text-on-surface-variant">
                        Acepto los términos de servicio y las políticas de acompañamiento cardiovascular.
                      </span>
                    </label>
                  </div>
                  <div className="pt-space-sm">
                    <button className="w-full h-12 bg-primary-container text-on-primary rounded-xl font-headline-sm text-title-md font-semibold shadow-md hover:opacity-95 transition-all flex items-center justify-center gap-space-xs" type="submit">
                      <span>
                        Registrarme en PULSO
                      </span>
                      {" "}
                      <span className="material-symbols-outlined text-[20px]">
                        check_circle
                      </span>
                    </button>
                  </div>
                </form>
              </div>
              <div className={tab === "recover" ? "space-y-space-md" : "space-y-space-md hidden"} id="view-recover">
                <div className="space-y-space-xs">
                  <h2 className="font-headline-sm text-headline-sm text-on-surface">
                    Recuperar acceso
                  </h2>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Escribe el correo electrónico asociado a tu cuenta y te enviaremos un enlace seguro para restablecer tu contraseña.
                  </p>
                </div>
                <form className="space-y-space-md pt-space-xs" onSubmit={(event) => handleFormSubmit(event, "recover")}>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                      Correo registrado
                    </label>
                    {" "}
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-3 text-outline pointer-events-none text-[20px]">
                        mail
                      </span>
                      {" "}
                      <input className="w-full h-12 pl-10 pr-4 bg-surface-container-low text-on-surface rounded-xl font-body-md text-body-md outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline" placeholder="clara.mendez@ejemplo.com" required type="email" />
                    </div>
                  </div>
                  <div className="p-space-md bg-secondary-fixed/30 rounded-xl flex items-start gap-space-sm text-on-secondary-fixed-variant">
                    <span className="material-symbols-outlined text-[20px] text-secondary">
                      mail_outline
                    </span>
                    {" "}
                    <p className="font-body-md text-body-md">
                      Recibirás un código de acceso temporal válido por 15 minutos en tu bandeja de entrada.
                    </p>
                  </div>
                  <div className="pt-space-sm space-y-space-sm">
                    <button className="w-full h-12 bg-primary-container text-on-primary rounded-xl font-headline-sm text-title-md font-semibold shadow-md hover:opacity-95 transition-all flex items-center justify-center gap-space-xs" type="submit">
                      <span>
                        Enviar enlace de recuperación
                      </span>
                      {" "}
                      <span className="material-symbols-outlined text-[20px]">
                        send
                      </span>
                    </button>
                    {" "}
                    <button className="w-full h-12 bg-surface-container-low text-on-surface rounded-xl font-headline-sm text-title-md font-semibold hover:bg-surface-container transition-all flex items-center justify-center" onClick={() => setTab("login")} type="button">
                      Volver a Iniciar Sesión
                    </button>
                  </div>
                </form>
              </div>
            </div>
            <div className="pt-space-xl mt-space-md border-t-0 flex flex-col sm:flex-row items-center justify-between gap-space-sm text-on-surface-variant font-label-sm text-label-sm">
              <div className="flex items-center gap-space-xs">
                <span className="material-symbols-outlined text-[16px] text-secondary">
                  lock
                </span>
                {" "}
                <span>
                  Cifrado clínico de extremo a extremo
                </span>
              </div>
              <div className="flex items-center gap-space-md">
                <a className="hover:text-primary transition-colors" href="#" onClick={(event) => event.preventDefault()}>
                  Privacidad
                </a>
                {" "}
                <span>
                  ·
                </span>
                {" "}
                <a className="hover:text-primary transition-colors" href="#" onClick={(event) => event.preventDefault()}>
                  Términos
                </a>
                {" "}
                <span>
                  ·
                </span>
                {" "}
                <a className="hover:text-primary transition-colors" href="#" onClick={(event) => event.preventDefault()}>
                  Soporte médico
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

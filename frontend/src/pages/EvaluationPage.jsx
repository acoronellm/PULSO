import { useState } from "react";

import useToast from "../hooks/useToast";
import { calculateBmi } from "../utils/health";

const SEX_ACTIVE =
  "flex items-center justify-center gap-space-xs rounded-xl font-label-md transition-all font-semibold bg-surface-container text-primary shadow-sm ring-2 ring-primary";
const SEX_INACTIVE =
  "flex items-center justify-center gap-space-xs rounded-xl font-label-md transition-all font-medium bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm text-on-surface-variant hover:border-primary/60 hover:bg-surface-container";
const HABIT_ACTIVE =
  "py-2 rounded-lg font-label-md text-primary font-bold bg-surface-container shadow-sm ring-2 ring-primary transition-all flex items-center justify-center gap-1";
const HABIT_INACTIVE =
  "py-2 rounded-lg font-label-md text-on-surface-variant bg-surface-container-lowest border-[1.5px] border-outline-variant hover:border-primary/60 transition-all flex items-center justify-center gap-1";

// Clasificación de la OMS, igual que el script de Stitch
function bmiStatus(bmi) {
  if (bmi < 18.5) {
    return {
      text: "Bajo peso",
      pill: "px-space-md py-1.5 rounded-full bg-surface-container-highest text-on-surface font-label-md font-semibold flex items-center gap-1.5 transition-colors",
      dot: "w-2 h-2 rounded-full bg-outline",
    };
  }
  if (bmi < 25) {
    return {
      text: "Peso saludable",
      pill: "px-space-md py-1.5 rounded-full bg-secondary-fixed text-on-secondary-fixed font-label-md font-semibold flex items-center gap-1.5 transition-colors",
      dot: "w-2 h-2 rounded-full bg-secondary",
    };
  }
  if (bmi < 30) {
    return {
      text: "Sobrepeso moderado",
      pill: "px-space-md py-1.5 rounded-full bg-surface-container text-primary font-label-md font-semibold flex items-center gap-1.5 transition-colors",
      dot: "w-2 h-2 rounded-full bg-primary",
    };
  }
  return {
    text: "Obesidad clínica",
    pill: "px-space-md py-1.5 rounded-full bg-error-container text-on-error-container font-label-md font-semibold flex items-center gap-1.5 transition-colors",
    dot: "w-2 h-2 rounded-full bg-error",
  };
}

function bpCategory(sys, dia) {
  if (sys < 120 && dia < 80) {
    return {
      title: "Presión arterial óptima",
      sub: "Valores dentro del rango protector ideal",
      icon: "material-symbols-outlined text-[20px] text-secondary",
    };
  }
  if (sys <= 129 && dia < 85) {
    return {
      title: "Presión arterial normal",
      sub: "Valores estándar en población adulta",
      icon: "material-symbols-outlined text-[20px] text-secondary",
    };
  }
  if (sys <= 139 || dia <= 89) {
    return {
      title: "Presión Normal Alta / Prehipertensión",
      sub: "Sistólica entre 130-139 mmHg o Diastólica 85-89 mmHg",
      icon: "material-symbols-outlined text-[20px] text-primary",
    };
  }
  return {
    title: "Tensión arterial elevada",
    sub: "Se sugiere confirmación médica ambulatoria periódica",
    icon: "material-symbols-outlined text-[20px] text-error",
  };
}

function HabitButtons({ habit, value, onChange }) {
  return (
    <div className="grid grid-cols-2 gap-space-xs mt-2">
      <button className={value ? HABIT_ACTIVE : HABIT_INACTIVE} id={`${habit}-si`} onClick={() => onChange(habit, true)} type="button">
        {value && (
          <span className="material-symbols-outlined text-[14px]">
            check
          </span>
        )}
        <span>
          Sí
        </span>
      </button>
      <button className={!value ? HABIT_ACTIVE : HABIT_INACTIVE} id={`${habit}-no`} onClick={() => onChange(habit, false)} type="button">
        {!value && (
          <span className="material-symbols-outlined text-[14px]">
            check
          </span>
        )}
        <span>
          No
        </span>
      </button>
    </div>
  );
}

export default function EvaluationPage({ form, onChange, onSubmit, loading, error }) {
  const { toast, toastClasses, showToast } = useToast(3500);
  const [validationError, setValidationError] = useState("");
  const visibleError = validationError || error;

  const estatura = parseFloat(form.estatura);
  const peso = parseFloat(form.peso);
  const bmiValid = estatura > 80 && peso > 20;
  const bmi = bmiValid ? calculateBmi(estatura, peso).toFixed(1) : null;
  const bmiInfo = bmiStatus(bmi ?? 0);
  const sys = parseInt(form.sistolica) || 120;
  const dia = parseInt(form.diastolica) || 80;
  const bp = bpCategory(sys, dia);
  const pointerPercent = Math.max(5, Math.min(95, ((sys - 90) / (180 - 90)) * 100));

  function handleInput(event) {
    onChange(event.target.name, event.target.value);
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (Number(form.sistolica) <= Number(form.diastolica)) {
      setValidationError("La presión sistólica debe ser mayor que la diastólica.");
      return;
    }
    setValidationError("");
    showToast("Calculando tu índice de salud cardiovascular...");
    onSubmit(showToast);
  }

  return (
    <main className="w-full pt-24 bg-surface min-h-[calc(100vh-140px)]">
      <div className="flex flex-col w-full">
        <div className="w-full max-w-7xl mx-auto px-margin-mobile md:px-margin pb-space-xl">
          {/* Header de bienvenida cordial */}
          <div className="pt-space-md pb-space-lg flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div>
              <div className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded-full bg-surface-container text-primary font-label-sm mb-space-xs">
                <span className="material-symbols-outlined text-[16px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                  ecg_heart
                </span>
                {" "}
                <span>
                  Protocolo Cardiovascular Rápido · 3 a 5 minutos
                </span>
              </div>
              <h1 className="font-display-hero text-headline-lg-mobile md:text-headline-lg font-bold text-on-surface tracking-tight">
                Hola, Clara. Completemos tu evaluación de hoy
              </h1>
              <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mt-1">
                Ingresa tus medidas habituales. Los datos se guardan de forma segura para orientarte mejor y generar tus recomendaciones personalizadas.
              </p>
            </div>
            {/* Badge de privacidad y cifrado clínico */}
            <div className="flex items-center gap-space-sm bg-surface-container-lowest px-space-md py-space-sm rounded-xl shadow-sm border border-outline-variant/20 shrink-0">
              <div className="w-9 h-9 rounded-full bg-surface-container flex items-center justify-center text-secondary">
                <span className="material-symbols-outlined text-[20px]">
                  shield_person
                </span>
              </div>
              <div>
                <div className="font-label-sm text-on-surface font-semibold">
                  Datos protegidos
                </div>
                <div className="font-label-sm text-[11px] text-on-surface-variant">
                  Confidencialidad biométrica activa
                </div>
              </div>
            </div>
          </div>
          {/* Stepper de 3 Pasos Clínicos */}
          <div className="w-full bg-surface-container-lowest rounded-xl shadow-sm p-space-md mb-space-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md relative">
              {/* Paso 1 */}
              <div className="flex items-center gap-space-sm group cursor-pointer" onClick={() => showToast("Navegando a la revisión de datos iniciales...")}>
                <div className="w-10 h-10 rounded-xl bg-primary text-on-primary flex items-center justify-center font-headline-sm font-semibold transition-all shadow-sm" id="step-badge-1">
                  <span className="material-symbols-outlined text-[20px]">
                    check
                  </span>
                </div>
                <div className="min-w-0">
                  <span className="font-label-sm text-secondary block font-semibold uppercase tracking-wider text-[11px]">
                    Paso 1 · Completado
                  </span>
                  {" "}
                  <span className="font-title-md text-body-lg font-semibold text-on-surface block truncate">
                    Datos personales
                  </span>
                </div>
              </div>
              {/* Paso 2 (Activo) */}
              <div className="flex items-center gap-space-sm">
                <div className="w-10 h-10 rounded-xl bg-primary-container text-on-primary flex items-center justify-center font-headline-sm font-bold shadow-md shadow-primary/20 ring-4 ring-primary/10" id="step-badge-2">
                  2
                </div>
                <div className="min-w-0">
                  <span className="font-label-sm text-primary block font-semibold uppercase tracking-wider text-[11px]">
                    Paso 2 · En curso
                  </span>
                  {" "}
                  <span className="font-title-md text-body-lg font-bold text-on-surface block truncate">
                    Medidas y hábitos
                  </span>
                </div>
              </div>
              {/* Paso 3 */}
              <div className="flex items-center gap-space-sm opacity-60">
                <div className="w-10 h-10 rounded-xl bg-surface-container text-on-surface-variant flex items-center justify-center font-headline-sm font-semibold" id="step-badge-3">
                  3
                </div>
                <div className="min-w-0">
                  <span className="font-label-sm text-on-surface-variant block font-medium uppercase tracking-wider text-[11px]">
                    Paso 3 · Siguiente
                  </span>
                  {" "}
                  <span className="font-title-md text-body-lg font-medium text-on-surface block truncate">
                    Revisar y calcular
                  </span>
                </div>
              </div>
            </div>
            {/* Barra de progreso visual sutil */}
            <div className="w-full bg-surface-container h-1.5 rounded-full mt-space-md overflow-hidden">
              <div className="bg-primary h-full rounded-full transition-all duration-500" style={{ width: "66%" }}></div>
            </div>
          </div>
          {/* Layout Grid Principal: Formulario + Panel Lateral Informativo */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
            {/* Columna Principal: El Formulario Elegante */}
            <div className="lg:col-span-8 flex flex-col gap-space-lg">
              <form className="bg-surface-container-lowest rounded-xl shadow-md p-space-lg md:p-space-xl flex flex-col gap-space-xl" id="evaluationForm" onSubmit={handleSubmit}>
                {/* SECCIÓN 1: Datos Personales */}
                <section className="flex flex-col gap-space-md">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-space-sm">
                      <span className="w-8 h-8 rounded-lg bg-surface-container text-primary flex items-center justify-center font-semibold text-label-md">
                        01
                      </span>
                      {" "}
                      <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                        Datos personales
                      </h2>
                    </div>
                    {" "}
                    <span className="font-label-sm text-secondary bg-surface-container-low px-space-sm py-0.5 rounded-md flex items-center gap-1 font-medium">
                      <span className="material-symbols-outlined text-[14px]">
                        verified
                      </span>
                      {" "}Validado
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                    {/* Campo Edad */}
                    <div className="flex flex-col gap-1.5">
                      <label className="font-label-md text-on-surface font-medium flex items-center justify-between" htmlFor="inputEdad">
                        <span>
                          Edad actual
                        </span>
                        {" "}
                        <span className="font-label-sm text-on-surface-variant text-[11px]">
                          Mayor de 18 años
                        </span>
                      </label>
                      {" "}
                      <div className="relative">
                        <input className="w-full h-12 px-space-md rounded-xl bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm font-title-md font-semibold text-on-surface outline-none hover:border-primary/60 focus:bg-surface-container-lowest focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all text-left [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" id="inputEdad" max="110" min="18" name="edad" onChange={handleInput} required type="number" value={form.edad} />
                        {" "}
                        <span className="absolute right-space-md top-1/2 -translate-y-1/2 font-label-md text-on-surface-variant pointer-events-none">
                          años
                        </span>
                      </div>
                      {" "}
                      <span className="font-label-sm text-on-surface-variant flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px] text-primary">
                          info
                        </span>
                        {" "}Calibrado para tablas de riesgo adulto SCORE-2
                      </span>
                    </div>
                    {/* Sexo Biológico Toggle Cards */}
                    <div className="flex flex-col gap-1.5">
                      <label className="font-label-md text-on-surface font-medium">
                        Sexo asignado al nacer
                      </label>
                      {" "}
                      <div className="grid grid-cols-2 gap-space-sm h-12">
                        <button className={form.sexo === "mujer" ? SEX_ACTIVE : SEX_INACTIVE} id="btnSexoMujer" onClick={() => onChange("sexo", "mujer")} type="button">
                          <span className="material-symbols-outlined text-[18px]">
                            female
                          </span>
                          {" "}
                          <span>
                            Mujer
                          </span>
                        </button>
                        {" "}
                        <button className={form.sexo === "hombre" ? SEX_ACTIVE : SEX_INACTIVE} id="btnSexoHombre" onClick={() => onChange("sexo", "hombre")} type="button">
                          <span className="material-symbols-outlined text-[18px]">
                            male
                          </span>
                          {" "}
                          <span>
                            Hombre
                          </span>
                        </button>
                      </div>
                      {" "}
                      <span className="font-label-sm text-on-surface-variant">
                        Requerido para cálculo hormonal de riesgo vascular
                      </span>
                    </div>
                  </div>
                </section>
                <div className="w-full h-px bg-surface-container"></div>
                {/* SECCIÓN 2: Medidas Físicas e IMC en Vivo */}
                <section className="flex flex-col gap-space-md">
                  <div className="flex items-center gap-space-sm">
                    <span className="w-8 h-8 rounded-lg bg-surface-container text-primary flex items-center justify-center font-semibold text-label-md">
                      02
                    </span>
                    {" "}
                    <div>
                      <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                        Medidas físicas
                      </h2>
                      <p className="font-label-sm text-on-surface-variant">
                        El IMC se computa en tiempo real según los parámetros ingresados
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                    {/* Estatura */}
                    <div className="flex flex-col gap-1.5">
                      <label className="font-label-md text-on-surface font-medium" htmlFor="inputEstatura">
                        Estatura habitual
                      </label>
                      {" "}
                      <div className="relative">
                        <input className="w-full h-12 px-space-md rounded-xl bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm font-title-md font-semibold text-on-surface outline-none hover:border-primary/60 focus:bg-surface-container-lowest focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all text-left [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" id="inputEstatura" max="220" min="120" name="estatura" onChange={handleInput} required type="number" value={form.estatura} />
                        {" "}
                        <span className="absolute right-space-md top-1/2 -translate-y-1/2 font-label-md text-on-surface-variant pointer-events-none">
                          cm
                        </span>
                      </div>
                      {" "}
                      <span className="font-label-sm text-on-surface-variant">
                        Descalzo(a) y en postura erguida
                      </span>
                    </div>
                    {/* Peso */}
                    <div className="flex flex-col gap-1.5">
                      <label className="font-label-md text-on-surface font-medium" htmlFor="inputPeso">
                        Peso actual
                      </label>
                      {" "}
                      <div className="relative">
                        <input className="w-full h-12 px-space-md rounded-xl bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm font-title-md font-semibold text-on-surface outline-none hover:border-primary/60 focus:bg-surface-container-lowest focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all text-left [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" id="inputPeso" max="200" min="30" name="peso" onChange={handleInput} required step="0.1" type="number" value={form.peso} />
                        {" "}
                        <span className="absolute right-space-md top-1/2 -translate-y-1/2 font-label-md text-on-surface-variant pointer-events-none">
                          kg
                        </span>
                      </div>
                      {" "}
                      <span className="font-label-sm text-on-surface-variant">
                        Toma matutina con ropa ligera
                      </span>
                    </div>
                  </div>
                  {/* Tarjeta destacada de solo lectura: IMC Dinámico */}
                  <div className="bg-surface-container-low rounded-xl p-space-md flex flex-col sm:flex-row sm:items-center justify-between gap-space-md transition-all">
                    <div className="flex items-start gap-space-sm">
                      <div className="w-12 h-12 rounded-xl bg-surface-container-lowest flex items-center justify-center text-primary shadow-sm shrink-0">
                        <span className="material-symbols-outlined text-[26px]">
                          monitor_weight
                        </span>
                      </div>
                      <div>
                        <div className="font-label-sm text-on-surface-variant font-medium">
                          Índice de Masa Corporal (IMC) calculado automáticamente
                        </div>
                        <div className="flex items-baseline gap-space-xs mt-0.5">
                          <span className="font-metric-numeral text-headline-lg font-bold text-on-surface tracking-tight" id="bmiValue">
{bmi ?? "--"}
</span>
                          {" "}
                          <span className="font-label-md text-on-surface-variant">
                            kg/m²
                          </span>
                        </div>
                      </div>
                    </div>
                    {/* Píldora de Estado IMC */}
                    <div className="flex sm:flex-col sm:items-end gap-1">
                      <div className={bmiInfo.pill} id="bmiPill">
                        <span className={bmiInfo.dot} id="bmiDot"></span>
                        {" "}
                        <span id="bmiStatusText">
{bmiInfo.text}
</span>
                      </div>
                      {" "}
                      <span className="font-label-sm text-on-surface-variant text-[11px]">
                        Rango de referencia según la OMS
                      </span>
                    </div>
                  </div>
                </section>
                <div className="w-full h-px bg-surface-container"></div>
                {/* SECCIÓN 3: Presión Arterial y Estilo de Vida */}
                <section className="flex flex-col gap-space-md">
                  <div className="flex items-center gap-space-sm">
                    <span className="w-8 h-8 rounded-lg bg-surface-container text-primary flex items-center justify-center font-semibold text-label-md">
                      03
                    </span>
                    {" "}
                    <div>
                      <h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                        Presión arterial y hábitos
                      </h2>
                      <p className="font-label-sm text-on-surface-variant">
                        Valores de tu tensiómetro domiciliario o control ambulatorio
                      </p>
                    </div>
                  </div>
                  {/* Campos de Tensión Arterial */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                    {/* Sistólica */}
                    <div className="flex flex-col gap-1.5">
                      <label className="font-label-md text-on-surface font-medium flex justify-between" htmlFor="inputSys">
                        <span>
                          Presión sistólica (máxima)
                        </span>
                        {" "}
                        <span className="font-label-sm text-on-surface-variant text-[11px]">
                          Ideal {"<"} 120
                        </span>
                      </label>
                      {" "}
                      <div className="relative">
                        <input className="w-full h-12 px-space-md rounded-xl bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm font-title-md font-semibold text-on-surface outline-none hover:border-primary/60 focus:bg-surface-container-lowest focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all text-left [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" id="inputSys" max="250" min="70" name="sistolica" onChange={handleInput} required type="number" value={form.sistolica} />
                        {" "}
                        <span className="absolute right-space-md top-1/2 -translate-y-1/2 font-label-md text-on-surface-variant pointer-events-none">
                          mmHg
                        </span>
                      </div>
                      {" "}
                      <span className="font-label-sm text-on-surface-variant flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px] text-secondary">
                          help
                        </span>
                        {" "}El valor superior de tu toma habitual
                      </span>
                    </div>
                    {/* Diastólica */}
                    <div className="flex flex-col gap-1.5">
                      <label className="font-label-md text-on-surface font-medium flex justify-between" htmlFor="inputDia">
                        <span>
                          Presión diastólica (mínima)
                        </span>
                        {" "}
                        <span className="font-label-sm text-on-surface-variant text-[11px]">
                          Ideal {"<"} 80
                        </span>
                      </label>
                      {" "}
                      <div className="relative">
                        <input className="w-full h-12 px-space-md rounded-xl bg-surface-container-low border-[1.5px] border-outline-variant shadow-sm font-title-md font-semibold text-on-surface outline-none hover:border-primary/60 focus:bg-surface-container-lowest focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all text-left [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" id="inputDia" max="150" min="40" name="diastolica" onChange={handleInput} required type="number" value={form.diastolica} />
                        {" "}
                        <span className="absolute right-space-md top-1/2 -translate-y-1/2 font-label-md text-on-surface-variant pointer-events-none">
                          mmHg
                        </span>
                      </div>
                      {" "}
                      <span className="font-label-sm text-on-surface-variant flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px] text-secondary">
                          help
                        </span>
                        {" "}El valor inferior
                      </span>
                    </div>
                  </div>
                  {/* Mini indicador visual de categoría de tensión arterial */}
                  <div className="p-space-md rounded-xl bg-surface-container-low flex items-center justify-between transition-all" id="bpCategoryContainer">
                    <div className="flex items-center gap-space-sm">
                      <span className={bp.icon} id="bpIcon">
                        cardiology
                      </span>
                      {" "}
                      <div>
                        <div className="font-label-md font-semibold text-on-surface" id="bpCategoryTitle">
{bp.title}
</div>
                        <div className="font-label-sm text-on-surface-variant" id="bpCategorySub">
{bp.sub}
</div>
                      </div>
                    </div>
                    {" "}
                    <span className="font-label-sm text-secondary font-semibold px-space-sm py-1 bg-surface-container-lowest rounded-lg shadow-sm">
                      Modo preventivo
                    </span>
                  </div>
                  {/* Hábitos de Vida Interactivos (Sí / No) */}
                  <div className="flex flex-col gap-space-md pt-space-xs">
                    <div className="font-title-md text-body-lg font-semibold text-on-surface">
                      Factores modificables de estilo de vida
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
                      {/* Consumo de Tabaco */}
                      <div className="p-space-md rounded-xl bg-surface-container-low flex flex-col justify-between gap-space-sm">
                        <div className="flex items-center gap-space-sm">
                          <div className="w-8 h-8 rounded-lg bg-surface-container-lowest flex items-center justify-center text-primary shadow-sm shrink-0">
                            <span className="material-symbols-outlined text-[18px]">
                              smoking_rooms
                            </span>
                          </div>
                          <div>
                            <div className="font-label-md font-semibold text-on-surface">
                              Consumo de tabaco
                            </div>
                            <div className="font-label-sm text-on-surface-variant text-[11px]">
                              Cigarrillos o vapeo
                            </div>
                          </div>
                        </div>
                        <HabitButtons habit="tabaco" onChange={onChange} value={form.tabaco} />
                      </div>
                      {/* Consumo Frecuente de Alcohol */}
                      <div className="p-space-md rounded-xl bg-surface-container-low flex flex-col justify-between gap-space-sm">
                        <div className="flex items-center gap-space-sm">
                          <div className="w-8 h-8 rounded-lg bg-surface-container-lowest flex items-center justify-center text-secondary shadow-sm shrink-0">
                            <span className="material-symbols-outlined text-[18px]">
                              local_bar
                            </span>
                          </div>
                          <div>
                            <div className="font-label-md font-semibold text-on-surface">
                              Consumo de alcohol
                            </div>
                            <div className="font-label-sm text-on-surface-variant text-[11px]">
                              {">"} 3 dosis semanales
                            </div>
                          </div>
                        </div>
                        <HabitButtons habit="alcohol" onChange={onChange} value={form.alcohol} />
                      </div>
                      {/* Actividad Física Regular */}
                      <div className="p-space-md rounded-xl bg-surface-container-low flex flex-col justify-between gap-space-sm">
                        <div className="flex items-center gap-space-sm">
                          <div className="w-8 h-8 rounded-lg bg-surface-container-lowest flex items-center justify-center text-primary shadow-sm shrink-0">
                            <span className="material-symbols-outlined text-[18px]">
                              directions_run
                            </span>
                          </div>
                          <div>
                            <div className="font-label-md font-semibold text-on-surface">
                              Actividad regular
                            </div>
                            <div className="font-label-sm text-on-surface-variant text-[11px]">
                              ≥ 150 min/semana
                            </div>
                          </div>
                        </div>
                        <HabitButtons habit="ejercicio" onChange={onChange} value={form.ejercicio} />
                      </div>
                    </div>
                  </div>
                </section>
                {/* SECCIÓN 4: Nota Aclaratoria Visible */}
                <div className="bg-surface-container-low rounded-xl p-space-md flex items-start gap-space-md">
                  <div className="w-8 h-8 rounded-full bg-secondary-fixed flex items-center justify-center text-secondary shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-[18px]">
                      info
                    </span>
                  </div>
                  <div className="text-on-surface-variant font-label-md leading-relaxed">
                    <strong className="font-semibold text-on-surface block mb-0.5">
                      Nota importante para tu comodidad:
                    </strong>
                    {" "}No solicitamos análisis de sangre, colesterol ni glucosa para esta estimación inicial. Este cálculo temprano se enfoca en hábitos medibles y presión basal de acuerdo con las guías de tamizaje poblacional de la OMS y la ESC.
                  </div>
                </div>
                {visibleError && (
                  <div className="bg-error-container text-on-error-container rounded-xl p-space-md flex items-start gap-space-sm" role="alert">
                    <span className="material-symbols-outlined text-[20px] shrink-0">
                      error
                    </span>
                    <div className="font-label-md">
                      <strong className="font-semibold block">
                        No pudimos calcular tu resultado
                      </strong>
                      {visibleError}
                    </div>
                  </div>
                )}
                {/* SECCIÓN 5: Botones de Acción Inferiores */}
                <div className="pt-space-md flex flex-col sm:flex-row items-center justify-between gap-space-md">
                  <div className="flex items-center gap-space-sm w-full sm:w-auto">
                    {/* Guardar Borrador */}
                    <button className="px-space-md h-12 rounded-xl bg-surface-container-lowest text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors font-label-md font-semibold flex items-center justify-center gap-1.5 shadow-sm w-full sm:w-auto" onClick={() => showToast("Tus datos han sido guardados como borrador seguro.")} type="button">
                      <span className="material-symbols-outlined text-[18px]">
                        save
                      </span>
                      {" "}
                      <span>
                        Guardar borrador
                      </span>
                    </button>
                  </div>
                  <div className="flex items-center gap-space-sm w-full sm:w-auto">
                    {/* Paso Anterior */}
                    <button className="px-space-md h-12 rounded-xl bg-surface-container text-on-surface-variant hover:text-on-surface hover:bg-surface-variant transition-colors font-label-md font-semibold flex items-center justify-center gap-1.5 w-full sm:w-auto" onClick={() => showToast("Navegando a la revisión de datos iniciales...")} type="button">
                      <span className="material-symbols-outlined text-[18px]">
                        arrow_back
                      </span>
                      {" "}
                      <span>
                        Paso anterior
                      </span>
                    </button>
                    {/* Botón Primario Prominente: Ver mi resultado */}
                    <button className="px-space-lg h-12 rounded-xl bg-primary-container hover:bg-primary text-on-primary transition-all duration-200 font-label-md font-bold flex items-center justify-center gap-space-sm shadow-md hover:shadow-xl hover:shadow-primary/20 shrink-0 w-full sm:w-auto group disabled:opacity-70" disabled={loading} type="submit">
                      <span className="material-symbols-outlined text-[20px] text-on-primary group-hover:scale-110 transition-transform" style={{ fontVariationSettings: "'FILL' 1" }}>
                        favorite
                      </span>
                      {" "}
                      <span>
                        {loading ? "Calculando..." : "Ver mi resultado"}
                      </span>
                      {" "}
                      <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">
                        arrow_forward
                      </span>
                    </button>
                  </div>
                </div>
              </form>
            </div>
            {/* Columna Lateral: Panel de Contexto Clínico & Ayuda Rápida */}
            <div className="lg:col-span-4 flex flex-col gap-space-md">
              {/* Tarjeta de Resumen en Vivo del Paciente */}
              <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-md flex flex-col gap-space-md">
                <div className="flex items-center gap-space-sm">
                  <div className="w-10 h-10 rounded-xl bg-primary-fixed flex items-center justify-center text-primary font-bold">
                    <span className="material-symbols-outlined text-[20px]">
                      badge
                    </span>
                  </div>
                  <div>
                    <div className="font-title-md text-on-surface font-semibold">
                      Ficha en curso
                    </div>
                    <div className="font-label-sm text-on-surface-variant">
                      Clara Méndez · ID #CM-8821
                    </div>
                  </div>
                </div>
                <div className="bg-surface-container-low rounded-xl p-space-sm flex flex-col gap-space-xs text-on-surface-variant font-label-sm">
                  <div className="flex justify-between py-1 px-1">
                    <span>
                      Edad registrada:
                    </span>
                    {" "}
                    <span className="font-semibold text-on-surface" id="summaryEdad">
{`${form.edad} años`}
</span>
                  </div>
                  <div className="flex justify-between py-1 px-1">
                    <span>
                      Sexo biológico:
                    </span>
                    {" "}
                    <span className="font-semibold text-on-surface" id="summarySexo">
{form.sexo === "mujer" ? "Mujer" : "Hombre"}
</span>
                  </div>
                  <div className="flex justify-between py-1 px-1">
                    <span>
                      Estatura / Peso:
                    </span>
                    {" "}
                    <span className="font-semibold text-on-surface" id="summaryTalla">
{bmiValid ? `${estatura} cm / ${peso} kg` : "--"}
</span>
                  </div>
                  <div className="flex justify-between py-1 px-1">
                    <span>
                      Tensión Arterial:
                    </span>
                    {" "}
                    <span className="font-semibold text-primary" id="summaryBP">
{`${sys} / ${dia} mmHg`}
</span>
                  </div>
                  <div className="flex justify-between py-1 px-1">
                    <span>
                      Actividad física:
                    </span>
                    {" "}
                    <span className={form.ejercicio ? "font-semibold text-secondary" : "font-semibold text-tertiary"} id="summaryActividad">
{form.ejercicio ? "Activa (≥150 min)" : "Sedentaria (<150 min)"}
</span>
                  </div>
                </div>
                {/* Micro-visualización: Rango de Tensión Sistólica */}
                <div className="pt-space-xs flex flex-col gap-1.5">
                  <div className="flex justify-between text-label-sm">
                    <span className="text-on-surface-variant font-medium">
                      Escala Tensión Sistólica
                    </span>
                    {" "}
                    <span className="text-primary font-bold" id="scaleSysText">
{`${sys} mmHg`}
</span>
                  </div>
                  {/* Barra con segmentos de color clínicos sin bordes */}
                  <div className="h-3 w-full rounded-full bg-surface-container overflow-hidden flex relative">
                    <div className="h-full bg-secondary-fixed w-1/3" title="Óptima (<120)"></div>
                    <div className="h-full bg-surface-container-highest w-1/3" title="Normal Alta (120-139)"></div>
                    <div className="h-full bg-error-container w-1/3" title="Elevada (>140)"></div>
                    {/* Indicador de aguja en vivo */}
                    <div className="absolute top-0 bottom-0 w-1.5 bg-primary rounded-full transition-all duration-300 shadow-sm" id="sysPointer" style={{ left: `${pointerPercent}%` }}></div>
                  </div>
                  <div className="flex justify-between text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">
                    <span>
                      Normal ({"<"}120)
                    </span>
                    {" "}
                    <span>
                      Límite (130-139)
                    </span>
                    {" "}
                    <span>
                      Alerta ({">"}140)
                    </span>
                  </div>
                </div>
              </div>
              {/* Tarjeta de Recomendación para la toma de Presión */}
              <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-md flex flex-col gap-space-sm">
                <div className="flex items-center gap-space-sm">
                  <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center text-primary">
                    <span className="material-symbols-outlined text-[18px]">
                      tips_and_updates
                    </span>
                  </div>
                  <h3 className="font-label-md font-semibold text-on-surface">
                    ¿Cómo medir tu presión correctamente?
                  </h3>
                </div>
                <ul className="flex flex-col gap-space-xs font-label-sm text-on-surface-variant mt-1">
                  <li className="flex items-start gap-space-xs">
                    <span className="material-symbols-outlined text-[14px] text-secondary mt-0.5">
                      check_circle
                    </span>
                    {" "}
                    <span>
                      Reposa 5 minutos sentado antes del registro.
                    </span>
                  </li>
                  <li className="flex items-start gap-space-xs">
                    <span className="material-symbols-outlined text-[14px] text-secondary mt-0.5">
                      check_circle
                    </span>
                    {" "}
                    <span>
                      No tomes café ni fumes en los 30 minutos previos.
                    </span>
                  </li>
                  <li className="flex items-start gap-space-xs">
                    <span className="material-symbols-outlined text-[14px] text-secondary mt-0.5">
                      check_circle
                    </span>
                    {" "}
                    <span>
                      Apoya el brazo a la altura de tu corazón.
                    </span>
                  </li>
                </ul>
              </div>
              {/* Banner de Guía Clínica */}
              <div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm relative overflow-hidden">
                <div className="relative z-10 flex flex-col gap-space-xs">
                  <span className="font-label-sm uppercase font-semibold tracking-wider text-secondary">
                    Basado en evidencia
                  </span>
                  {" "}
                  <div className="font-title-md text-on-surface font-semibold">
                    Guías ESC / AHA 2024
                  </div>
                  <p className="font-label-sm text-on-surface-variant">
                    Tus valores se contrastan con algoritmos validados de riesgo cardiovascular para prevenir infartos e ictus.
                  </p>
                </div>
                {/* Decoración suave sutil en el fondo */}
                <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-surface-container rounded-full opacity-60 pointer-events-none"></div>
              </div>
            </div>
          </div>
          {/* Toast Notification flotante para acciones (Borrador guardado / Enrutamiento) */}
          <div className={`fixed bottom-6 right-6 bg-inverse-surface text-inverse-on-surface px-space-md py-space-sm rounded-xl shadow-xl flex items-center gap-space-sm transition-all duration-300 ${toastClasses} z-50`} id="toastNotification">
            <span className="material-symbols-outlined text-[20px] text-secondary-fixed">
              check_circle
            </span>
            {" "}
            <span className="font-label-md font-medium" id="toastMessage">
{toast.message || "Borrador guardado exitosamente."}
</span>
          </div>
        </div>
      </div>
    </main>
  );
}

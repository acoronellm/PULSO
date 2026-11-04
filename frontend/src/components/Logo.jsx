// Corazón con trazo de pulso, tomado de la pantalla de acceso de Stitch
export default function Logo({ className = "w-9 h-9" }) {
  return (
    <div className={`${className} rounded-xl bg-primary-container flex items-center justify-center text-on-primary shadow-md shrink-0`}>
      <svg className="w-3/5 h-3/5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" viewBox="0 0 24 24">
        <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path>
        <path d="M3.22 12H7l2-4 3 8 2.5-5 1.5 2h4.78" stroke="white" strokeWidth="2"></path>
      </svg>
    </div>
  );
}

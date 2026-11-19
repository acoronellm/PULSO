# React + Vite

## Pruebas de integración frontend/backend

Las pruebas PI-05 a PI-07 usan Vitest Browser Mode con Chromium real y Testing Library.
Requieren que el stack local esté activo (`docker compose up --build -d` desde la raíz
del repositorio), incluyendo un backend configurado para conectarse al RAG para PI-05.

Instala el navegador de pruebas una vez:

```sh
npm install
npx playwright install chromium
```

Ejecuta estas pruebas desde `frontend`:

```sh
npm run test:integration
```

Las solicitudes usan el proxy de Vite hacia `http://127.0.0.1:8000`. Para apuntar a
otro backend local, configura `VITE_PROXY_TARGET` antes de ejecutar Vitest. Las pruebas
usan el perfil ficticio del formulario y no reemplazan las llamadas HTTP del frontend.

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

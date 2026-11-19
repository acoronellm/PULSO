import react from "@vitejs/plugin-react";
import { playwright } from "@vitest/browser-playwright";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000",
    },
  },
  test: {
    include: ["src/integration/**/*.browser.test.tsx"],
    globals: true,
    setupFiles: "./src/integration/browserSetup.ts",
    testTimeout: 120_000,
    hookTimeout: 20_000,
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [{ browser: "chromium" }],
      headless: true,
    },
  },
});

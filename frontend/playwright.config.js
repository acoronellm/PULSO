import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/integration",

  timeout: 120000,

  expect: {
    timeout: 10000,
  },

  use: {
    baseURL: "http://127.0.0.1:5173",
    headless: true,
  },

  webServer: {
    command: "npm run dev -- --host 127.0.0.1",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: true,
    timeout: 120000,
    env: {
      ...process.env,
      VITE_API_URL: "http://localhost:8000",
    },
  },
});
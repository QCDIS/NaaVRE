import { defineConfig } from "cypress";

export default defineConfig({
  baseUrl: "http://localhost:8888?token=abcd",
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});

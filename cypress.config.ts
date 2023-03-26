import { defineConfig } from 'cypress'

export default defineConfig({
  numTestsKeptInMemory: 10,
  screenshotsFolder: './build/cypress-tests/screenshots',
  video: false,
  videosFolder: './build/cypress-tests/videos',
  videoUploadOnPasses: false,
  fixturesFolder: false,
  defaultCommandTimeout: 8000,
  execTimeout: 120000,
  pageLoadTimeout: 120000,
  responseTimeout: 60000,
  viewportWidth: 1400,
  viewportHeight: 800,
  retries: {
    runMode: 1,
    openMode: 1,
  },
  e2e: {
    setupNodeEvents(on, config) {},
    baseUrl: 'http://localhost:8888/lab',
    specPattern: './cypress/integration/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: './cypress/support/commands.ts'
  },
})

import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://172.17.0.1:8888/lab',
  },
})
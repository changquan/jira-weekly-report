import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Override when the backend isn't on the default port, e.g.
// BACKEND_URL=http://localhost:8001 npm run dev
const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    // The repo lives on /mnt/c, where WSL gets no file-change events; poll instead.
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': backendUrl,
      '/health': backendUrl,
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
  },
})

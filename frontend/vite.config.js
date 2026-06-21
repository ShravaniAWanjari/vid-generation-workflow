import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'force-exit-after-build',
      apply: 'build',
      closeBundle() {
        console.log('Build completed, forcing exit...');
        process.exit(0);
      }
    }
  ],
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Get all mp4 files in the public directory
const publicDir = path.resolve(__dirname, 'public');
const files = fs.existsSync(publicDir) ? fs.readdirSync(publicDir) : [];
const videoFiles = files.filter(f => f.endsWith('.mp4'));

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  },
  define: {
    __AVAILABLE_VIDEOS__: JSON.stringify(videoFiles)
  },
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

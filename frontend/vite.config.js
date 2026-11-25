import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
function defaultLocaleHtml() {
  return {
    name: 'default-locale-html',
    transformIndexHtml(html) {
      const raw = process.env.VITE_DEFAULT_LOCALE || 'es'
      const prefix = String(raw).toLowerCase().split(/[-_]/)[0]
      const locale = ['es', 'en', 'zh'].includes(prefix) ? prefix : 'es'
      return html.replaceAll('__MIROFISH_DEFAULT_LOCALE__', locale)
    }
  }
}

export default defineConfig({
  plugins: [vue(), defaultLocaleHtml()],
  envDir: path.resolve(__dirname, '..'),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@locales': path.resolve(__dirname, '../locales')
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      }
    }
  }
})

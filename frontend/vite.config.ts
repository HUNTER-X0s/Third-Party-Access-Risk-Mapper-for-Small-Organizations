import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
  ],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    // Target modern browsers — smaller, faster output
    target: 'es2020',

    // Raise warning threshold (we already know the bundle; suppress noise)
    chunkSizeWarningLimit: 600,

    // Minification
    minify: 'esbuild',

    // CSS code-splitting: each async chunk gets its own CSS
    cssCodeSplit: true,

    // Source maps off in production (faster load, no source leakage)
    sourcemap: false,

    rollupOptions: {
      output: {
        // Manual chunk splitting — keeps vendor libs separate so they can be
        // cached independently from app code changes.
        manualChunks: {
          // React core — almost never changes
          'vendor-react': ['react', 'react-dom'],

          // Heavy graph library — only loaded on Access Map tab
          'vendor-reactflow': ['@xyflow/react'],

          // Lucide icons — shared everywhere but large
          'vendor-lucide': ['lucide-react'],

          // App-specific heavy pages (split so dashboard loads fast)
          'page-graph': [
            './src/components/AccessGraphView.tsx',
          ],
          'page-monitoring': [
            './src/pages/MonitoringPage.tsx',
          ],
          'page-vendors': [
            './src/pages/VendorsPage.tsx',
          ],
          'page-connectors': [
            './src/pages/ConnectorsPage.tsx',
          ],
        },

        // Stable filenames with content hash for long-term caching
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },

  // Optimize deps — pre-bundle heavy CJS packages for fast dev HMR
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'lucide-react',
      '@xyflow/react',
    ],
  },
});

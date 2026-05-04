import tailwindcss from '@tailwindcss/vite';
import { defineConfig, PluginOption } from 'vite';
import solidPlugin from 'vite-plugin-solid';

const watchPlugin: PluginOption = {
  name: "watch plugin",
  
}

export default defineConfig({
  plugins: [ solidPlugin(), tailwindcss(), ],
  server: {
    port: 3000,
  },
  build: {
    target: 'esnext',
  },
});

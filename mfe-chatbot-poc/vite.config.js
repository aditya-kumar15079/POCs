import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), cssInjectedByJsPlugin()],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"), // 👈 inject manually
  },
  build: {
    lib: {
      entry: "src/mfe-entry.jsx",
      name: "ChatBot",
      fileName: "chat-bot",
      formats: ["iife"],
    },
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
        },
      },
    },
  },
});

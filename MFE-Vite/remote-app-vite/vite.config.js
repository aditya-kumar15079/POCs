import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite";
import svgr from "vite-plugin-svgr";
import path from "path";
import federation from "@originjs/vite-plugin-federation";
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js';

export default defineConfig({
  plugins: [
    react(),
    svgr(),
    tailwindcss(),
    federation({
      name: "chatbot_mfe",
      filename: "remoteEntry.js",
      exposes: {
        "./ChatRoot": "./src/bootstrap.jsx",
        "./chatbotReducer": "./src/reducer/chatbotReducer.js",
      },
      shared: {
        react: {
          singleton: true,
          requiredVersion: false,
          eager: false,
        },
        "react-dom": {
          singleton: true,
          requiredVersion: false,
          eager: false,
        },
        "react-redux": {
          singleton: true,
          requiredVersion: false,
        },
        redux: {
          singleton: true,
          requiredVersion: false,
        },
        "@reduxjs/toolkit": {
          singleton: true,
          requiredVersion: false,
        },
      },
    }),
    cssInjectedByJsPlugin(),
  ],
  build: {
    target: "esnext",
    cssCodeSplit: false,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src/app"),
    },
  },
});

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "./",
  plugins: [react()],
  root: "./renderer",
  build: {
    outDir: "../dist",
    emptyOutDir: true,
  },
});

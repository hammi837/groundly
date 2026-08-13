import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, "src/index.ts"),
      name: "GroundlyWidget",
      formats: ["iife"],
      fileName: () => "widget.js",
    },
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true,
    minify: true,
  },
  server: {
    port: 5174,
    open: "/demo.html",
  },
  publicDir: "public",
});

import { screenGraphPlugin } from "@animaapp/vite-plugin-screen-graph";
import react from "@vitejs/plugin-react";
import tailwind from "tailwindcss";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    mode === "development" && screenGraphPlugin()
  ].filter(Boolean),
  publicDir: "public",
  base: "./",
  css: {
    postcss: {
      plugins: [tailwind()],
    },
  },
  // === 프록시 설정 추가 ===
  server: {
    proxy: {
      // 1. 백엔드에서 직접 서빙하는 HTML 페이지들
      "/schedule": "http://localhost:8000",
      "/auth": "http://localhost:8000",
      "/login": "http://localhost:8000",
      "/home": "http://localhost:8000",
      
      // 2. API 요청들 (main.py에 정의된 @app.post 등)
      "/parse-multi-schedule": "http://localhost:8000",
      "/check_duplicates": "http://localhost:8000",
      "/register-google-calendar": "http://localhost:8000",
    },
  },
}));
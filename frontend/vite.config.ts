import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import path from "path"

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    define: {
      // Only expose the browser-safe Key ID, not Razorpay secrets.
      "import.meta.env.ROZAR_PAY_API_KEY": JSON.stringify(
        env.ROZAR_PAY_API_KEY ?? "",
      ),
    },
    plugins: [react(), tailwindcss(),],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  };
})

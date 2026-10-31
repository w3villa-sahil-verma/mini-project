import type { FetchConfig } from "@/hooks/useFetch";

export const API_CONFIG: FetchConfig = {
  baseUrl: import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
  credentials: 'include'
};
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { RouterProvider } from 'react-router'
import { router } from './routes.ts'
import { Toaster } from "sonner";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Toaster
        position="top-right"
        richColors
        closeButton
      />
    <RouterProvider router={router} />,
  </StrictMode>,
)

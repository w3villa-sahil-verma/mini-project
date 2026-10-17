import { createBrowserRouter, redirect } from "react-router";
import { Home } from "./pages/home";
import { Pricing } from "./pages/pricing";
import { Profile } from "./pages/profile";
import { Login } from "./pages/login";
import { Register } from "./pages/register";
import { Dashboard } from "./pages/dashboard";
import { PrimaryLayout } from "./layouts/primary";

export const router = createBrowserRouter([
  {
    path: "/",
    // Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "profile", Component: Profile },
      { path: "pricing", Component: Pricing },
      { path: "register", Component: Register },
      { path: "login", Component: Login },
      { path: "dashboard", Component: Dashboard },
      {
        path: "auth",
        Component: PrimaryLayout,
        children: [
          {
            index: true,
            loader: () => redirect("dashboard"),
          },
          {
            path: "dashboard",
            Component: Dashboard,
          },
        ],
      },
    ],
  },
]);

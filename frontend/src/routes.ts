import { createBrowserRouter, redirect } from "react-router";
import { Home } from "./pages/home";
import { Pricing } from "./pages/pricing";
import { Profile } from "./pages/profile";
import { Login } from "./pages/login";
import { Register } from "./pages/register";
import { Dashboard } from "./pages/dashboard";
import { PrimaryLayout } from "./layouts/primary";
import { Plan } from "./pages/plan";
import { Users } from "./pages/user/users.page";

export const router = createBrowserRouter([
  {
    path: "/",
    // Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "register", Component: Register },
      { path: "login", Component: Login },
      {
        path: "user",
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
          {
            path: "profile",
            Component: Dashboard,
          },
          {
            path: "plans",
            Component: Dashboard,
          },
        ],
      },
      {
        path: "admin",
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
          {
            path: "users",
            Component: Users,
          },
          {
            path: "plans",
            Component: Plan,
          },
        ],
      },
    ],
  },
]);

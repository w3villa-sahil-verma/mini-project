import { createBrowserRouter, redirect } from "react-router";
import { Home } from "./pages/home";
import { Login } from "./pages/login";
import { Register } from "./pages/register";
import { Dashboard } from "./pages/dashboard";
import { PrimaryLayout } from "./layouts/primary";
import { Plan } from "./pages/plan";
import { Users } from "./pages/user/users.page";
import Pricing from "./components/shadcn-space/blocks/pricing-02/pricing";

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
            Component: Pricing,
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
            path: "profile",
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

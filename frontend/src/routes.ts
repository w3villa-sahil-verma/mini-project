import { createBrowserRouter, redirect } from "react-router";
import { Home } from "./pages/home";
import { Login } from "./pages/login";
import { Register } from "./pages/register";
import { Dashboard } from "./pages/dashboard";
import { PrimaryLayout } from "./layouts/primary";
import { Plan } from "./pages/plan";
import { Users } from "./pages/user/users.page";
import { handleFetch } from "./hooks/useFetch";
import type { CommonResponse } from "./types/common/request";
import { logger } from "./utils/logger";

import { createContext } from "react-router";
import { toast } from "sonner";
import type { User } from "./types/common/user";
import { ProfilePage } from "./pages/profile";
import { PricingPage } from "./pages/pricing";
import { GalleryPage } from "./pages/gallery";
import { AdminGalleryPage } from "./pages/admin/gallery";


export const userContext = createContext<User | null>(null);

export const router = createBrowserRouter([
  {
    id: 'root',
    path: "/",
    middleware: [
      async ({ context }) => {
        await handleFetch<CommonResponse<User>>(
          "/api/v1/auth/me",
          (resp) => {
            const user = resp.data;
            context.set(userContext, user);
          },
          (err) => {
            logger.error(err.message);
            toast.error(err.message);
            context.set(userContext, null);
            redirect("/");
          },
        );
      },
    ],
    loader: ({ context }) => {
      const user = context.get(userContext);
      return { user };
    },
    children: [
      {
        index: true,
        Component: Home,
      },
      { path: "register", Component: Register },
      { path: "login", Component: Login },
      { path: "gallary", Component: GalleryPage },
      {
        path: "user",
        Component: PrimaryLayout,
        middleware: [
          ({ context }) => {
            const user = context.get(userContext);
            if (!user) return redirect("/");
            if (user.role === "ADMIN") return redirect("/admin");
          },
        ],
        children: [
          {
            index: true,
            loader: () => redirect("pricing"),
          },
          {
            path: "profile",
            Component: ProfilePage,
          },
          {
            path: "pricing",
            Component: PricingPage,
          },
        ],
      },
      {
        path: "admin",
        Component: PrimaryLayout,
        middleware: [
          ({ context }) => {
            const user = context.get(userContext);

            if (!user) return redirect("/");

            if (user.role === "USER") return redirect("/user");
          },
        ],
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
            Component: ProfilePage,
          },
          {
            path: "users",
            Component: Users,
          },
          {
            path: "plans",
            Component: Plan,
          },
          {
            path: "gallery",
            Component: AdminGalleryPage,
          },
        ],
      },
    ],
  },
]);

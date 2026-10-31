import * as React from "react";

import { NavMain } from "@/components/nav-main";
import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import {
  IconDashboard,
  IconListDetails,
  IconFolder,
  IconUsers,
  IconInnerShadowTop,
} from "@tabler/icons-react";
import { Link, useRouteLoaderData } from "react-router";
import type { User } from "@/types/common/user";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user } = useRouteLoaderData<{ user: User | null }>("root")!;

  const role = user?.role || "USER";

  const user_nav = [
    {
      title: "Pricing",
      url: "/user/pricing",
      icon: <IconFolder />,
    },
    {
      title: "Profile",
      url: "/user/profile",
      icon: <IconListDetails />,
    },
  ];

  const admin_nav = [
    {
      title: "Dashboard",
      url: "/admin/dashboard",
      icon: <IconDashboard />,
    },
    {
      title: "Profile",
      url: "/admin/profile",
      icon: <IconListDetails />,
    },
    {
      title: "Plans",
      url: "/admin/plans",
      icon: <IconFolder />,
    },
    {
      title: "Users",
      url: "/admin/users",
      icon: <IconUsers />,
    },
  ];

  const NAV = {
    USER: user_nav,
    ADMIN: admin_nav,
  };

  const data = {
    user: {
      name: "shadcn",
      email: user?.user_id || "m@example.com",
      avatar: "/avatars/shadcn.jpg",
    },
    navMain: NAV[role],
  };
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <Link to={"/"}>
            <SidebarMenuItem>
              <SidebarMenuButton className="data-[slot=sidebar-menu-button]:p-1.5!">
                <IconInnerShadowTop className="size-5!" />
                <span className="text-base font-semibold">
                  Membership Managment
                </span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </Link>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  );
}

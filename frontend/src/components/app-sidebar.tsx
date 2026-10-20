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
  IconChartBar,
  IconFolder,
  IconUsers,
  IconInnerShadowTop,
} from "@tabler/icons-react";
import { Link } from "react-router";

const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/admin/dashboard",
      icon: <IconDashboard />,
    },
    {
      title: "Page Hosting",
      url: "#",
      icon: <IconListDetails />,
    },
    {
      title: "Analytics",
      url: "#",
      icon: <IconChartBar />,
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
  ],
};
export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <Link to={"/"}>
          <SidebarMenuItem>
            <SidebarMenuButton
              className="data-[slot=sidebar-menu-button]:p-1.5!"
            >
              <IconInnerShadowTop className="size-5!" />
              <span className="text-base font-semibold">ABC Membership Managment</span>
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

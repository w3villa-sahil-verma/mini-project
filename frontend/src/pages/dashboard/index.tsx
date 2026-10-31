import { useEffect, useState } from "react";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { handleFetch } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";

type DashboardPlan = {
  id: number;
  name: string;
  duration_hours: number;
  price_minor: number;
  currency: string;
  is_active: boolean;
};

type DashboardUser = {
  id: number;
  email: string;
  role: string;
  created_at: string;
};

type MonthlyCount = {
  month: string;
  count: number;
};

type UpcomingExpiration = {
  id: number;
  user_email: string;
  plan_name: string;
  status: string;
  starts_at: string | null;
  expires_at: string | null;
};

type DashboardData = {
  summary: {
    total_plans: number;
    active_subscriptions: number;
    expired_subscriptions: number;
    total_users: number;
  };
  plans: DashboardPlan[];
  recent_users: DashboardUser[];
  user_registrations: MonthlyCount[];
  subscriptions_by_month: MonthlyCount[];
  upcoming_expirations: UpcomingExpiration[];
  recent_expirations: {
    id: number;
    user_email: string;
    plan_name: string;
    expires_at: string | null;
  }[];
};

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatDuration(hours: number) {
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  if (days === 0) return `${hours} hours`;
  if (remainingHours === 0) return `${days} days`;
  return `${days} days, ${remainingHours} hours`;
}

function formatPrice(priceMinor: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
  }).format(priceMinor / 100);
}

function MetricCard({
  label,
  value,
  description,
  loading,
}: {
  label: string;
  value: number | undefined;
  description: string;
  loading: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        {loading ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <CardTitle className="text-3xl tabular-nums">{value ?? 0}</CardTitle>
        )}
        <CardDescription>{description}</CardDescription>
      </CardHeader>
    </Card>
  );
}

function MonthlyChart({
  title,
  description,
  data,
  label,
  color,
}: {
  title: string;
  description: string;
  data: MonthlyCount[];
  label: string;
  color: string;
}) {
  const chartConfig = {
    count: { label, color },
  } satisfies ChartConfig;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-60 w-full">
          <AreaChart data={data} margin={{ left: 8, right: 8 }}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={24}
            />
            <ChartTooltip
              content={<ChartTooltipContent indicator="dot" />}
            />
            <Area
              dataKey="count"
              type="monotone"
              fill="var(--color-count)"
              fillOpacity={0.2}
              stroke="var(--color-count)"
              strokeWidth={2}
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

export function Dashboard() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    void handleFetch<CommonResponse<DashboardData>>(
      "/api/v1/admin/dashboard",
      (response) => {
        if (!active) return;
        setDashboard(response.data);
        setError(null);
      },
      (requestError) => {
        if (!active) return;
        setError(requestError.message);
      },
    ).finally(() => {
      if (active) setLoading(false);
    });

    return () => {
      active = false;
    };
  }, []);

  const summary = dashboard?.summary;

  return (
    <div className="flex flex-1 flex-col gap-6 p-4 md:p-6">
      <header>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Overview of gym members, plans, and subscriptions.
        </p>
      </header>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-destructive"
        >
          Unable to load dashboard data: {error}
        </div>
      )}

      <section
        aria-label="Dashboard summary"
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <MetricCard
          label="Plans"
          value={summary?.total_plans}
          description="Plans configured in the system"
          loading={loading}
        />
        <MetricCard
          label="Active subscriptions"
          value={summary?.active_subscriptions}
          description="Memberships active right now"
          loading={loading}
        />
        <MetricCard
          label="Users"
          value={summary?.total_users}
          description="Registered, non-deleted members"
          loading={loading}
        />
        <MetricCard
          label="Expired subscriptions"
          value={summary?.expired_subscriptions}
          description="Memberships whose duration has ended"
          loading={loading}
        />
      </section>

      {dashboard && (
        <>
          <section
            aria-label="Monthly activity"
            className="grid gap-4 xl:grid-cols-2"
          >
            <MonthlyChart
              title="User registrations"
              description="New member registrations over the last 12 months"
              data={dashboard.user_registrations}
              label="Registrations"
              color="var(--chart-1)"
            />
            <MonthlyChart
              title="Subscriptions"
              description="Subscriptions created over the last 12 months"
              data={dashboard.subscriptions_by_month}
              label="Subscriptions"
              color="var(--chart-2)"
            />
          </section>

          <section className="grid gap-4 xl:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Plans</CardTitle>
                <CardDescription>
                  Membership plans and their current availability.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Duration</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dashboard.plans.map((plan) => (
                      <TableRow key={plan.id}>
                        <TableCell className="font-medium">{plan.name}</TableCell>
                        <TableCell>{formatDuration(plan.duration_hours)}</TableCell>
                        <TableCell>
                          {formatPrice(plan.price_minor, plan.currency)}
                        </TableCell>
                        <TableCell>
                          {plan.is_active ? "Active" : "Inactive"}
                        </TableCell>
                      </TableRow>
                    ))}
                    {dashboard.plans.length === 0 && (
                      <TableRow>
                        <TableCell
                          colSpan={4}
                          className="h-20 text-center text-muted-foreground"
                        >
                          No plans found.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent users</CardTitle>
                <CardDescription>
                  The latest registered members.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Registered</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dashboard.recent_users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell className="font-medium">
                          {user.email}
                        </TableCell>
                        <TableCell>{user.role}</TableCell>
                        <TableCell>{formatDate(user.created_at)}</TableCell>
                      </TableRow>
                    ))}
                    {dashboard.recent_users.length === 0 && (
                      <TableRow>
                        <TableCell
                          colSpan={3}
                          className="h-20 text-center text-muted-foreground"
                        >
                          No users found.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </section>

          <Card>
            <CardHeader>
              <CardTitle>Upcoming subscription end periods</CardTitle>
              <CardDescription>
                Active and scheduled subscriptions ordered by expiration date.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Member</TableHead>
                    <TableHead>Plan</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Starts</TableHead>
                    <TableHead>Ends</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dashboard.upcoming_expirations.map((subscription) => (
                    <TableRow key={subscription.id}>
                      <TableCell className="font-medium">
                        {subscription.user_email}
                      </TableCell>
                      <TableCell>{subscription.plan_name}</TableCell>
                      <TableCell>{subscription.status}</TableCell>
                      <TableCell>{formatDate(subscription.starts_at)}</TableCell>
                      <TableCell>{formatDate(subscription.expires_at)}</TableCell>
                    </TableRow>
                  ))}
                  {dashboard.upcoming_expirations.length === 0 && (
                    <TableRow>
                      <TableCell
                        colSpan={5}
                        className="h-20 text-center text-muted-foreground"
                      >
                        No upcoming subscription expirations.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recently expired subscriptions</CardTitle>
              <CardDescription>
                Memberships whose access period has ended.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Member</TableHead>
                    <TableHead>Plan</TableHead>
                    <TableHead>Expired</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dashboard.recent_expirations.map((subscription) => (
                    <TableRow key={subscription.id}>
                      <TableCell className="font-medium">
                        {subscription.user_email}
                      </TableCell>
                      <TableCell>{subscription.plan_name}</TableCell>
                      <TableCell>{formatDate(subscription.expires_at)}</TableCell>
                    </TableRow>
                  ))}
                  {dashboard.recent_expirations.length === 0 && (
                    <TableRow>
                      <TableCell
                        colSpan={3}
                        className="h-20 text-center text-muted-foreground"
                      >
                        No expired subscriptions found.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

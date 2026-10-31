import * as React from "react";
import { toast } from "sonner";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { handleFetch } from "@/hooks/useFetch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { CommonResponse } from "@/types/common/request";

const userSchema = z.object({
  id: z.number(),
  email: z.string(),
  full_name: z.string(),
  role: z.enum(["ADMIN", "USER"]),
  is_deleted: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

type User = z.infer<typeof userSchema>;
const userListSchema = z.object({
  items: z.array(userSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
  total_pages: z.number(),
});
type UserList = z.infer<typeof userListSchema>;

const API = "/api/v1/admin/users";
const PAGE_SIZE_OPTIONS = [10, 20, 50] as const;

export function UsersTable() {
  const [users, setUsers] = React.useState<UserList>({
    items: [],
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 0,
  });
  const [search, setSearch] = React.useState("");
  const [role, setRole] = React.useState("all");
  const [status, setStatus] = React.useState("all");
  const [page, setPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(20);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let active = true;
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
        status,
      });
      if (search.trim()) params.set("search", search.trim());
      if (role !== "all") params.set("role", role);

      setLoading(true);
      setError(null);
      void handleFetch<CommonResponse<UserList>>(
        `${API}?${params.toString()}`,
        (response) => {
          if (!active) return;
          const parsed = userListSchema.safeParse(response.data);
          if (!parsed.success) {
            const message = "Unexpected users data format.";
            setError(message);
            toast.error(message);
            return;
          }
          setUsers(parsed.data);
        },
        (requestError) => {
          if (!active) return;
          setError(requestError.message);
          toast.error(requestError.message);
        },
      ).finally(() => {
        if (active) setLoading(false);
      });
    }, search ? 300 : 0);

    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [page, pageSize, role, search, status]);

  const updateFilter = (update: () => void) => {
    update();
    setPage(1);
  };

  return (
    <section className="w-full space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Users</h1>
        <p className="text-sm text-muted-foreground">
          Search and filter registered users, then browse the results by page.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[minmax(16rem,1fr)_12rem_12rem_10rem]">
        <Input
          aria-label="Search users"
          placeholder="Search name, email, phone, or ID"
          value={search}
          onChange={(event) =>
            updateFilter(() => setSearch(event.currentTarget.value))
          }
        />
        <select
          aria-label="Filter users by role"
          value={role}
          onChange={(event) => updateFilter(() => setRole(event.target.value))}
          className="h-9 rounded-lg border border-input bg-background px-3 text-sm"
        >
          <option value="all">All roles</option>
          <option value="USER">User</option>
          <option value="ADMIN">Admin</option>
        </select>
        <select
          aria-label="Filter users by status"
          value={status}
          onChange={(event) =>
            updateFilter(() => setStatus(event.target.value))
          }
          className="h-9 rounded-lg border border-input bg-background px-3 text-sm"
        >
          <option value="all">All statuses</option>
          <option value="active">Active</option>
          <option value="deleted">Deleted</option>
        </select>
        <select
          aria-label="Users per page"
          value={pageSize}
          onChange={(event) =>
            updateFilter(() => setPageSize(Number(event.target.value)))
          }
          className="h-9 rounded-lg border border-input bg-background px-3 text-sm"
        >
          {PAGE_SIZE_OPTIONS.map((size) => (
            <option key={size} value={size}>
              {size} per page
            </option>
          ))}
        </select>
      </div>

      {error && (
        <p className="text-sm text-destructive" role="alert">
          Could not load users: {error}
        </p>
      )}

      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created At</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  Loading users...
                </TableCell>
              </TableRow>
            ) : users.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  {error ? "Users could not be loaded." : "No users found."}
                </TableCell>
              </TableRow>
            ) : (
              users.items.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.id}</TableCell>
                  <TableCell className="font-medium">
                    {user.full_name || "Not provided"}
                  </TableCell>
                  <TableCell className="font-medium">{user.email}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>
                    <Badge
                      variant={user.is_deleted ? "destructive" : "default"}
                    >
                      {user.is_deleted ? "Deleted" : "Active"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground" aria-live="polite">
          {users.total === 0
            ? "0 users"
            : `Showing ${(page - 1) * pageSize + 1}–${Math.min(
                page * pageSize,
                users.total,
              )} of ${users.total} users`}
        </p>
        <div className="flex items-center justify-between gap-3 sm:justify-end">
          <span className="text-sm text-muted-foreground">
            Page {users.total_pages === 0 ? 0 : page} of {users.total_pages}
          </span>
          <Button
            variant="outline"
            disabled={loading || page <= 1}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            disabled={loading || page >= users.total_pages}
            onClick={() => setPage((current) => current + 1)}
          >
            Next
          </Button>
        </div>
      </div>
    </section>
  );
}

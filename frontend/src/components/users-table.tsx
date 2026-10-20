import * as React from "react";
import { toast } from "sonner";
import { useFetch } from "@/hooks/useFetch";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
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
  role: z.enum(["ADMIN", "USER"]),
  is_deleted: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

type User = z.infer<typeof userSchema>;

const API = "/api/v1/admin/users";

export function UsersTable() {
  const [users, setUsers] = React.useState<User[]>([]);

  const [loading] = useFetch<CommonResponse<User[]>>(
    API,
    (resp) => {
      const parsed = z.array(userSchema).safeParse(resp.data);

      if (!parsed.success) {
        toast.error("Unexpected users data format.");
        return;
      }

      setUsers(parsed.data);
    },
    (err) => {
      toast.error(err.message);
    },
    [],
  );

  return (
    <section className="w-full space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Users</h1>
        <p className="text-sm text-muted-foreground">
          View all registered users.
        </p>
      </div>

      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created At</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  Loading users...
                </TableCell>
              </TableRow>
            ) : users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  No users found.
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.id}</TableCell>
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
    </section>
  );
}

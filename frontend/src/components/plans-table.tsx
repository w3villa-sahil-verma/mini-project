import * as React from "react";
import { toast } from "sonner";
import { handleFetch } from "@/hooks/useFetch";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { CommonResponse } from "@/types/common/request";

const planSchema = z.object({
  id: z.number(),
  name: z.string(),
  duration_hours: z.number(),
  price_minor: z.number(),
  currency: z.string(),
  is_active: z.boolean(),
});
type Plan = z.infer<typeof planSchema>;
const formSchema = z.object({
  name: z.string().trim().min(1, "Plan name is required").max(50),
  duration_hours: z.number().int().positive("Duration must be at least 1 hour"),
  price_minor: z.number().int().nonnegative("Price cannot be negative"),
  currency: z.string().trim().length(3, "Use a 3-letter currency code"),
  is_active: z.boolean(),
});
type PlanForm = z.infer<typeof formSchema>;
const emptyForm: PlanForm = {
  name: "",
  duration_hours: 1,
  price_minor: 0,
  currency: "INR",
  is_active: true,
};
const API = "/api/v1/admin/plans";

function request<T>(url: string, options?: RequestInit): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    void handleFetch<T>(
      url,
      (payload) => resolve(payload),
      (error) => reject(error),
      {
        credentials: "include",
        headers: { "Content-Type": "application/json", ...options?.headers },
        ...options,
      },
    );
  });
}
function money(minor: number, currency: string) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency.toUpperCase(),
  }).format(minor / 100);
}

export function PlansTable() {
  const [plans, setPlans] = React.useState<Plan[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [open, setOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<Plan | null>(null);
  const [form, setForm] = React.useState<PlanForm>(emptyForm);
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [search, setSearch] = React.useState("");

  const loadPlans = React.useCallback(async () => {
    setLoading(true);
    try {
      const resp = await request<CommonResponse<Plan[]>>(API);
      const parsed = z.array(planSchema).safeParse(resp.data);
      if (!parsed.success)
        throw new Error("Plans API returned an unexpected data format.");
      setPlans(parsed.data);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not load plans.");
    } finally {
      setLoading(false);
    }
  }, []);
  React.useEffect(() => {
    void loadPlans();
  }, [loadPlans]);

  function createPlan() {
    setEditing(null);
    setForm(emptyForm);
    setErrors({});
    setOpen(true);
  }
  function editPlan(plan: Plan) {
    setEditing(plan);
    setForm({
      name: plan.name,
      duration_hours: plan.duration_hours,
      price_minor: plan.price_minor,
      currency: plan.currency,
      is_active: plan.is_active,
    });
    setErrors({});
    setOpen(true);
  }
  function field<K extends keyof PlanForm>(key: K, value: PlanForm[K]) {
    setForm((old) => ({ ...old, [key]: value }));
    setErrors((old) => ({ ...old, [key]: "" }));
  }
  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = formSchema.safeParse({
      ...form,
      name: form.name.trim(),
      currency: form.currency.trim().toUpperCase(),
    });
    if (!result.success) {
      const next: Record<string, string> = {};
      result.error.issues.forEach((issue) => {
        next[String(issue.path[0] ?? "form")] = issue.message;
      });
      setErrors(next);
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        await request(`${API}/${editing.id}`, {
          method: "PATCH",
          body: JSON.stringify(result.data),
        });
        toast.success("Plan updated.");
      } else {
        await request(API, {
          method: "POST",
          body: JSON.stringify(result.data),
        });
        toast.success("Plan created.");
      }
      setOpen(false);
      await loadPlans();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not save plan.");
    } finally {
      setSaving(false);
    }
  }
  async function toggleActive(plan: Plan) {
    try {
      await request(`${API}/${plan.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !plan.is_active }),
      });
      toast.success(plan.is_active ? "Plan deactivated." : "Plan activated.");
      await loadPlans();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not update plan.");
    }
  }
  async function removePlan(plan: Plan) {
    if (
      !window.confirm(
        `Delete the ${plan.name} plan? If subscriptions reference it, deactivate it instead.`,
      )
    )
      return;
    try {
      await request(`${API}/${plan.id}`, { method: "DELETE" });
      toast.success("Plan deleted.");
      await loadPlans();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not delete plan.");
    }
  }
  const visible = plans.filter((p) =>
    `${p.name} ${p.currency}`.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <section className="w-full space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Plan management
          </h1>
          <p className="text-sm text-muted-foreground">
            Create and manage SubTrack subscription plans.
          </p>
        </div>
        <Button onClick={createPlan}>Add plan</Button>
      </div>
      <div className="flex items-center gap-3">
        <Input
          aria-label="Search plans"
          placeholder="Search plans..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
        <span className="text-sm text-muted-foreground">
          {visible.length} plan(s)
        </span>
      </div>
      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  Loading plans...
                </TableCell>
              </TableRow>
            ) : visible.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  No plans found.
                </TableCell>
              </TableRow>
            ) : (
              visible.map((plan) => (
                <TableRow key={plan.id}>
                  <TableCell className="font-medium">{plan.name}</TableCell>
                  <TableCell>
                    {plan.duration_hours} hour
                    {plan.duration_hours === 1 ? "" : "s"}
                  </TableCell>
                  <TableCell>
                    {money(plan.price_minor, plan.currency)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={plan.is_active ? "default" : "secondary"}>
                      {plan.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => editPlan(plan)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => void toggleActive(plan)}
                      >
                        {plan.is_active ? "Deactivate" : "Activate"}
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => void removePlan(plan)}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Edit plan" : "Create plan"}</DialogTitle>
            <DialogDescription>
              Set the plan name, duration, price and availability.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={save} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="plan-name">Plan name</Label>
              <Input
                id="plan-name"
                value={form.name}
                onChange={(e) => field("name", e.target.value)}
                required
              />
              {errors.name && (
                <p className="text-sm text-destructive">{errors.name}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="plan-duration">Duration (hours)</Label>
              <Input
                id="plan-duration"
                type="number"
                min={1}
                step={1}
                value={form.duration_hours}
                onChange={(e) =>
                  field("duration_hours", Number(e.target.value))
                }
                required
              />
              {errors.duration_hours && (
                <p className="text-sm text-destructive">
                  {errors.duration_hours}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="plan-price">Price (paise / minor units)</Label>
              <Input
                id="plan-price"
                type="number"
                min={0}
                step={1}
                value={form.price_minor}
                onChange={(e) => field("price_minor", Number(e.target.value))}
                required
              />
              <p className="text-xs text-muted-foreground">
                Example: ₹99 = 9900 paise. Free plans use 0.
              </p>
              {errors.price_minor && (
                <p className="text-sm text-destructive">{errors.price_minor}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="plan-currency">Currency</Label>
              <Input
                id="plan-currency"
                value={form.currency}
                maxLength={3}
                onChange={(e) =>
                  field("currency", e.target.value.toUpperCase())
                }
                required
              />
              {errors.currency && (
                <p className="text-sm text-destructive">{errors.currency}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="plan-active"
                checked={form.is_active}
                onCheckedChange={(checked) =>
                  field("is_active", checked === true)
                }
              />
              <Label htmlFor="plan-active">Available for users to select</Label>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                disabled={saving}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving
                  ? "Saving..."
                  : editing
                    ? "Save changes"
                    : "Create plan"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </section>
  );
}

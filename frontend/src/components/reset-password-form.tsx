import { useEffect, useState } from "react";
import { Link } from "react-router";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { handleFetch, HttpError } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";

type ResetStatus = "checking" | "ready" | "invalid" | "complete";

export function ResetPasswordForm({ token }: { token: string | null }) {
  const [status, setStatus] = useState<ResetStatus>(
    token ? "checking" : "invalid",
  );
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;

    void handleFetch<CommonResponse<null>>(
      `/api/v1/auth/password-reset/validate?token=${encodeURIComponent(token)}`,
      () => setStatus("ready"),
      () => setStatus("invalid"),
    );
  }, [token]);

  const handleSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      setStatus("invalid");
      return;
    }
    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    setLoading(true);
    setError(null);
    await handleFetch<CommonResponse<null>>(
      "/api/v1/auth/password-reset/confirm",
      () => setStatus("complete"),
      (requestError) => {
        if (requestError instanceof HttpError && requestError.status === 400) {
          setStatus("invalid");
          return;
        }
        setError("We couldn't update your password. Please try again.");
      },
      {
        method: "POST",
        body: JSON.stringify({ token, password }),
      },
    );
    setLoading(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {status === "complete" ? "Password updated" : "Create a new password"}
        </CardTitle>
        <CardDescription>
          {status === "complete"
            ? "Your password has been changed. Sign in with your new password."
            : status === "invalid"
              ? "This password reset link is invalid or has expired."
              : "Choose a new password for your Image Gallery account."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {status === "checking" && (
          <p className="text-sm text-muted-foreground" role="status">
            Checking your reset link…
          </p>
        )}
        {status === "ready" && (
          <form onSubmit={handleSubmit}>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="new-password">New password</FieldLabel>
                <Input
                  autoComplete="new-password"
                  id="new-password"
                  minLength={8}
                  required
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="confirm-password">
                  Confirm password
                </FieldLabel>
                <Input
                  autoComplete="new-password"
                  id="confirm-password"
                  minLength={8}
                  required
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                />
              </Field>
              {error && (
                <p className="text-sm text-destructive" role="alert">
                  {error}
                </p>
              )}
              <Button type="submit" disabled={loading}>
                {loading ? "Updating password…" : "Update password"}
              </Button>
            </FieldGroup>
          </form>
        )}
        {status === "invalid" && (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Request a new link to reset your password.
            </p>
            <Button render={<Link to="/forgot-password" />} nativeButton={false}>
              Request a new link
            </Button>
          </div>
        )}
        {status === "complete" && (
          <Button render={<Link to="/login" />} nativeButton={false}>
            Back to sign in
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

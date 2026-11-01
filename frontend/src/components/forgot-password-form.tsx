import { useState } from "react";
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
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { handleFetch, HttpError } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);

    await handleFetch<CommonResponse<null>>(
      "/api/v1/auth/password-reset/request",
      (response) => setMessage(response.message),
      (requestError) => {
        setError(
          requestError instanceof HttpError && requestError.status === 404
            ? "We couldn't find an account with that email address."
            : "We couldn't send a reset email. Please try again.",
        );
      },
      {
        method: "POST",
        body: JSON.stringify({ email }),
      },
    );
    setLoading(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Forgot your password?</CardTitle>
        <CardDescription>
          Enter the email address associated with your account and we&apos;ll
          send you a password reset link.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="reset-email">Email</FieldLabel>
              <Input
                autoComplete="email"
                id="reset-email"
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </Field>
            {message && (
              <FieldDescription role="status">{message}</FieldDescription>
            )}
            {error && (
              <p className="text-sm text-destructive" role="alert">
                {error}
              </p>
            )}
            <Button type="submit" disabled={loading}>
              {loading ? "Sending link…" : "Send reset link"}
            </Button>
            <FieldDescription className="text-center">
              Remembered it? <Link to="/login">Back to sign in</Link>
            </FieldDescription>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}

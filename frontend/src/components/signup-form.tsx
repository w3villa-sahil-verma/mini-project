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
import { handleFetch } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";
import { logger } from "@/utils/logger";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

type SignupFormProps = React.ComponentProps<typeof Card> & {
  token: string | null;
};

type TOKEN_TYPE = "REGISTRATION";

type TokenPayload = {
  email: string;
  type: TOKEN_TYPE;
  exp: string;
  iat: string;
};

type RequestPayload = {
  email: string;
  password: string;
  token: string;
};

export function SignupForm({ token, ...props }: SignupFormProps) {
  const navigate = useNavigate();

  const [requestPayload, setRequestPayload] = useState<RequestPayload | null>(
    null,
  );
  const [loading, setLoading] = useState(false);

  const tokenPayload = useMemo<TokenPayload | null>(() => {
    let payload = null;
    try {
      const payloadChunk = token?.split(".")?.[1];

      if (payloadChunk) payload = JSON.parse(atob(payloadChunk));
    } catch (error) {
      if (error instanceof Error) {
        logger.error(error);
        toast.error(error.message);
      }
    }

    return payload;
  }, [token]);

  useEffect(() => {
    if (token && tokenPayload) {
      setRequestPayload({
        password: "",
        email: tokenPayload?.email,
        token: token,
      });
    }
  }, [tokenPayload, token]);

  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();

    setLoading(true);
    await handleFetch<CommonResponse<any>>(
      `/api/v1/auth/standard/register`,
      (resp) => {
        logger.debug("Data received:", resp);
        toast.success(resp.message)
        navigate("/user/dashboard")
      },
      (error) => {
        logger.error("Error occurred:", error);
        toast.error(error.message)
      },
      {
        method: "POST",
        body: JSON.stringify(requestPayload),
      },
    );
    setLoading(false);
  };

  return (
    <Card {...props}>
      <CardHeader>
        <CardTitle>Create an account</CardTitle>
        <CardDescription>
          Enter your information below to create your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input
                disabled
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={tokenPayload?.email}
              />
              <FieldDescription>
                We&apos;ll use this to contact you. We will not share your email
                with anyone else.
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="password">Password</FieldLabel>
              <Input
                id="password"
                type="password"
                required
                value={requestPayload?.password}
                onChange={(e) => {
                  setRequestPayload((prev) => {
                    if (prev !== null) {
                      return {
                        ...prev,
                        password: e.target.value!,
                      };
                    }

                    return prev;
                  });
                }}
              />
              <FieldDescription>
                Must be at least 8 characters long.
              </FieldDescription>
            </Field>
            {/* <Field>
              <FieldLabel htmlFor="confirm-password">
                Confirm Password
              </FieldLabel>
              <Input id="confirm-password" type="password" required />
              <FieldDescription>Please confirm your password.</FieldDescription>
            </Field> */}
            <FieldGroup>
              <Field>
                <Button type="submit" disabled={loading}>Create Account</Button>
                <FieldDescription className="px-6 text-center">
                  Already have an account? <a href="#">Sign in</a>
                </FieldDescription>
              </Field>
            </FieldGroup>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}

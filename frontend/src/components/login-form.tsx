import { cn } from "cn";

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
import { useNavigate } from "react-router";
import { useState } from "react";
import { logger } from "@/utils/logger";
import { toast } from "sonner";
import { handleFetch } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";

type RequestPayload = {
  email: string;
  password: string;
};

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const navigate = useNavigate();

  const [requestPayload, setRequestPayload] = useState<RequestPayload>({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();

    setLoading(true);
    await handleFetch<CommonResponse<any>>(
      `/api/v1/auth/standard/login`,
      (resp) => {
        logger.debug("Data received:", resp);
        toast.success(resp.message);
        navigate("/admin/dashboard");
      },
      (error) => {
        logger.error("Error occurred:", error);
        toast.error(error.message);
      },
      {
        method: "POST",
        body: JSON.stringify(requestPayload),
      },
    );
    setLoading(false);
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Login to your account</CardTitle>
          <CardDescription>
            Enter your email below to login to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="email">Email</FieldLabel>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  value={requestPayload?.email || ""}
                  onChange={(e) =>
                    setRequestPayload((p) => {
                      return {...p, email: e.target.value}
                    })
                  }
                />
              </Field>
              <Field>
                <div className="flex items-center">
                  <FieldLabel htmlFor="password">Password</FieldLabel>
                  <a
                    href="#"
                    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a>
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  value={requestPayload?.password || ""}
                  onChange={(e) =>
                    setRequestPayload((p) => {
                      return {...p, password: e.target.value}
                    })
                  }
                />
              </Field>
              <Field>
                <Button type="submit" disabled={loading}>
                  Login
                </Button>
                <Button variant="outline" type="button">
                  Login with Google
                </Button>
                <FieldDescription className="text-center">
                  Don&apos;t have an account? <a href="#">Sign up</a>
                </FieldDescription>
              </Field>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

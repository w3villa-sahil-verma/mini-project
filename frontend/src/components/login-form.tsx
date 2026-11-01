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
import { useEffect, useState } from "react";
import { logger } from "@/utils/logger";
import { toast } from "sonner";
import { handleFetch } from "@/hooks/useFetch";
import { useRevalidator } from "react-router";
import type { CommonResponse } from "@/types/common/request";
import { OAuthButtons } from "@/components/oauth-buttons";
import { useSearchParams } from "react-router";
import { ImageGalleryLogo } from "@/components/image-gallery-logo";

type RequestPayload = {
  email: string;
  password: string;
};

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const navigate = useNavigate();
  const revalidate = useRevalidator();
  const [searchParams, setSearchParams] = useSearchParams();

  const [requestPayload, setRequestPayload] = useState<RequestPayload>({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (searchParams.get("oauth_error") !== "1") return;
    toast.error("Sign-in with the selected provider failed. Please try again.");
    setSearchParams((current) => {
      current.delete("oauth_error");
      return current;
    }, { replace: true });
  }, [searchParams, setSearchParams]);

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
    await revalidate.revalidate();
    setLoading(false);
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <div className="flex size-10 items-center justify-center rounded-full bg-[#20221e] text-[#f7f5ef]">
            <ImageGalleryLogo className="size-5" />
          </div>
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
                <FieldDescription className="text-center">Or continue with</FieldDescription>
                <OAuthButtons />
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

"use client";

import { cn } from "cn";

import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldSeparator,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { handleFetch } from "@/hooks/useFetch";
import { RegistrationLinkSentDialog } from "./dialogs/registration-link-send-dialog";
import { useState } from "react";
import { logger } from "@/utils/logger";
import { toast } from "sonner";
import type { CommonResponse } from "@/types/common/request";
import { OAuthButtons } from "@/components/oauth-buttons";
import { ImageGalleryLogo } from "@/components/image-gallery-logo";
import { Link } from "react-router";

export function SignupEmailForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [openRegistrationLinkSentDialog, setOpenRegistrationLinkSentDialog] =
    useState<boolean>(false);
  const [email, setEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleClick(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    if (email) {
      setLoading(true)
      await handleFetch<CommonResponse<unknown>>(
        `/api/v1/auth/registeration-mail?email=${encodeURIComponent(email)}`,
        (resp) => {
          logger.debug("Data received:", resp)
          toast.success(resp.message)
          setOpenRegistrationLinkSentDialog(true);
        },
        (error) => {
          logger.error("Error occurred:", error);
          toast.error(error.message)
        },
      );
      setLoading(false)
    }
  }

  return (
    <>
      <div className={cn("flex flex-col gap-6", className)} {...props}>
        <form onSubmit={handleClick}>
          <FieldGroup>
            <div className="flex flex-col items-center gap-2 text-center">
              <a
                href="#"
                className="flex flex-col items-center gap-2 font-medium"
              >
                <div className="flex size-8 items-center justify-center rounded-md text-[#20221e]">
                  <ImageGalleryLogo className="size-6" />
                </div>
                <span className="sr-only">Image Gallery.</span>
              </a>
              <h1 className="text-xl font-bold">Welcome to Image Gallery.</h1>
              <FieldDescription>
                Already have an account? <Link to="/login">Sign in</Link>
              </FieldDescription>
            </div>
            <Field>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={email || ""}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Field>
            <Field>
              <Button type="submit" disabled={loading}>Create Account</Button>
            </Field>
            <FieldSeparator>Or</FieldSeparator>
            <OAuthButtons />
          </FieldGroup>
        </form>
        <FieldDescription className="px-6 text-center">
          By clicking continue, you agree to our{" "}
          <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
        </FieldDescription>
      </div>

      {/* Dialogs */}

      <RegistrationLinkSentDialog
        open={openRegistrationLinkSentDialog}
        onOpenChange={setOpenRegistrationLinkSentDialog}
        email={email || ""}
      />
    </>
  );
}

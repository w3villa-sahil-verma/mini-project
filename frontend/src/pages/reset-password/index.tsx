import { useSearchParams } from "react-router";

import { ResetPasswordForm } from "@/components/reset-password-form";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();

  return (
    <main className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <ResetPasswordForm token={searchParams.get("token")} />
      </div>
    </main>
  );
}

import { SignupEmailForm } from "@/components/signup-email-form";
import { SignupForm } from "@/components/signup-form";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";

export function Register() {
  const [searchParams, _] = useSearchParams();
  const [token, setToken] = useState<string|null>(null);

  useEffect(()=>{
    setToken(searchParams.get('token'))
  },[searchParams])

  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        {!!!token && <SignupEmailForm />}
        {!!token && <SignupForm token={token} />}
      </div>
    </div>
  );
}

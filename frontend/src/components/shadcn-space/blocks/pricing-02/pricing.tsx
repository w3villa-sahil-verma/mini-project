"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Check } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { handleFetch } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";
import { toast } from "sonner";

type PricingPlan = {
  id: number;
  name: string;
  duration_hours: number;
  price_minor: number;
  currency: string;
};

type CheckoutResult =
  | {
      type: "activated";
      subscription: { status: "ACTIVE" | "SCHEDULED" };
    }
  | {
      type: "razorpay";
      order_id: string;
      amount: number;
      currency: string;
      plan_name: string;
    };

type RazorpaySuccess = {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
};

type RazorpayOptions = {
  key: string;
  amount: number;
  currency: string;
  name: string;
  description: string;
  order_id: string;
  handler: (response: RazorpaySuccess) => void;
  modal: { ondismiss: () => void };
  theme: { color: string };
};

declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => { open: () => void };
  }
}

const RAZORPAY_CHECKOUT_URL =
  "https://checkout.razorpay.com/v1/checkout.js";

function request<T>(url: string, init?: RequestInit): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    void handleFetch<T>(
      url,
      resolve,
      reject,
      { credentials: "include", ...init },
    );
  });
}

function loadRazorpay(): Promise<void> {
  if (window.Razorpay) return Promise.resolve();

  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = RAZORPAY_CHECKOUT_URL;
    script.async = true;
    script.onload = () => {
      if (window.Razorpay) {
        resolve();
      } else {
        reject(new Error("Razorpay Checkout could not be initialized."));
      }
    };
    script.onerror = () => reject(new Error("Could not load Razorpay Checkout."));
    document.body.appendChild(script);
  });
}

function formatDuration(durationHours: number): string {
  if (durationHours % 24 === 0) {
    const days = durationHours / 24;
    return `${days} day${days === 1 ? "" : "s"}`;
  }

  return `${durationHours} hour${durationHours === 1 ? "" : "s"}`;
}

function formatPrice(priceMinor: number, currency: string): string {
  const amount = new Intl.NumberFormat("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(priceMinor / 100);

  return `${currency} ${amount}`;
}

const Pricing = () => {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [checkoutPlanId, setCheckoutPlanId] = useState<number | null>(null);

  async function startCheckout(plan: PricingPlan) {
    setCheckoutPlanId(plan.id);
    let checkoutOpened = false;

    try {
      const keyId = import.meta.env.ROZAR_PAY_API_KEY;
      if (plan.price_minor > 0 && !keyId) {
        throw new Error("Set ROZAR_PAY_API_KEY in frontend/.env.");
      }

      const response = await request<CommonResponse<CheckoutResult>>(
        "/api/v1/payments/checkout",
        {
          method: "POST",
          body: JSON.stringify({ plan_id: plan.id }),
        },
      );

      if (response.data.type === "activated") {
        toast.success(
          response.data.subscription.status === "SCHEDULED"
            ? "Free plan scheduled after your current membership."
            : "Free plan activated.",
        );
        return;
      }

      await loadRazorpay();
      if (!window.Razorpay) {
        throw new Error("Razorpay Checkout could not be initialized.");
      }
      if (!keyId) {
        throw new Error("Set ROZAR_PAY_API_KEY in frontend/.env.");
      }

      const checkout = new window.Razorpay({
        key: keyId,
        amount: response.data.amount,
        currency: response.data.currency,
        name: "Gym Membership",
        description: response.data.plan_name,
        order_id: response.data.order_id,
        handler: (payment) => {
          void request<CommonResponse<{ status: "ACTIVE" | "SCHEDULED" }>>(
            "/api/v1/payments/verify",
            {
              method: "POST",
              body: JSON.stringify(payment),
            },
          )
            .then((verification) => {
              toast.success(
                verification.data.status === "SCHEDULED"
                  ? "Payment successful. Your plan will start after your current membership."
                  : "Payment successful. Your plan is now active.",
              );
            })
            .catch((verificationError: unknown) => {
              toast.error(
                verificationError instanceof Error
                  ? verificationError.message
                  : "Could not verify the payment.",
              );
            })
            .finally(() => setCheckoutPlanId(null));
        },
        modal: {
          ondismiss: () => setCheckoutPlanId(null),
        },
        theme: { color: "#2563eb" },
      });

      checkout.open();
      checkoutOpened = true;
    } catch (checkoutError) {
      toast.error(
        checkoutError instanceof Error
          ? checkoutError.message
          : "Could not start checkout.",
      );
    } finally {
      if (!checkoutOpened) setCheckoutPlanId(null);
    }
  }

  useEffect(() => {
    let isCurrentRequest = true;

    void request<CommonResponse<PricingPlan[]>>("/api/v1/plans")
      .then((response) => {
        if (!isCurrentRequest) return;
        setPlans(response.data);
        setError(null);
      })
      .catch((requestError: unknown) => {
        if (!isCurrentRequest) return;
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Could not load pricing plans.",
        );
      })
      .finally(() => {
        if (isCurrentRequest) setLoading(false);
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [reloadKey]);

  const pricingCardVariants = {
    hidden: {
      opacity: 0,
      x: -60,
    },
    visible: (index: number) => ({
      opacity: 1,
      x: 0,
      transition: {
        delay: index * 0.25,
        duration: 0.6,
        ease: "easeInOut" as const,
      },
    }),
  };

  return (
    <section className="bg-background py-10 lg:py-0">
      <div className="max-w-7xl mx-auto px-4 xl:px-16 lg:py-20 sm:py-16 py-8">
        <div className="flex flex-col gap-8 md:gap-12 items-center justify-center w-full">
          {/* Heading */}
          <div className="flex flex-col gap-4 justify-center items-center">
            {/* Badge */}
            <Badge
              variant={"outline"}
              className="py-1 px-3 text-sm font-normal leading-5 w-fit h-7"
            >
              Pricing
            </Badge>
            {/* Heading */}
            <div className="max-w-3xs sm:max-w-md mx-auto text-center">
              <h2 className="text-foreground text-3xl sm:text-5xl font-medium">
                Choose your membership plan
              </h2>
            </div>
          </div>
          {loading ? (
            <p className="text-muted-foreground" role="status">
              Loading pricing plans...
            </p>
          ) : error ? (
            <div className="flex flex-col items-center gap-3 text-center">
              <p className="text-destructive" role="alert">{error}</p>
              <Button
                variant="outline"
                onClick={() => {
                  setLoading(true);
                  setError(null);
                  setReloadKey((current) => current + 1);
                }}
              >
                Try again
              </Button>
            </div>
          ) : plans.length === 0 ? (
            <p className="text-muted-foreground">
              No membership plans are currently available.
            </p>
          ) : (
            <div className="flex flex-col lg:flex-row gap-6 items-stretch h-full w-full">
              {plans.map((plan: PricingPlan, index: number) => {
                const duration = formatDuration(plan.duration_hours);

                return (
                  <motion.div
                    key={plan.id}
                    variants={pricingCardVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    custom={index}
                    className="relative flex-1 flex flex-col w-full"
                  >
                    <Card className="relative flex-1 flex flex-col rounded-2xl p-8 gap-8 border border-border">
                      <CardHeader className="p-0">
                        <div className="flex flex-col gap-3 self-stretch">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-2xl font-medium text-primary">
                              {plan.name}
                            </CardTitle>
                            <Badge variant="outline">
                              {duration}
                            </Badge>
                          </div>
                          <CardDescription className="text-base font-normal">
                            Membership access for {duration}.
                          </CardDescription>
                        </div>
                      </CardHeader>

                      <CardContent className="flex flex-col flex-1 gap-8 p-0">
                        <div className="flex flex-col gap-1">
                          <span className="text-foreground text-4xl sm:text-5xl font-medium">
                            {formatPrice(plan.price_minor, plan.currency)}
                          </span>
                          <span className="text-muted-foreground text-base font-normal">
                            for {duration}
                          </span>
                        </div>

                        <Separator orientation="horizontal" />

                        <ul className="flex flex-col gap-4 flex-1">
                          <li
                            className="flex items-center gap-3 text-base font-normal text-muted-foreground"
                          >
                            <Check className="size-4 text-primary shrink-0" />
                            Membership access
                          </li>
                        </ul>

                        <Button
                          className="w-full h-12 cursor-pointer"
                          variant="outline"
                          disabled={checkoutPlanId !== null}
                          onClick={() => void startCheckout(plan)}
                        >
                          {checkoutPlanId === plan.id
                            ? "Processing..."
                            : "Get started"}
                        </Button>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Pricing;

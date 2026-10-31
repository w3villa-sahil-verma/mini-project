import { useState } from "react";
import {
  ArrowRight,
  Check,
  ChevronDown,
  CircleUserRound,
  Menu,
  ShieldCheck,
  Sparkles,
  UsersRound,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router";
import { useRouteLoaderData } from "react-router";
import type { User, USER_ROLE } from "@/types/common/user";

const features = [
  {
    icon: UsersRound,
    title: "One clear member view",
    description:
      "Keep profiles, roles, renewals, and engagement in one place your whole team can trust.",
  },
  {
    icon: ShieldCheck,
    title: "Built for responsible teams",
    description:
      "Thoughtful permissions and dependable records help you manage every detail with confidence.",
  },
  {
    icon: Sparkles,
    title: "Less admin, more impact",
    description:
      "Automate the busywork so your organization can focus on the people and mission that matter.",
  },
];

export function Home() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user } = useRouteLoaderData<{ user: User | null }>("root")!;

  return (
    <main className="min-h-screen overflow-hidden bg-[#f7f8f5] text-[#173b35] dark:bg-[#102c28] dark:text-[#eef4ed]">
      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <a
          href="#top"
          className="flex items-center gap-3"
          aria-label="ABC Membership Management home"
        >
          <span className="flex size-10 items-center justify-center rounded-xl bg-[#173b35] text-sm font-bold tracking-tight text-[#f4c95d]">
            ABC
          </span>
          <span className="hidden text-sm font-semibold tracking-[-0.02em] sm:block">
            Membership management
          </span>
        </a>
        <nav
          className="hidden items-center gap-8 text-sm font-medium text-[#52706a] md:flex"
          aria-label="Main navigation"
        >
          <a className="transition-colors hover:text-[#173b35]" href="#why-abc">
            Why ABC
          </a>
          <a
            className="transition-colors hover:text-[#173b35]"
            href="#how-it-works"
          >
            How it works
          </a>
          <Link
            className="transition-colors hover:text-[#173b35]"
            to="/gallary"
          >
            Gallery
          </Link>
          <a className="transition-colors hover:text-[#173b35]" href="#support">
            Support
          </a>
        </nav>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="ml-1 rounded-full p-2 text-[#173b35] transition-colors hover:bg-[#dce9df] dark:text-[#eef4ed] dark:hover:bg-[#244a42] md:hidden"
            aria-label={
              menuOpen ? "Close navigation menu" : "Open navigation menu"
            }
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
        {menuOpen && (
          <nav
            className="absolute inset-x-5 top-19 rounded-2xl border border-[#c9d9cc] bg-[#f7f8f5] p-3 shadow-xl dark:border-[#2a4b44] dark:bg-[#163832] md:hidden"
            aria-label="Mobile navigation"
          >
            <a
              onClick={() => setMenuOpen(false)}
              className="block rounded-xl px-4 py-3 text-sm font-medium text-[#173b35] hover:bg-[#e8f0e8] dark:text-[#eef4ed] dark:hover:bg-[#244a42]"
              href="#why-abc"
            >
              Why ABC
            </a>
            <a
              onClick={() => setMenuOpen(false)}
              className="block rounded-xl px-4 py-3 text-sm font-medium text-[#173b35] hover:bg-[#e8f0e8] dark:text-[#eef4ed] dark:hover:bg-[#244a42]"
              href="#how-it-works"
            >
              How it works
            </a>
            <Link
              onClick={() => setMenuOpen(false)}
              className="block rounded-xl px-4 py-3 text-sm font-medium text-[#173b35] hover:bg-[#e8f0e8] dark:text-[#eef4ed] dark:hover:bg-[#244a42]"
              to="/gallary"
            >
              Gallery
            </Link>
            <a
              onClick={() => setMenuOpen(false)}
              className="block rounded-xl px-4 py-3 text-sm font-medium text-[#173b35] hover:bg-[#e8f0e8] dark:text-[#eef4ed] dark:hover:bg-[#244a42]"
              href="#support"
            >
              Support
            </a>
          </nav>
        )}
      </header>

      <section
        id="top"
        className="relative mx-auto grid max-w-7xl items-center gap-12 px-5 pb-16 pt-8 sm:gap-14 sm:px-6 sm:pb-20 sm:pt-12 lg:grid-cols-[1.03fr_.97fr] lg:px-10 lg:pb-28 lg:pt-20"
      >
        <div className="relative z-10 max-w-2xl">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-[#c9d9cc] bg-[#eef4ed] px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-[#173b35]">
            <span className="size-1.5 rounded-full bg-[#d99d31]" />
            Membership, made human
          </div>
          <h1 className="max-w-2xl text-5xl font-semibold leading-[1.03] tracking-[-0.055em] text-[#173b35] dark:text-[#eef4ed] sm:text-6xl lg:text-[76px]">
            Help your community{" "}
            <span className="font-serif italic font-normal text-[#ba7a24]">
              belong.
            </span>
          </h1>
          <p className="mt-7 max-w-lg text-lg leading-8 text-[#52706a] dark:text-[#b8cbc0]">
            ABC brings your members, programs, and organization together in one
            calm, capable workspace—so you can spend less time managing and more
            time making a difference.
          </p>
          <SignActions role={user?.role} />
          <div className="mt-8 flex items-center gap-3 text-sm text-[#52706a]">
            <div className="flex -space-x-2" aria-hidden="true">
              <span className="flex size-8 items-center justify-center rounded-full border-2 border-[#f7f8f5] bg-[#d6a18b] text-[10px] font-bold text-white">
                JM
              </span>
              <span className="flex size-8 items-center justify-center rounded-full border-2 border-[#f7f8f5] bg-[#7caaa0] text-[10px] font-bold text-white">
                RK
              </span>
              <span className="flex size-8 items-center justify-center rounded-full border-2 border-[#f7f8f5] bg-[#d1b45b] text-[10px] font-bold text-white">
                AS
              </span>
            </div>
            <span>Trusted by growing organizations</span>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-130 sm:max-w-130 lg:ml-auto">
          <div className="absolute -right-16 -top-12 size-56 rounded-full bg-[#e3eddf] blur-3xl" />
          <div className="absolute -bottom-12 -left-12 size-48 rounded-full bg-[#f4dfb1] blur-3xl" />
          <div className="relative rotate-2 rounded-[28px] border border-[#d7e2d6] bg-white p-3 shadow-[0_24px_70px_rgba(34,73,61,0.13)]">
            <div className="overflow-hidden rounded-[20px] border border-[#e2e9e1] bg-[#f7faf6]">
              <div className="flex items-center justify-between border-b border-[#e2e9e1] bg-white px-5 py-4">
                <div className="flex items-center gap-2.5">
                  <span className="size-7 rounded-lg bg-[#173b35]" />
                  <span className="text-xs font-bold tracking-tight text-[#173b35]">
                    ABC workspace
                  </span>
                </div>
                <div className="flex gap-1.5">
                  <span className="size-2 rounded-full bg-[#d5e1d7]" />
                  <span className="size-2 rounded-full bg-[#d5e1d7]" />
                  <span className="size-2 rounded-full bg-[#d5e1d7]" />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-[105px_1fr]">
                <div className="hidden border-r border-[#e2e9e1] bg-[#f1f6f0] p-3 sm:block">
                  <div className="mb-5 h-2 w-14 rounded bg-[#b7cbc0]" />
                  <div className="space-y-3">
                    <div className="h-2 w-16 rounded bg-[#d3e0d5]" />
                    <div className="h-2 w-12 rounded bg-[#d3e0d5]" />
                    <div className="h-2 w-14 rounded bg-[#d3e0d5]" />
                    <div className="h-2 w-10 rounded bg-[#d3e0d5]" />
                  </div>
                </div>
                <div className="p-5 sm:p-6">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-[10px] font-medium text-[#78918a]">
                        Good morning, Maya
                      </p>
                      <h2 className="mt-1 text-xl font-semibold tracking-tight text-[#173b35]">
                        Your organization
                      </h2>
                    </div>
                    <div className="size-8 rounded-full bg-[#dba68e]" />
                  </div>
                  <div className="mt-5 grid grid-cols-2 gap-2.5">
                    <div className="rounded-xl bg-[#173b35] p-3 text-white">
                      <p className="text-[9px] text-[#c7ddd1]">
                        Active members
                      </p>
                      <p className="mt-2 text-2xl font-semibold">1,284</p>
                      <p className="mt-1 text-[9px] text-[#f4c95d]">
                        ↑ 8.4% this month
                      </p>
                    </div>
                    <div className="rounded-xl border border-[#dce7dc] bg-white p-3">
                      <p className="text-[9px] text-[#78918a]">Renewals due</p>
                      <p className="mt-2 text-2xl font-semibold text-[#173b35]">
                        42
                      </p>
                      <p className="mt-1 text-[9px] text-[#ba7a24]">
                        Next 30 days
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 rounded-xl border border-[#dce7dc] bg-white p-3.5">
                    <div className="flex items-center justify-between">
                      <p className="text-[10px] font-semibold text-[#173b35]">
                        Member growth
                      </p>
                      <p className="text-[9px] text-[#78918a]">Last 6 months</p>
                    </div>
                    <div className="mt-5 flex h-20 items-end gap-2">
                      <div className="h-[38%] flex-1 rounded-t bg-[#d8e6d9]" />
                      <div className="h-[52%] flex-1 rounded-t bg-[#c4d9ca]" />
                      <div className="h-[48%] flex-1 rounded-t bg-[#c4d9ca]" />
                      <div className="h-[68%] flex-1 rounded-t bg-[#9fbbb0]" />
                      <div className="h-[76%] flex-1 rounded-t bg-[#7fa99d]" />
                      <div className="h-full flex-1 rounded-t bg-[#d99d31]" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="absolute -bottom-5 -left-7 hidden items-center gap-3 rounded-2xl border border-[#d7e2d6] bg-white px-4 py-3 shadow-lg sm:flex">
            <span className="flex size-8 items-center justify-center rounded-full bg-[#e8f2e5] text-[#477b60]">
              <Check className="size-4" />
            </span>
            <div>
              <p className="text-xs font-semibold text-[#173b35]">
                Renewal complete
              </p>
              <p className="text-[10px] text-[#78918a]">2 minutes ago</p>
            </div>
          </div>
        </div>
      </section>

      <section
        id="why-abc"
        className="border-y border-[#dce7dc] bg-[#eef4ed] px-6 py-20 lg:px-10 dark:border-[#2a4b44] dark:bg-[#163832]"
      >
        <div className="mx-auto max-w-7xl">
          <div className="max-w-xl">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#ba7a24]">
              Everything in one place
            </p>
            <h2 className="mt-4 text-4xl font-semibold tracking-[-0.04em] text-[#173b35] dark:text-[#eef4ed] sm:text-5xl">
              A better way to care for your members.
            </h2>
          </div>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {features.map(({ icon: Icon, title, description }) => (
              <article key={title} className="border-t border-[#cbdacf] pt-5">
                <Icon className="size-6 text-[#ba7a24]" />
                <h3 className="mt-5 text-lg font-semibold text-[#173b35]">
                  {title}
                </h3>
                <p className="mt-3 max-w-xs text-sm leading-6 text-[#52706a]">
                  {description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section
        id="how-it-works"
        className="mx-auto flex max-w-7xl flex-col items-start gap-8 px-6 py-14 text-sm text-[#52706a] sm:flex-row sm:items-center sm:justify-between lg:px-10"
      >
        <p>Ready to make membership management feel simple?</p>
        <div className="flex items-center gap-5">
          <a
            href="#support"
            className="font-medium text-[#173b35] hover:underline"
          >
            Talk to our team
            <ChevronDown className="ml-1 inline size-3 -rotate-90" />
          </a>
          <a
            href="/register"
            className="font-medium text-[#173b35] hover:underline"
          >
            Get started <ArrowRight className="ml-1 inline size-3" />
          </a>
        </div>
      </section>
      <footer
        id="support"
        className="bg-[#173b35] px-6 py-8 text-sm text-[#c7ddd1] lg:px-10 dark:bg-[#0a211e]"
      >
        <div className="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p>
            <span className="font-semibold text-white">ABC</span> Membership
            management
          </p>
          <p>Simple systems for stronger communities.</p>
        </div>
      </footer>
    </main>
  );
}

function SignActions({ role }: { role?: USER_ROLE }) {
  return (
    <div className="mt-9 flex items-center gap-1">
      {!role && (
        <Link
          to="/register"
          className="inline-flex w-full items-center justify-center gap-2 whitespace-nowrap"
        >
          <Button
            size="lg"
            className="h-13 min-w-53 rounded-full bg-[#d99d31] px-6 text-[#173b35] shadow-[0_8px_20px_rgba(217,157,49,0.2)] transition-colors hover:bg-[#b8791f] hover:text-white focus-visible:ring-[#d99d31]"
          >
            <span>Register your organization</span>
            <ArrowRight className="size-4 shrink-0" aria-hidden="true" />
          </Button>
        </Link>
      )}
      {!role && (
        <Link
          to="/login"
          className="inline-flex w-full items-center justify-center gap-2 whitespace-nowrap"
        >
          <Button
            size="lg"
            variant="outline"
            className="h-13 min-w-35.5 rounded-full border-[#b8cbc0] bg-transparent px-6 text-[#173b35] transition-colors hover:border-[#173b35] hover:bg-[#173b35] hover:text-white focus-visible:ring-[#173b35] dark:border-[#b8cbc0] dark:text-[#eef4ed] dark:hover:border-[#dbe9df] dark:hover:bg-[#dbe9df] dark:hover:text-[#173b35]"
          >
            <CircleUserRound className="size-4 shrink-0" aria-hidden="true" />
            <span>Sign in to ABC</span>
          </Button>
        </Link>
      )}
      {role && (
        <Link
          to={`${role.toLowerCase()}`}
          className="inline-flex w-full items-center justify-center gap-2 whitespace-nowrap"
        >
          <Button
            size="lg"
            variant="outline"
            className="h-13 min-w-35.5 rounded-full border-[#b8cbc0] bg-transparent px-6 text-[#173b35] transition-colors hover:border-[#173b35] hover:bg-[#173b35] hover:text-white focus-visible:ring-[#173b35] dark:border-[#b8cbc0] dark:text-[#eef4ed] dark:hover:border-[#dbe9df] dark:hover:bg-[#dbe9df] dark:hover:text-[#173b35]"
          >
            <CircleUserRound className="size-4 shrink-0" aria-hidden="true" />
            <span>Continue </span>
          </Button>
        </Link>
      )}
    </div>
  );
}

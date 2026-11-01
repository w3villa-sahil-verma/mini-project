import { useState } from "react";
import {
  ArrowDownRight,
  ArrowRight,
  Images,
  LockKeyhole,
  Menu,
  Sparkles,
  X,
} from "lucide-react";
import { Link, useRouteLoaderData } from "react-router";

import type { User } from "@/types/common/user";

const previewImages = [
  {
    src: "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=85",
    alt: "Mountain lake reflecting the surrounding peaks",
    title: "Quiet places",
    className:
      "absolute left-[5%] top-[3%] h-[72%] w-[66%] -rotate-2 sm:left-[8%] sm:w-[62%]",
  },
  {
    src: "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=700&q=85",
    alt: "Sunlit flowers in a garden",
    title: "Small details",
    className:
      "absolute right-0 top-[10%] h-[39%] w-[37%] rotate-3 sm:right-[2%] sm:w-[34%]",
  },
  {
    src: "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=800&q=85",
    alt: "Ocean waves rolling toward the shore",
    title: "Open water",
    className:
      "absolute bottom-[2%] right-[4%] h-[39%] w-[51%] rotate-2 sm:bottom-0 sm:right-[7%] sm:w-[44%]",
  },
];

const highlights = [
  {
    number: "01",
    title: "Come on in",
    description:
      "Explore a handpicked collection of free images right away. No account needed to start looking.",
  },
  {
    number: "02",
    title: "Find your next favorite",
    description:
      "Browse thoughtful collections and discover images across nature, travel, color, and everyday life.",
  },
  {
    number: "03",
    title: "Go a little further",
    description:
      "A subscription unlocks premium images. Sign in with an active plan to see the full collection.",
  },
];

export function Home() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user } = useRouteLoaderData<{ user: User | null }>("root")!;
  const accountPath = user ? `/${user.role.toLowerCase()}` : "/login";
  const membershipPath =
    user?.role === "ADMIN"
      ? "/admin"
      : user
        ? "/user/pricing"
        : "/register";

  const closeMenu = () => setMenuOpen(false);

  return (
    <main className="min-h-screen overflow-hidden bg-[#f7f5ef] text-[#20221e]">
      <header className="relative z-20 mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8 lg:px-12">
        <Link
          to="/"
          className="flex items-center gap-3"
          aria-label="Image Gallery home"
        >
          <span className="flex size-10 items-center justify-center rounded-full bg-[#20221e] text-[#f7f5ef]">
            <Images className="size-5" aria-hidden="true" />
          </span>
          <span className="font-heading text-base font-bold tracking-tight">
            Image Gallery
          </span>
        </Link>

        <nav
          className="hidden items-center gap-8 text-sm font-medium text-[#686960] md:flex"
          aria-label="Main navigation"
        >
          <Link className="transition-colors hover:text-[#20221e]" to="/gallery">
            Gallery
          </Link>
          <a className="transition-colors hover:text-[#20221e]" href="#about">
            About
          </a>
          <a
            className="transition-colors hover:text-[#20221e]"
            href="#membership"
          >
            Membership
          </a>
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Link
            className="px-3 py-2 text-sm font-semibold transition-colors hover:text-[#e44e31]"
            to={accountPath}
          >
            {user ? "My account" : "Sign in"}
          </Link>
          <Link
            to={user ? "/gallery" : "/register"}
            className="inline-flex h-10 items-center justify-center rounded-full bg-[#e95c3b] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#cf482b]"
          >
            {user ? "Explore images" : "Join for free"}
          </Link>
        </div>

        <button
          type="button"
          className="inline-flex size-10 items-center justify-center rounded-full border border-[#dedbd2] md:hidden"
          aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? (
            <X className="size-5" aria-hidden="true" />
          ) : (
            <Menu className="size-5" aria-hidden="true" />
          )}
        </button>

        {menuOpen && (
          <nav
            className="absolute inset-x-5 top-[4.5rem] rounded-2xl border border-[#e4e1d8] bg-[#fffefa] p-3 shadow-xl md:hidden"
            aria-label="Mobile navigation"
          >
            <Link
              onClick={closeMenu}
              className="block rounded-xl px-4 py-3 text-sm font-medium hover:bg-[#f3f0e8]"
              to="/gallery"
            >
              Explore the gallery
            </Link>
            <a
              onClick={closeMenu}
              className="block rounded-xl px-4 py-3 text-sm font-medium hover:bg-[#f3f0e8]"
              href="#about"
            >
              About
            </a>
            <a
              onClick={closeMenu}
              className="block rounded-xl px-4 py-3 text-sm font-medium hover:bg-[#f3f0e8]"
              href="#membership"
            >
              Membership
            </a>
            <Link
              onClick={closeMenu}
              className="block rounded-xl px-4 py-3 text-sm font-medium text-[#e44e31] hover:bg-[#f3f0e8]"
              to={accountPath}
            >
              {user ? "My account" : "Sign in"}
            </Link>
          </nav>
        )}
      </header>

      <section className="mx-auto grid max-w-7xl items-center gap-8 px-5 pb-16 pt-6 sm:px-8 sm:pb-24 lg:grid-cols-[0.92fr_1.08fr] lg:gap-10 lg:px-12 lg:pb-28 lg:pt-12">
        <div className="relative z-10 max-w-xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#e6c6b8] bg-[#f7e9e1] px-3.5 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-[#a8432d]">
            <Sparkles className="size-3.5" aria-hidden="true" />
            A little wonder, every day
          </div>
          <h1 className="font-heading text-5xl font-semibold leading-[0.99] tracking-[-0.06em] sm:text-6xl lg:text-[76px]">
            See the world
            <br />
            <span className="font-serif font-normal italic text-[#e95c3b]">
              differently.
            </span>
          </h1>
          <p className="mt-6 max-w-md text-base leading-7 text-[#686960] sm:text-lg sm:leading-8">
            A place to pause, look closer, and find images that stay with you.
            Start exploring our free gallery today.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              to="/gallery"
              className="inline-flex h-12 items-center justify-center gap-2 rounded-full bg-[#20221e] px-6 text-sm font-semibold text-white transition-colors hover:bg-[#373a34]"
            >
              Explore the gallery
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
            <Link
              to={membershipPath}
              className="inline-flex h-12 items-center gap-2 rounded-full px-5 text-sm font-semibold transition-colors hover:bg-[#ece9e1]"
            >
              Discover premium
              <ArrowDownRight className="size-4" aria-hidden="true" />
            </Link>
          </div>
          <p className="mt-5 text-xs font-medium tracking-wide text-[#828379]">
            Free images for everyone. Premium collections for members.
          </p>
        </div>

        <div
          className="relative mx-auto h-[420px] w-full max-w-[620px] sm:h-[500px]"
          aria-label="A preview of images in the gallery"
          role="group"
        >
          {previewImages.map((image) => (
            <figure
              key={image.title}
              className={`${image.className} overflow-hidden rounded-[1.4rem] border-[5px] border-[#fffefa] bg-[#e6e2d9] shadow-[0_24px_70px_rgba(47,43,33,0.16)] sm:rounded-[1.8rem] sm:border-[7px]`}
            >
              <img
                src={image.src}
                alt={image.alt}
                className="size-full object-cover"
                fetchPriority={image.title === "Quiet places" ? "high" : "auto"}
              />
              <figcaption className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent px-4 pb-4 pt-12 text-sm font-medium text-white sm:px-5 sm:pb-5">
                {image.title}
              </figcaption>
            </figure>
          ))}
          <div className="absolute bottom-[11%] left-0 flex items-center gap-2.5 rounded-full border border-[#e4e1d8] bg-[#fffefa] px-4 py-3 text-xs font-semibold shadow-lg sm:bottom-[9%] sm:left-[3%] sm:px-5 sm:text-sm">
            <span className="size-2 rounded-full bg-[#e95c3b]" />
            Open gallery, open to all
          </div>
        </div>
      </section>

      <section
        id="about"
        className="border-y border-[#e5e1d7] bg-[#efede5] px-5 py-16 sm:px-8 sm:py-20 lg:px-12"
      >
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div className="max-w-2xl">
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#e95c3b]">
                The joy is in the looking
              </p>
              <h2 className="mt-4 font-heading text-3xl font-semibold tracking-[-0.045em] sm:text-5xl">
                A gallery that welcomes everyone.
              </h2>
            </div>
            <p className="max-w-sm text-sm leading-6 text-[#686960]">
              Wander through beautiful images at your own pace. The door is
              always open to the free collection.
            </p>
          </div>

          <div className="mt-12 grid gap-8 border-t border-[#d8d5ca] pt-6 md:grid-cols-3 md:gap-10">
            {highlights.map((highlight) => (
              <article key={highlight.number}>
                <p className="text-xs font-semibold tracking-[0.12em] text-[#e95c3b]">
                  {highlight.number}
                </p>
                <h3 className="mt-5 font-heading text-xl font-semibold tracking-tight">
                  {highlight.title}
                </h3>
                <p className="mt-3 max-w-sm text-sm leading-6 text-[#686960]">
                  {highlight.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section
        id="membership"
        className="mx-auto flex max-w-7xl flex-col gap-8 px-5 py-16 sm:px-8 md:flex-row md:items-center md:justify-between lg:px-12 lg:py-20"
      >
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-[#e95c3b]">
            <LockKeyhole className="size-3.5" aria-hidden="true" />
            For the curious
          </div>
          <h2 className="mt-4 font-heading text-3xl font-semibold tracking-[-0.045em] sm:text-4xl">
            Some stories are worth staying for.
          </h2>
          <p className="mt-3 max-w-xl text-sm leading-6 text-[#686960] sm:text-base">
            Sign in and choose a membership to unlock premium images. Your free
            gallery stays open whether you subscribe or not.
          </p>
        </div>
        <Link
          to={membershipPath}
          className="inline-flex h-12 shrink-0 items-center justify-center gap-2 self-start rounded-full bg-[#e95c3b] px-6 text-sm font-semibold text-white transition-colors hover:bg-[#cf482b] md:self-center"
        >
          {user ? "View membership plans" : "Join and explore"}
          <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
      </section>

      <footer className="bg-[#20221e] px-5 py-7 text-sm text-[#d7d5cc] sm:px-8 lg:px-12">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <Link to="/" className="flex items-center gap-2.5 font-semibold text-white">
            <Images className="size-4" aria-hidden="true" />
            Image Gallery
          </Link>
          <p>Find a moment. Keep the feeling.</p>
          <Link
            to="/gallery"
            className="font-medium transition-colors hover:text-white"
          >
            Browse images
          </Link>
        </div>
      </footer>
    </main>
  );
}

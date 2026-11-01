import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useRouteLoaderData } from "react-router";
import { LockKeyhole, RefreshCw } from "lucide-react";

import { Button, buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { handleFetch } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";
import type { User } from "@/types/common/user";

type GalleryImage = {
  id: number;
  is_premium: boolean;
  filename: string;
  image_url: string | null;
};

type GalleryPageData = {
  items: GalleryImage[];
  has_more: boolean;
  next_offset: number;
  has_premium_access: boolean;
};

function requestPage(offset: number): Promise<CommonResponse<GalleryPageData>> {
  return new Promise((resolve, reject) => {
    void handleFetch<CommonResponse<GalleryPageData>>(
      `/api/v1/gallery?offset=${offset}`,
      resolve,
      reject,
    );
  });
}

export function GalleryPage() {
  const { user } = useRouteLoaderData<{ user: User | null }>("root")!;
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [hasPremiumAccess, setHasPremiumAccess] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const membershipPath = !user
    ? "/register"
    : user.role === "ADMIN"
      ? "/admin"
      : "/user/pricing";

  const loadPage = useCallback(async (pageOffset: number) => {
    setError(null);
    setLoading(pageOffset === 0);
    setLoadingMore(pageOffset !== 0);
    try {
      const response = await requestPage(pageOffset);
      setImages((current) =>
        pageOffset === 0
          ? response.data.items
          : [
              ...current,
              ...response.data.items.filter(
                (image) => !current.some((existing) => existing.id === image.id),
              ),
            ],
      );
      setHasMore(response.data.has_more);
      setHasPremiumAccess(response.data.has_premium_access);
      setOffset(response.data.next_offset);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Could not load gallery images.",
      );
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, []);

  useEffect(() => {
    void loadPage(0);
  }, [loadPage]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasMore || loading || loadingMore || error) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          void loadPage(offset);
        }
      },
      { rootMargin: "400px" },
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [error, hasMore, loadPage, loading, loadingMore, offset]);

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 px-4 py-8 sm:px-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Gallery</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Browse free images and unlock the full gallery with an active plan.
          </p>
        </div>
        {!hasPremiumAccess && (
          <Link
            to={membershipPath}
            className={buttonVariants({ className: "h-9 rounded-lg px-3" })}
          >
            View membership plans
          </Link>
        )}
      </header>

      {error && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-destructive/40 p-4">
          <p className="text-sm text-destructive" role="alert">
            Could not load images: {error}
          </p>
          <Button variant="outline" onClick={() => void loadPage(images.length ? offset : 0)}>
            <RefreshCw className="size-4" />
            Retry
          </Button>
        </div>
      )}

      <section
        aria-label="Gallery images"
        className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        {images.map((image) => (
          <Card key={image.id} className="overflow-hidden p-0">
            <div className="relative aspect-square bg-muted">
              {image.image_url ? (
                <img
                  src={image.image_url}
                  alt={image.is_premium ? "Premium gallery image" : image.filename}
                  loading="lazy"
                  className="size-full object-cover"
                />
              ) : (
                <div
                  className="relative flex size-full items-center justify-center overflow-hidden bg-gradient-to-br from-primary/20 via-muted to-primary/40"
                  aria-label="Premium image preview is blurred"
                >
                  <div className="absolute -left-8 top-8 size-40 rounded-full bg-primary/40 blur-3xl" />
                  <div className="absolute -right-4 bottom-4 size-36 rounded-full bg-fuchsia-400/40 blur-3xl" />
                  <div className="relative flex items-center gap-2 rounded-full bg-background/80 px-4 py-2 text-sm font-medium backdrop-blur-md">
                    <LockKeyhole className="size-4" />
                    Premium image
                  </div>
                </div>
              )}
              {image.is_premium && (
                <span className="absolute left-3 top-3 rounded-full bg-background/90 px-2.5 py-1 text-xs font-semibold backdrop-blur">
                  Premium
                </span>
              )}
            </div>
            <CardHeader className="p-4">
              <CardTitle className="text-sm">
                {image.is_premium && !hasPremiumAccess
                  ? "Premium image"
                  : image.filename}
              </CardTitle>
              <CardDescription>
                {image.is_premium && !hasPremiumAccess
                  ? "An active membership is required to view this image."
                  : image.is_premium
                    ? "Premium member image"
                    : "Free image"}
              </CardDescription>
            </CardHeader>
          </Card>
        ))}
        {loading &&
          Array.from({ length: 8 }, (_, index) => (
            <Skeleton key={index} className="aspect-square w-full rounded-xl" />
          ))}
      </section>

      {!loading && images.length === 0 && !error && (
        <p className="py-16 text-center text-muted-foreground">
          No gallery images are available yet.
        </p>
      )}

      {loadingMore && (
        <p className="py-4 text-center text-sm text-muted-foreground" role="status">
          Loading more images…
        </p>
      )}
      <div ref={sentinelRef} aria-hidden="true" className="h-1" />
    </main>
  );
}

import { useCallback, useEffect, useState } from "react";
import { Check, ChevronLeft, ChevronRight, ImagePlus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { handleFetch } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";

type AdminGalleryImage = {
  id: number;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: string;
  is_premium: boolean;
  created_at: string;
  image_url: string | null;
};

type GalleryList = {
  items: AdminGalleryImage[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type PresignedUpload = {
  image_id: number;
  upload_url: string;
  expires_in: number;
};

function request<T>(url: string, init?: RequestInit): Promise<T> {
  return new Promise((resolve, reject) => {
    void handleFetch<T>(url, resolve, reject, init);
  });
}

export function AdminGalleryPage() {
  const [gallery, setGallery] = useState<GalleryList | null>(null);
  const [page, setPage] = useState(1);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [uploadAsPremium, setUploadAsPremium] = useState(false);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const loadGallery = useCallback(() => {
    setLoading(true);
    setError(null);
    void request<CommonResponse<GalleryList>>(
      `/api/v1/admin/gallery?page=${page}&page_size=24`,
    )
      .then((response) => {
        setGallery(response.data);
        setSelectedIds([]);
      })
      .catch((requestError: unknown) => {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Could not load gallery images.",
        );
      })
      .finally(() => setLoading(false));
  }, [page]);

  useEffect(() => {
    loadGallery();
  }, [loadGallery, reloadKey]);

  const uploadFiles = async () => {
    if (files.length === 0) return;
    setProcessing(true);
    let uploaded = 0;
    try {
      for (const file of files) {
        const presign = await request<CommonResponse<PresignedUpload>>(
          "/api/v1/admin/gallery/presign",
          {
            method: "POST",
            body: JSON.stringify({
              filename: file.name,
              content_type: file.type,
              size_bytes: file.size,
              is_premium: uploadAsPremium,
            }),
          },
        );

        const uploadResponse = await fetch(presign.data.upload_url, {
          method: "PUT",
          headers: { "Content-Type": file.type },
          body: file,
        });
        if (!uploadResponse.ok) {
          throw new Error(
            `Storage rejected ${file.name} (${uploadResponse.status}).`,
          );
        }
        await request<CommonResponse<AdminGalleryImage>>(
          `/api/v1/admin/gallery/${presign.data.image_id}/complete`,
          { method: "POST" },
        );
        uploaded += 1;
      }

      toast.success(`${uploaded} image${uploaded === 1 ? "" : "s"} uploaded.`);
      setFiles([]);
      if (page !== 1) setPage(1);
      else setReloadKey((key) => key + 1);
    } catch (uploadError) {
      toast.error(
        uploadError instanceof Error
          ? uploadError.message
          : "Could not upload gallery images.",
      );
      setReloadKey((key) => key + 1);
    } finally {
      setProcessing(false);
    }
  };

  const togglePremium = async (image: AdminGalleryImage) => {
    try {
      await request<CommonResponse<AdminGalleryImage>>(
        `/api/v1/admin/gallery/${image.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({ is_premium: !image.is_premium }),
        },
      );
      toast.success("Gallery image updated.");
      setReloadKey((key) => key + 1);
    } catch (updateError) {
      toast.error(
        updateError instanceof Error
          ? updateError.message
          : "Could not update gallery image.",
      );
    }
  };

  const deleteSelected = async () => {
    if (selectedIds.length === 0) return;
    if (!window.confirm(`Delete ${selectedIds.length} selected image(s)?`)) return;
    setProcessing(true);
    try {
      await request<CommonResponse<{ deleted_ids: number[] }>>(
        "/api/v1/admin/gallery/bulk-delete",
        {
          method: "POST",
          body: JSON.stringify({ image_ids: selectedIds }),
        },
      );
      toast.success("Selected images deleted.");
      setReloadKey((key) => key + 1);
    } catch (deleteError) {
      toast.error(
        deleteError instanceof Error
          ? deleteError.message
          : "Could not delete selected images.",
      );
    } finally {
      setProcessing(false);
    }
  };

  const deleteOne = async (image: AdminGalleryImage) => {
    if (!window.confirm(`Delete "${image.filename}"?`)) return;
    setProcessing(true);
    try {
      await request<CommonResponse<{ id: number }>>(
        `/api/v1/admin/gallery/${image.id}`,
        { method: "DELETE" },
      );
      toast.success("Image deleted.");
      setReloadKey((key) => key + 1);
    } catch (deleteError) {
      toast.error(
        deleteError instanceof Error
          ? deleteError.message
          : "Could not delete image.",
      );
    } finally {
      setProcessing(false);
    }
  };

  const allOnPageSelected =
    Boolean(gallery?.items.length) &&
    gallery?.items.every((image) => selectedIds.includes(image.id));

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 p-4 md:p-6">
      <header>
        <h1 className="text-2xl font-semibold">Gallery management</h1>
        <p className="text-sm text-muted-foreground">
          Upload images, mark premium access, and manage the public gallery.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Upload images</CardTitle>
          <CardDescription>
            Select multiple JPEG, PNG, or WebP images. Each file can be up to 5 MB.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="min-w-0 flex-1 space-y-2">
            <label htmlFor="gallery-files" className="text-sm font-medium">
              Image files
            </label>
            <input
              id="gallery-files"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              multiple
              disabled={processing}
              onChange={(event) =>
                setFiles(Array.from(event.currentTarget.files ?? []))
              }
              className="block w-full text-sm file:mr-3 file:rounded-md file:border file:bg-background file:px-3 file:py-2"
            />
            {files.length > 0 && (
              <p className="text-xs text-muted-foreground">
                {files.length} file{files.length === 1 ? "" : "s"} selected
              </p>
            )}
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={uploadAsPremium}
              onChange={(event) => setUploadAsPremium(event.currentTarget.checked)}
            />
            Upload as premium
          </label>
          <Button
            type="button"
            disabled={processing || files.length === 0}
            onClick={() => void uploadFiles()}
          >
            <ImagePlus className="size-4" />
            {processing ? "Processing..." : "Upload selected"}
          </Button>
        </CardContent>
      </Card>

      <section className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold">Gallery images</h2>
            <p className="text-sm text-muted-foreground">
              {gallery?.total ?? 0} image{gallery?.total === 1 ? "" : "s"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {gallery && gallery.items.length > 0 && (
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={allOnPageSelected}
                  onChange={(event) =>
                    setSelectedIds(
                      event.currentTarget.checked
                        ? gallery.items.map((image) => image.id)
                        : [],
                    )
                  }
                />
                Select page
              </label>
            )}
            <Button
              variant="destructive"
              disabled={processing || selectedIds.length === 0}
              onClick={() => void deleteSelected()}
            >
              <Trash2 className="size-4" />
              Delete selected ({selectedIds.length})
            </Button>
          </div>
        </div>

        {error && (
          <p className="text-sm text-destructive" role="alert">
            Could not load gallery: {error}
          </p>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {loading
            ? Array.from({ length: 8 }, (_, index) => (
                <div
                  key={index}
                  className="aspect-square animate-pulse rounded-xl bg-muted"
                />
              ))
            : gallery?.items.map((image) => (
                <Card key={image.id} className="overflow-hidden p-0">
                  <div className="relative aspect-square bg-muted">
                    {image.image_url ? (
                      <img
                        src={image.image_url}
                        alt={image.filename}
                        loading="lazy"
                        className="size-full object-cover"
                      />
                    ) : (
                      <div className="flex size-full items-center justify-center text-sm text-muted-foreground">
                        Upload pending
                      </div>
                    )}
                    <label className="absolute left-3 top-3 flex size-8 items-center justify-center rounded-md bg-background/90">
                      <input
                        type="checkbox"
                        aria-label={`Select ${image.filename}`}
                        checked={selectedIds.includes(image.id)}
                        onChange={(event) => {
                          const checked = event.currentTarget.checked;
                          setSelectedIds((ids) =>
                            checked
                              ? [...ids, image.id]
                              : ids.filter((id) => id !== image.id),
                          );
                        }}
                      />
                    </label>
                    <span className="absolute right-3 top-3 rounded-full bg-background/90 px-2 py-1 text-xs font-medium">
                      {image.is_premium ? "Premium" : "Free"}
                    </span>
                  </div>
                  <CardContent className="space-y-3 p-4">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium" title={image.filename}>
                        {image.filename}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {image.status} · {(image.size_bytes / 1024).toFixed(0)} KB
                      </p>
                    </div>
                    <div className="flex items-center justify-between gap-2">
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        disabled={processing || image.status !== "READY"}
                        onClick={() => void togglePremium(image)}
                      >
                        <Check className="size-3" />
                        Make {image.is_premium ? "free" : "premium"}
                      </Button>
                      <Button
                        type="button"
                        size="icon-sm"
                        variant="destructive"
                        aria-label={`Delete ${image.filename}`}
                        disabled={processing}
                        onClick={() => void deleteOne(image)}
                      >
                        <Trash2 />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
        </div>

        {gallery && gallery.total_pages > 1 && (
          <nav
            className="flex items-center justify-center gap-4"
            aria-label="Gallery management pagination"
          >
            <Button
              variant="outline"
              disabled={page <= 1 || loading}
              onClick={() => setPage((current) => current - 1)}
            >
              <ChevronLeft className="size-4" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {gallery.page} of {gallery.total_pages}
            </span>
            <Button
              variant="outline"
              disabled={page >= gallery.total_pages || loading}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
              <ChevronRight className="size-4" />
            </Button>
          </nav>
        )}
      </section>
    </main>
  );
}

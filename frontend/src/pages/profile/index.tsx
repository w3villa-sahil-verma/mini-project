/**
 * Profile management with address suggestions, a map, and PDF export.
 * Requires Maps JavaScript API, Places API (New), and Geocoding API for the configured key.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent, FormEvent, KeyboardEvent } from "react";
import { GoogleMap, MarkerF, useJsApiLoader } from "@react-google-maps/api";
import { jsPDF } from "jspdf";
import { z } from "zod";
import {
  Check,
  LocateFixed,
  Download,
  Loader2,
  MapPin,
  MapPinOff,
  Search,
  TriangleAlert,
  Upload,
} from "lucide-react";

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCurrentLocation } from "@/hooks/useCurrentLocation";
import { handleFetch } from "@/hooks/useFetch";
import type { CommonResponse } from "@/types/common/request";
import { toast } from "sonner";

const LIBRARIES: "places"[] = ["places"];
const MAP_STYLE = { width: "100%", height: "100%" };

type Profile = {
  fullName: string;
  email: string;
  phone: string;
  street: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  location: google.maps.LatLngLiteral | null;
};

type Membership = {
  plan_name: string;
  status: "ACTIVE" | "SCHEDULED" | "EXPIRED";
  starts_at: string | null;
  expires_at: string | null;
  has_premium_access: boolean;
} | null;

type ProfileImageUpload = {
  image_id: number;
  object_key: string;
  upload_url: string;
  expires_in: number;
};

type ProfileImageResult = {
  image_id: number;
  image_url: string;
};

const profileResponseSchema = z.object({
  full_name: z.string(),
  email: z.string(),
  phone: z.string().nullable(),
  street: z.string().nullable(),
  city: z.string().nullable(),
  state: z.string().nullable(),
  postal_code: z.string().nullable(),
  country: z.string().nullable(),
  latitude: z.number().nullable(),
  longitude: z.number().nullable(),
  membership: z
    .object({
      plan_name: z.string(),
      status: z.enum(["ACTIVE", "SCHEDULED", "EXPIRED"]),
      starts_at: z.string().nullable(),
      expires_at: z.string().nullable(),
      has_premium_access: z.boolean(),
    })
    .nullable(),
  profile_image_url: z.string().nullable(),
});

type ProfileResponseData = z.infer<typeof profileResponseSchema>;

const INITIAL_PROFILE: Profile = {
  fullName: "",
  email: "",
  phone: "",
  street: "",
  city: "",
  state: "",
  postalCode: "",
  country: "",
  location: null,
};

type AddressComponent = {
  types: string[];
  longText?: string | null;
  long_name?: string;
};

/* -------------------------------------------------------------------------- */
/* Address auto-suggest (Places API New)                                       */
/* -------------------------------------------------------------------------- */

type AddressAutocompleteProps = {
  value: string;
  onChange: (value: string) => void;
  onSelect: (place: google.maps.places.Place) => void;
  disabled: boolean;
};

function AddressAutocomplete({
  value,
  onChange,
  onSelect,
  disabled,
}: AddressAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<
    google.maps.places.AutocompleteSuggestion[]
  >([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [requestFailed, setRequestFailed] = useState(false);
  const sessionRef = useRef<google.maps.places.AutocompleteSessionToken | null>(
    null,
  );
  const wrapRef = useRef<HTMLDivElement>(null);
  const listId = "address-suggestions";

  // Fetch suggestions, debounced while the user types.
  useEffect(() => {
    if (disabled || value.trim().length < 3) {
      setSuggestions([]);
      return;
    }
    const places = window.google?.maps?.places;
    if (!places?.AutocompleteSuggestion) {
      setRequestFailed(true);
      return;
    }

    const sessionToken =
      sessionRef.current ?? new places.AutocompleteSessionToken();
    sessionRef.current = sessionToken;
    let cancelled = false;
    setRequestFailed(false);
    setLoading(true);

    const timer = setTimeout(async () => {
      try {
        const { suggestions: result } =
          await places.AutocompleteSuggestion.fetchAutocompleteSuggestions({
            input: value,
            sessionToken,
          });
        if (!cancelled) {
          setSuggestions(result.filter((s) => s.placePrediction));
          setActive(-1);
        }
      } catch {
        if (!cancelled) {
          setSuggestions([]);
          setRequestFailed(true);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [value, disabled]);

  // Close on outside click.
  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (
        !(event.target instanceof Node) ||
        !wrapRef.current?.contains(event.target)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const choose = async (
    suggestion: google.maps.places.AutocompleteSuggestion,
  ) => {
    const prediction = suggestion.placePrediction;
    if (!prediction) return;

    setOpen(false);
    setSuggestions([]);
    try {
      const place = prediction.toPlace();
      await place.fetchFields({
        fields: ["formattedAddress", "location", "addressComponents"],
      });
      sessionRef.current = null; // a session ends once a place is fetched
      onSelect(place);
    } catch {
      onChange(prediction.text.text);
    }
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (!open || suggestions.length === 0) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive((index) => (index + 1) % suggestions.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((index) =>
        index <= 0 ? suggestions.length - 1 : index - 1,
      );
    } else if (event.key === "Enter" && active >= 0) {
      event.preventDefault();
      const suggestion = suggestions[active];
      if (suggestion) void choose(suggestion);
    } else if (event.key === "Escape") {
      setOpen(false);
    }
  };

  return (
    <div ref={wrapRef} className="relative">
      <Search
        className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
        aria-hidden
      />
      <Input
        id="address-search"
        role="combobox"
        aria-expanded={open && suggestions.length > 0}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={active >= 0 ? `${listId}-${active}` : undefined}
        autoComplete="off"
        className="pl-9 pr-9"
        placeholder="Start typing your address"
        value={value}
        disabled={disabled}
        onChange={(event) => {
          onChange(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={onKeyDown}
      />
      {loading && (
        <Loader2
          className="absolute right-3 top-1/2 size-4 -translate-y-1/2 animate-spin text-muted-foreground"
          aria-label="Loading suggestions"
        />
      )}

      {requestFailed && (
        <p className="mt-2 text-sm text-destructive" role="status">
          Address suggestions are unavailable. Check the key's website restrictions and
          confirm Places API (New) is enabled in the key's Google Cloud project.
        </p>
      )}

      {open && suggestions.length > 0 && (
        <ul
          id={listId}
          role="listbox"
          className="absolute z-20 mt-1 max-h-72 w-full overflow-auto rounded-md border bg-popover p-1 text-popover-foreground shadow-md"
        >
          {suggestions.map((s, i) => {
            const p = s.placePrediction;
            if (!p) return null;
            const main = p.mainText?.text ?? p.text.text;
            const secondary = p.secondaryText?.text;
            return (
              <li
                key={p.placeId}
                id={`${listId}-${i}`}
                role="option"
                aria-selected={i === active}
                onMouseEnter={() => setActive(i)}
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => void choose(s)}
                className={`flex cursor-pointer items-start gap-2 rounded-sm px-2 py-2 text-sm ${
                  i === active ? "bg-accent text-accent-foreground" : ""
                }`}
              >
                <MapPin className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                <span className="min-w-0">
                  <span className="block truncate font-medium">{main}</span>
                  {secondary && (
                    <span className="block truncate text-xs text-muted-foreground">
                      {secondary}
                    </span>
                  )}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Helpers                                                                     */
/* -------------------------------------------------------------------------- */

function parsePlace(
  place: google.maps.places.Place,
): Pick<
  Profile,
  "street" | "city" | "state" | "postalCode" | "country" | "location"
> {
  return parseAddressComponents(
    place.addressComponents,
    place.location
      ? { lat: place.location.lat(), lng: place.location.lng() }
      : null,
  );
}

function parseAddressComponents(
  components: readonly AddressComponent[] | undefined,
  location: google.maps.LatLngLiteral | null,
): Pick<
  Profile,
  "street" | "city" | "state" | "postalCode" | "country" | "location"
> {
  const get = (type: string) => {
    const component = components?.find((item) => item.types.includes(type));
    return component?.longText ?? component?.long_name ?? "";
  };
  const street = [get("street_number"), get("route")].filter(Boolean).join(" ");
  return {
    street: street || get("sublocality_level_1") || get("premise"),
    city: get("locality") || get("administrative_area_level_2"),
    state: get("administrative_area_level_1"),
    postalCode: get("postal_code"),
    country: get("country"),
    location,
  };
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase();
}

function apiRequest<T>(url: string, init?: RequestInit): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    void handleFetch<T>(url, resolve, reject, init);
  });
}

function downloadProfilePdf(profile: Profile) {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const left = 56;
  let y = 72;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.text(profile.fullName || "Profile", left, y);
  y += 20;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(110);
  doc.text(`Exported on ${new Date().toLocaleDateString()}`, left, y);
  y += 20;
  doc.setDrawColor(210);
  doc.line(left, y, 539, y);
  y += 32;

  const section = (title: string, rows: [string, string][]) => {
    doc.setTextColor(20);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text(title, left, y);
    y += 22;
    rows.forEach(([label, val]) => {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(110);
      doc.text(label, left, y);
      doc.setTextColor(20);
      doc.setFontSize(11);
      doc.text(doc.splitTextToSize(val || "Not provided", 340), left + 140, y);
      y += 22;
    });
    y += 14;
  };

  section("Personal details", [
    ["Full name", profile.fullName],
    ["Email", profile.email],
    ["Phone", profile.phone],
  ]);
  section("Address", [
    ["Street", profile.street],
    ["City", profile.city],
    ["State / region", profile.state],
    ["Postal code", profile.postalCode],
    ["Country", profile.country],
    [
      "Coordinates",
      profile.location
        ? `${profile.location.lat.toFixed(5)}, ${profile.location.lng.toFixed(5)}`
        : "",
    ],
  ]);

  doc.save(`${(profile.fullName || "profile").replace(/\s+/g, "-").toLowerCase()}-profile.pdf`);
}

/* -------------------------------------------------------------------------- */
/* Page                                                                        */
/* -------------------------------------------------------------------------- */

export function ProfilePage() {
  const [profile, setProfile] = useState<Profile>(INITIAL_PROFILE);
  const [membership, setMembership] = useState<Membership>(null);
  const [profileImageUrl, setProfileImageUrl] = useState<string | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const { getCurrentLocation, loading: locating } = useCurrentLocation();

  const { isLoaded, loadError: mapLoadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? "",
    libraries: LIBRARIES,
  });

  const applyApiProfile = useCallback((data: ProfileResponseData) => {
    const nextProfile: Profile = {
      fullName: data.full_name,
      email: data.email,
      phone: data.phone ?? "",
      street: data.street ?? "",
      city: data.city ?? "",
      state: data.state ?? "",
      postalCode: data.postal_code ?? "",
      country: data.country ?? "",
      location:
        data.latitude !== null && data.longitude !== null
          ? { lat: data.latitude, lng: data.longitude }
          : null,
    };
    setProfile(nextProfile);
    setMembership(data.membership);
    setProfileImageUrl(data.profile_image_url);
    setSearch([nextProfile.street, nextProfile.city].filter(Boolean).join(", "));
  }, []);

  const loadProfile = useCallback(() => {
    setLoading(true);
    setLoadError(null);
    void handleFetch<CommonResponse<ProfileResponseData>>(
      "/api/v1/users/me",
      (response) => {
        const parsed = profileResponseSchema.safeParse(response.data);
        if (!parsed.success) {
          const message = "Unexpected profile data format.";
          setLoadError(message);
          toast.error(message);
        } else {
          applyApiProfile(parsed.data);
        }
        setLoading(false);
      },
      (error) => {
        setLoadError(error.message);
        toast.error(error.message);
        setLoading(false);
      },
    );
  }, [applyApiProfile]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const set = (key: Exclude<keyof Profile, "location">) => (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    setSaved(false);
    setProfile((previous) => ({ ...previous, [key]: event.target.value }));
  };

  const handleSelect = useCallback((place: google.maps.places.Place) => {
    const parsed = parsePlace(place);
    setSaved(false);
    setProfile((previous) => ({ ...previous, ...parsed }));
    setSearch(place.formattedAddress ?? "");
  }, []);

  const handleUseCurrentLocation = async () => {
    try {
      const currentLocation = await getCurrentLocation();
      const address = parseAddressComponents(
        currentLocation.addressComponents,
        currentLocation.coordinates,
      );
      setProfile((previous) => ({ ...previous, ...address }));
      setSearch(currentLocation.formattedAddress);
      setSaved(false);
      toast.success("Current location added to your profile.");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Could not determine your current location.";
      toast.error(message);
    }
  };

  const handleSave = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setSaved(false);
    void handleFetch<CommonResponse<ProfileResponseData>>(
      "/api/v1/users/me",
      (response) => {
        const parsed = profileResponseSchema.safeParse(response.data);
        if (!parsed.success) {
          toast.error("Unexpected profile data format.");
        } else {
          applyApiProfile(parsed.data);
          setSaved(true);
          toast.success(response.message);
        }
        setSaving(false);
      },
      (error) => {
        toast.error(error.message);
        setSaving(false);
      },
      {
        method: "PUT",
        body: JSON.stringify({
          full_name: profile.fullName,
          email: profile.email,
          phone: profile.phone || null,
          street: profile.street || null,
          city: profile.city || null,
          state: profile.state || null,
          postal_code: profile.postalCode || null,
          country: profile.country || null,
          latitude: profile.location?.lat ?? null,
          longitude: profile.location?.lng ?? null,
        }),
      },
    );
  };

  const handleProfileImageChange = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = "";
    if (!file) return;

    setUploadingImage(true);
    try {
      const presignResponse = await apiRequest<
        CommonResponse<ProfileImageUpload>
      >("/api/v1/uploads/presign", {
        method: "POST",
        body: JSON.stringify({
          filename: file.name,
          content_type: file.type,
          size_bytes: file.size,
        }),
      });

      const uploadResponse = await fetch(presignResponse.data.upload_url, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });
      if (!uploadResponse.ok) {
        throw new Error(
          `Image storage rejected the upload (${uploadResponse.status}).`,
        );
      }

      const completedResponse = await apiRequest<
        CommonResponse<ProfileImageResult>
      >(`/api/v1/uploads/${presignResponse.data.image_id}/complete`, {
        method: "POST",
      });
      setProfileImageUrl(completedResponse.data.image_url);
      toast.success("Profile image updated.");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not upload profile image.",
      );
    } finally {
      setUploadingImage(false);
    }
  };

  const mapOptions = useMemo(
    () => ({
      disableDefaultUI: true,
      zoomControl: true,
      clickableIcons: false,
      gestureHandling: "cooperative",
    }),
    []
  );

  if (loading) {
    return (
      <main className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6">
        <p className="text-sm text-muted-foreground" role="status">
          Loading profile...
        </p>
      </main>
    );
  }

  if (loadError) {
    return (
      <main className="mx-auto w-full max-w-5xl space-y-4 px-4 py-8 sm:px-6">
        <p className="text-sm text-destructive" role="alert">
          Could not load your profile: {loadError}
        </p>
        <Button variant="outline" onClick={loadProfile}>
          Retry
        </Button>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-4 py-8 sm:px-6">      
      {/* Header */}
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex flex-col items-center gap-2">
            <Avatar className="size-16">
              <AvatarImage
                src={profileImageUrl ?? undefined}
                alt={`${profile.fullName || "Profile"} profile`}
              />
              <AvatarFallback className="text-lg">
                {initials(profile.fullName)}
              </AvatarFallback>
            </Avatar>
            <input
              ref={imageInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="sr-only"
              onChange={handleProfileImageChange}
              aria-label="Choose profile image"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={uploadingImage}
              onClick={() => imageInputRef.current?.click()}
            >
              <Upload className="size-4" />
              {uploadingImage ? "Uploading..." : "Change photo"}
            </Button>
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {profile.fullName || "Your profile"}
            </h1>
            <p className="text-sm text-muted-foreground">
              {profile.email || "Add your details below"}
            </p>
          </div>
        </div>
        <Button variant="outline" onClick={() => downloadProfilePdf(profile)}>
          <Download className="size-4" />
          Download profile
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Membership</CardTitle>
          <CardDescription>Your current plan and access status.</CardDescription>
        </CardHeader>
        <CardContent>
          {membership ? (
            <div className="grid gap-3 text-sm sm:grid-cols-3">
              <div>
                <p className="text-muted-foreground">Plan</p>
                <p className="font-medium">{membership.plan_name}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Status</p>
                <p className="font-medium">{membership.status}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Premium access</p>
                <p className="font-medium">
                  {membership.has_premium_access ? "Available" : "Unavailable"}
                </p>
              </div>
              {membership.expires_at && (
                <p className="text-muted-foreground sm:col-span-3">
                  {membership.status === "EXPIRED" ? "Expired" : "Ends"}{" "}
                  {new Date(membership.expires_at).toLocaleString()}
                </p>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No active or previous membership.
            </p>
          )}
        </CardContent>
      </Card>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Personal details */}
        <Card>
          <CardHeader>
            <CardTitle>Personal details</CardTitle>
            <CardDescription>How we contact you and address you.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="fullName">Full name</Label>
              <Input
                id="fullName"
                autoComplete="name"
                value={profile.fullName}
                onChange={set("fullName")}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                value={profile.email}
                onChange={set("email")}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                type="tel"
                autoComplete="tel"
                value={profile.phone}
                onChange={set("phone")}
              />
            </div>
          </CardContent>
        </Card>

        {/* Address + map */}
        <Card>
          <CardHeader>
            <CardTitle>Address</CardTitle>
            <CardDescription>
              Search for your address and pick a suggestion. You can adjust the fields afterwards.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="address-search">Find address</Label>
                <AddressAutocomplete
                  value={search}
                  onChange={setSearch}
                  onSelect={handleSelect}
                  disabled={!isLoaded || Boolean(mapLoadError)}
                />
                {mapLoadError && (
                  <p className="flex items-center gap-2 text-sm text-destructive" role="alert">
                    <TriangleAlert className="size-4" />
                    Address search and current location are unavailable. Enter your address manually.
                  </p>
                )}
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleUseCurrentLocation}
                  disabled={!isLoaded || locating || Boolean(mapLoadError)}
                >
                  {locating ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <LocateFixed className="size-4" />
                  )}
                  {locating ? "Finding location..." : "Use current location"}
                </Button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="street">Street address</Label>
                <Input
                  id="street"
                  autoComplete="address-line1"
                  value={profile.street}
                  onChange={set("street")}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    autoComplete="address-level2"
                    value={profile.city}
                    onChange={set("city")}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State / region</Label>
                  <Input
                    id="state"
                    autoComplete="address-level1"
                    value={profile.state}
                    onChange={set("state")}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="postalCode">Postal code</Label>
                  <Input
                    id="postalCode"
                    autoComplete="postal-code"
                    value={profile.postalCode}
                    onChange={set("postalCode")}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="country">Country</Label>
                  <Input
                    id="country"
                    autoComplete="country-name"
                    value={profile.country}
                    onChange={set("country")}
                  />
                </div>
              </div>
            </div>

            {/* Map */}
            <div
              className="min-h-64 overflow-hidden rounded-lg border bg-muted lg:min-h-full"
              aria-label="Map showing your address"
            >
              {isLoaded && profile.location ? (
                <GoogleMap
                  mapContainerStyle={MAP_STYLE}
                  center={profile.location}
                  zoom={15}
                  options={mapOptions}
                >
                  <MarkerF position={profile.location} />
                </GoogleMap>
              ) : (
                <div className="flex h-full min-h-64 flex-col items-center justify-center gap-2 p-6 text-center text-sm text-muted-foreground">
                  {mapLoadError ? (
                    <TriangleAlert className="size-6" />
                  ) : !isLoaded ? (
                    <Loader2 className="size-6 animate-spin" />
                  ) : (
                    <MapPinOff className="size-6" />
                  )}
                  <p>
                    {mapLoadError
                      ? "The map couldn't load. Check your connection and try again."
                      : !isLoaded
                      ? "Loading map…"
                      : "Pick an address suggestion to see it on the map."}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3">
          <p className="text-sm text-muted-foreground" role="status" aria-live="polite">
            {saved && (
              <span className="inline-flex items-center gap-1">
                <Check className="size-4" /> Changes saved
              </span>
            )}
          </p>
          <Button type="submit" disabled={saving}>
            {saving && <Loader2 className="size-4 animate-spin" />}
            Save changes
          </Button>
        </div>
      </form>
    </main>
  );
}
/**
 * ProfilePage.jsx
 * Covers 4.2 (profile + address auto-suggest + map) and 4.3 (profile download).
 *
 * Install:
 *   npm i @react-google-maps/api jspdf lucide-react
 *   npx shadcn@latest add button input label card avatar separator
 *
 * Env (Vite): VITE_GOOGLE_MAPS_API_KEY
 *   In Google Cloud enable: Maps JavaScript API + Places API (New)
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { GoogleMap, MarkerF, useJsApiLoader } from "@react-google-maps/api";
import { jsPDF } from "jspdf";
import {
  Check,
  Download,
  Loader2,
  MapPin,
  MapPinOff,
  Search,
  TriangleAlert,
} from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
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

const LIBRARIES = ["places"];
const MAP_STYLE = { width: "100%", height: "100%" };

const INITIAL_PROFILE = {
  fullName: "",
  email: "",
  phone: "",
  street: "",
  city: "",
  state: "",
  postalCode: "",
  country: "",
  location: null, // { lat, lng }
};

/* -------------------------------------------------------------------------- */
/* Address auto-suggest (Places API New)                                       */
/* -------------------------------------------------------------------------- */

function AddressAutocomplete({ value, onChange, onSelect, disabled }) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [requestFailed, setRequestFailed] = useState(false);
  const sessionRef = useRef(null);
  const wrapRef = useRef(null);
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

    sessionRef.current ??= new places.AutocompleteSessionToken();
    let cancelled = false;
    setRequestFailed(false);
    setLoading(true);

    const timer = setTimeout(async () => {
      try {
        const { suggestions: result } =
          await places.AutocompleteSuggestion.fetchAutocompleteSuggestions({
            input: value,
            sessionToken: sessionRef.current,
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
    const close = (e) => {
      if (!wrapRef.current?.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const choose = async (suggestion) => {
    setOpen(false);
    setSuggestions([]);
    try {
      const place = suggestion.placePrediction.toPlace();
      await place.fetchFields({
        fields: ["formattedAddress", "location", "addressComponents"],
      });
      sessionRef.current = null; // a session ends once a place is fetched
      onSelect(place);
    } catch {
      onChange(suggestion.placePrediction.text.text);
    }
  };

  const onKeyDown = (e) => {
    if (!open || suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => (i + 1) % suggestions.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => (i <= 0 ? suggestions.length - 1 : i - 1));
    } else if (e.key === "Enter" && active >= 0) {
      e.preventDefault();
      choose(suggestions[active]);
    } else if (e.key === "Escape") {
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
        onChange={(e) => {
          onChange(e.target.value);
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
            const main = p.mainText?.text ?? p.text.text;
            const secondary = p.secondaryText?.text;
            return (
              <li
                key={p.placeId}
                id={`${listId}-${i}`}
                role="option"
                aria-selected={i === active}
                onMouseEnter={() => setActive(i)}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => choose(s)}
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

function parsePlace(place) {
  const get = (type) =>
    place.addressComponents?.find((c) => c.types.includes(type))?.longText ?? "";
  const street = [get("street_number"), get("route")].filter(Boolean).join(" ");
  return {
    street: street || get("sublocality_level_1") || get("premise"),
    city: get("locality") || get("administrative_area_level_2"),
    state: get("administrative_area_level_1"),
    postalCode: get("postal_code"),
    country: get("country"),
    location: place.location
      ? { lat: place.location.lat(), lng: place.location.lng() }
      : null,
  };
}

function initials(name) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase();
}

function downloadProfilePdf(profile) {
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

  const section = (title, rows) => {
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

export function ProfilePage({ initialProfile = INITIAL_PROFILE, onSave }) {
  const [profile, setProfile] = useState({ ...INITIAL_PROFILE, ...initialProfile });
  const [search, setSearch] = useState(
    [initialProfile.street, initialProfile.city].filter(Boolean).join(", ")
  );
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? "",
    libraries: LIBRARIES,
  });

  const set = (key) => (e) => {
    setSaved(false);
    setProfile((p) => ({ ...p, [key]: e.target.value }));
  };

  const handleSelect = useCallback((place) => {
    const parsed = parsePlace(place);
    setSaved(false);
    setProfile((p) => ({ ...p, ...parsed }));
    setSearch(place.formattedAddress ?? "");
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave?.(profile);
      setSaved(true);
    } finally {
      setSaving(false);
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

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-4 py-8 sm:px-6">
      {/* Header */}
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Avatar className="size-14">
            <AvatarFallback className="text-lg">{initials(profile.fullName)}</AvatarFallback>
          </Avatar>
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
                {loadError ? (
                  <p className="flex items-center gap-2 text-sm text-destructive" role="alert">
                    <TriangleAlert className="size-4" />
                    Address search is unavailable. Enter your address manually.
                  </p>
                ) : (
                  <AddressAutocomplete
                    value={search}
                    onChange={setSearch}
                    onSelect={handleSelect}
                    disabled={!isLoaded}
                  />
                )}
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
                  {loadError ? (
                    <TriangleAlert className="size-6" />
                  ) : !isLoaded ? (
                    <Loader2 className="size-6 animate-spin" />
                  ) : (
                    <MapPinOff className="size-6" />
                  )}
                  <p>
                    {loadError
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
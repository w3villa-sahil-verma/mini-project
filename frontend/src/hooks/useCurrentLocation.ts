import { useCallback, useState } from "react";

export type CurrentLocation = {
  coordinates: google.maps.LatLngLiteral;
  formattedAddress: string;
  addressComponents: google.maps.GeocoderAddressComponent[];
};

function getPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Location is not supported by this browser."));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      resolve,
      (error) => {
        const message =
          error.code === error.PERMISSION_DENIED
            ? "Location permission was denied. Allow location access and try again."
            : error.code === error.POSITION_UNAVAILABLE
              ? "Your current location is unavailable."
              : "The request for your location timed out. Please try again.";
        reject(new Error(message));
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
    );
  });
}

export function useCurrentLocation() {
  const [loading, setLoading] = useState(false);

  const getCurrentLocation = useCallback(async (): Promise<CurrentLocation> => {
    setLoading(true);
    try {
      const position = await getPosition();
      const coordinates = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };
      const geocoder = new google.maps.Geocoder();
      const { results } = await geocoder.geocode({ location: coordinates });
      const address = results[0];

      if (!address) {
        throw new Error("No address could be found for your current location.");
      }

      return {
        coordinates,
        formattedAddress: address.formatted_address,
        addressComponents: address.address_components,
      };
    } finally {
      setLoading(false);
    }
  }, []);

  return { getCurrentLocation, loading };
}

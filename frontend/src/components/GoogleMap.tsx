import { useEffect, useRef, useState } from "react";
import type { Place } from "@/types/place";

const GOOGLE_MAPS_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined;
let loaderPromise: Promise<void> | null = null;

function loadGoogleMaps(): Promise<void> {
  if (!GOOGLE_MAPS_KEY) {
    return Promise.reject(new Error("VITE_GOOGLE_MAPS_API_KEY is not set"));
  }
  if ((window as any).google?.maps) return Promise.resolve();
  if (loaderPromise) return loaderPromise;

  const existing = document.getElementById("google-maps-js");
  if (existing) {
    loaderPromise = new Promise((resolve, reject) => {
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("Failed to load Google Maps")), {
        once: true,
      });
    });
    return loaderPromise;
  }

  loaderPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.id = "google-maps-js";
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_KEY}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Google Maps"));
    document.head.appendChild(script);
  });
  return loaderPromise;
}

interface GoogleMapProps {
  places: Place[];
  highlightedId?: string;
  onPlaceClick?: (place: Place) => void;
}

export function GoogleMap({ places, highlightedId, onPlaceClick }: GoogleMapProps) {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const instanceRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<Map<string, google.maps.Marker>>(new Map());
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    loadGoogleMaps()
      .then(() => {
        if (!mounted || !mapRef.current) return;
        setLoadError(null);
        const center = { lat: 25.0330, lng: 121.5654 };
        instanceRef.current = new google.maps.Map(mapRef.current, {
          center,
          zoom: 13,
        });
      })
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : "Failed to load Google Maps";
        setLoadError(msg);
        console.error(err);
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const map = instanceRef.current;
    if (!map) return;

    markersRef.current.forEach((marker) => marker.setMap(null));
    markersRef.current.clear();

    const bounds = new google.maps.LatLngBounds();
    places.forEach((p) => {
      if (p.latitude == null || p.longitude == null) return;
      const position = { lat: p.latitude, lng: p.longitude };
      const marker = new google.maps.Marker({
        position,
        map,
        title: p.name,
      });
      marker.addListener("click", () => onPlaceClick?.(p));
      markersRef.current.set(p.id, marker);
      bounds.extend(position);
    });

    if (places.length > 0) {
      map.fitBounds(bounds, 80);
    }
  }, [places, onPlaceClick]);

  useEffect(() => {
    markersRef.current.forEach((marker, id) => {
      if (id === highlightedId) {
        marker.setAnimation(google.maps.Animation.BOUNCE);
      } else {
        marker.setAnimation(null);
      }
    });
  }, [highlightedId]);

  if (loadError) {
    return (
      <div className="flex h-full w-full items-center justify-center p-6 text-center text-sm text-red-700">
        {loadError}
      </div>
    );
  }

  return <div ref={mapRef} className="h-full w-full" />;
}

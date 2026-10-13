import { useEffect, useRef, useState } from "react";

const GOOGLE_MAPS_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined;
let loaderPromise: Promise<void> | null = null;

function loadGoogleMaps(): Promise<void> {
  if (!GOOGLE_MAPS_KEY) {
    return Promise.reject(new Error("地圖無法顯示：frontend/.env 沒有設定 VITE_GOOGLE_MAPS_API_KEY"));
  }
  if ("google" in window && window.google?.maps) return Promise.resolve();
  if (loaderPromise) return loaderPromise;

  const existing = document.getElementById("google-maps-js");
  if (existing) {
    loaderPromise = new Promise((resolve, reject) => {
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("Google 地圖載入失敗，請檢查網路或前端金鑰")), {
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
    script.onerror = () => reject(new Error("Google 地圖載入失敗，請檢查網路或前端金鑰"));
    document.head.appendChild(script);
  });
  return loaderPromise;
}

export interface MapPin {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

interface GoogleMapProps {
  /** In rank order; pins are labelled 1, 2, 3… */
  pins: MapPin[];
  origin?: { lat: number; lng: number } | null;
  highlightedId?: string | null;
  onPinClick?: (id: string) => void;
}

const TAIPEI = { lat: 25.033, lng: 121.5654 };

export function GoogleMap({ pins, origin, highlightedId, onPinClick }: GoogleMapProps) {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const instanceRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<Map<string, google.maps.Marker>>(new Map());
  const originRef = useRef<google.maps.Marker | null>(null);
  const [ready, setReady] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    loadGoogleMaps()
      .then(() => {
        if (!mounted || !mapRef.current) return;
        instanceRef.current = new google.maps.Map(mapRef.current, {
          center: TAIPEI,
          zoom: 14,
          disableDefaultUI: true,
          zoomControl: true,
          clickableIcons: false,
          gestureHandling: "greedy",
        });
        setReady(true);
      })
      .catch((err: unknown) => {
        setLoadError(err instanceof Error ? err.message : "Google 地圖載入失敗");
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const map = instanceRef.current;
    if (!ready || !map) return;

    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current.clear();
    originRef.current?.setMap(null);

    const bounds = new google.maps.LatLngBounds();
    if (origin) {
      originRef.current = new google.maps.Marker({
        position: origin,
        map,
        title: "出發點",
        zIndex: 1,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 8,
          fillColor: "#2563eb",
          fillOpacity: 1,
          strokeColor: "#ffffff",
          strokeWeight: 3,
        },
      });
      bounds.extend(origin);
    }
    pins.forEach((pin, i) => {
      const position = { lat: pin.latitude, lng: pin.longitude };
      const marker = new google.maps.Marker({
        position,
        map,
        title: pin.name,
        label: { text: String(i + 1), color: "#ffffff", fontWeight: "700" },
        zIndex: 10 + pins.length - i,
      });
      marker.addListener("click", () => onPinClick?.(pin.id));
      markersRef.current.set(pin.id, marker);
      bounds.extend(position);
    });

    if (pins.length > 0) {
      map.fitBounds(bounds, 48);
      if ((map.getZoom() ?? 0) > 17) map.setZoom(17);
    } else if (origin) {
      map.setCenter(origin);
    }
  }, [ready, pins, origin, onPinClick]);

  useEffect(() => {
    markersRef.current.forEach((marker, id) => {
      marker.setAnimation(id === highlightedId ? google.maps.Animation.BOUNCE : null);
    });
    const selected = highlightedId ? markersRef.current.get(highlightedId) : undefined;
    const pos = selected?.getPosition();
    if (pos) instanceRef.current?.panTo(pos);
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

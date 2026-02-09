import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import type { Cafe } from "@/types/cafe";

// Fix default marker icon issue with bundlers
const defaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const highlightIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [30, 49],
  iconAnchor: [15, 49],
  popupAnchor: [1, -40],
  shadowSize: [49, 49],
  className: "hue-rotate-[200deg] brightness-150",
});

function FitBounds({ cafes }: { cafes: Cafe[] }) {
  const map = useMap();
  const validCafes = cafes.filter((c) => c.latitude && c.longitude);
  if (validCafes.length > 0) {
    const bounds = L.latLngBounds(
      validCafes.map((c) => [c.latitude, c.longitude])
    );
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
  }
  return null;
}

interface CafeMapProps {
  cafes: Cafe[];
  highlightedId?: string;
  onCafeClick?: (cafe: Cafe) => void;
}

export function CafeMap({ cafes, highlightedId, onCafeClick }: CafeMapProps) {
  // Default center: Taipei
  const center: [number, number] = [25.042, 121.535];

  return (
    <MapContainer
      center={center}
      zoom={13}
      className="h-full w-full rounded-xl"
      style={{ minHeight: "400px" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitBounds cafes={cafes} />
      {cafes
        .filter((c) => c.latitude && c.longitude)
        .map((cafe) => (
          <Marker
            key={cafe.id}
            position={[cafe.latitude, cafe.longitude]}
            icon={cafe.id === highlightedId ? highlightIcon : defaultIcon}
            eventHandlers={{
              click: () => onCafeClick?.(cafe),
            }}
          >
            <Popup>
              <div className="text-sm">
                <p className="font-bold text-base">{cafe.name}</p>
                <p className="text-gray-600">{cafe.address}</p>
                <div className="mt-1 space-y-0.5 text-xs">
                  <p>WiFi: {cafe.wifi} / Socket: {cafe.socket}</p>
                  <p>Quiet: {cafe.quiet} / Seat: {cafe.seat}</p>
                  {cafe.open_time && <p>{cafe.open_time}</p>}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
    </MapContainer>
  );
}

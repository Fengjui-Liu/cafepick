import type { Area } from "@/types/cafe";
import type { PlaceRecommendation, Place } from "@/types/place";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getRecommendations(
  city: string,
  district?: string,
  topN = 5,
  transit?: { name: string; latitude: number; longitude: number },
  maxWalkMinutes?: number
) {
  const params = new URLSearchParams();
  params.set("city", city);
  if (district) params.set("district", district);
  if (transit) {
    params.set("transit_name", transit.name);
    params.set("transit_lat", String(transit.latitude));
    params.set("transit_lng", String(transit.longitude));
  }
  if (maxWalkMinutes) params.set("max_walk_minutes", String(maxWalkMinutes));
  params.set("top_n", String(topN));

  const data = await fetchJSON<{ recommendations: PlaceRecommendation[] }>(
    `${API_BASE}/api/cafes/recommend?${params}`
  );
  return data.recommendations;
}

export async function getAreas() {
  const data = await fetchJSON<{ areas: Area[] }>(`${API_BASE}/api/areas`);
  return data.areas;
}

export async function getArea(city: string) {
  const data = await fetchJSON<{ areas: Area[] }>(
    `${API_BASE}/api/areas?city=${encodeURIComponent(city)}`
  );
  return data.areas[0];
}

export async function getTransitPoints(
  city: string,
  district?: string,
  query?: string
) {
  const params = new URLSearchParams();
  params.set("city", city);
  if (district) params.set("district", district);
  if (query) params.set("query", query);
  const data = await fetchJSON<{ transit_points: Place[] }>(
    `${API_BASE}/api/transit?${params}`
  );
  return data.transit_points;
}

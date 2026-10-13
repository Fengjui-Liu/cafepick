import type { Area } from "@/types/cafe";
import type { PlaceRecommendation, Place, Mode, RecommendResponse } from "@/types/place";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url);
  } catch {
    throw new Error(`連不到後端 ${API_BASE}，請確認 run_dev.sh 有在跑`);
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    // FastAPI validation errors come back as a list of {loc, msg}.
    const message = Array.isArray(detail)
      ? detail.map((d) => `${(d.loc ?? []).join(".")}: ${d.msg}`).join("；")
      : detail;
    throw new Error(message || `API error: ${res.status}`);
  }
  return res.json();
}

export async function getRecommendations(
  city: string,
  district?: string,
  keyword?: string,
  topN = 5,
  transit?: { name: string; latitude: number; longitude: number },
  maxWalkMinutes?: number
) {
  const params = new URLSearchParams();
  params.set("city", city);
  if (district) params.set("district", district);
  if (keyword) params.set("query", keyword);
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

export interface RecommendParams {
  mode: Mode;
  origin:
    | { lat: number; lng: number }
    | { station: string }
    | { district: string; city?: string };
  pet?: boolean;
  maxWalkMinutes?: number;
  /** ids already shown, for 「換 3 間」 */
  exclude?: string[];
  topN?: number;
}

export async function recommend(p: RecommendParams) {
  const params = new URLSearchParams({ mode: p.mode });
  if ("lat" in p.origin) {
    params.set("lat", String(p.origin.lat));
    params.set("lng", String(p.origin.lng));
  } else if ("station" in p.origin) {
    params.set("station", p.origin.station);
  } else {
    params.set("district", p.origin.district);
    if (p.origin.city) params.set("city", p.origin.city);
  }
  if (p.pet) params.set("pet", "true");
  if (p.maxWalkMinutes) params.set("max_walk_minutes", String(p.maxWalkMinutes));
  if (p.exclude?.length) params.set("exclude", p.exclude.join(","));
  if (p.topN) params.set("top_n", String(p.topN));
  return fetchJSON<RecommendResponse>(`${API_BASE}/api/recommend?${params}`);
}

export async function searchStations(q: string) {
  const data = await fetchJSON<{ stations: { name: string; lines: string[] }[] }>(
    `${API_BASE}/api/stations?q=${encodeURIComponent(q)}`
  );
  return data.stations;
}

import type { Mode, RecommendResponse } from "@/types/place";

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

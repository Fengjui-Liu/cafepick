import type { CafeRecommendation, Area, Filters } from "@/types/cafe";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getRecommendations(
  filters: Filters,
  topN = 5,
  latitude?: number,
  longitude?: number
) {
  const params = new URLSearchParams();
  params.set("city", filters.city);
  if (filters.district) params.set("district", filters.district);
  if (filters.mrt) params.set("mrt", filters.mrt);
  if (filters.has_wifi) params.set("has_wifi", "true");
  if (filters.has_socket) params.set("has_socket", "true");
  if (filters.quiet_level) params.set("quiet_level", filters.quiet_level);
  if (filters.price_range) params.set("price_range", filters.price_range);
  if (filters.limited_time) params.set("limited_time", filters.limited_time);
  if (filters.has_reservation) params.set("has_reservation", "true");
  params.set("top_n", String(topN));
  if (latitude) params.set("latitude", String(latitude));
  if (longitude) params.set("longitude", String(longitude));

  const data = await fetchJSON<{ recommendations: CafeRecommendation[] }>(
    `${API_BASE}/api/cafes/recommend?${params}`
  );
  return data.recommendations;
}

export async function getAreas() {
  const data = await fetchJSON<{ areas: Area[] }>(`${API_BASE}/api/areas`);
  return data.areas;
}

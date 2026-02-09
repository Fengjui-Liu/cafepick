import type { Cafe, CafeRecommendation, Area, Filters } from "@/types/cafe";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

function shouldIncludeParam(val: unknown): boolean {
  return !(
    val === undefined ||
    val === null ||
    val === "" ||
    val === 0 ||
    val === false
  );
}

export async function getCafes(filters?: Partial<Filters>) {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, val]) => {
      if (shouldIncludeParam(val)) {
        params.set(key, String(val));
      }
    });
  }
  const data = await fetchJSON<{ total: number; cafes: Cafe[] }>(
    `${API_BASE}/api/cafes?${params}`
  );
  return data;
}

export async function getRecommendations(
  filters: Partial<Filters>,
  topN = 3,
  latitude?: number,
  longitude?: number
) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, val]) => {
    if (shouldIncludeParam(val)) {
      params.set(key, String(val));
    }
  });
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

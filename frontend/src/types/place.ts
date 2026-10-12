export interface NearestMrt {
  name: string;
  lines: string[];
  distance_km: number;
  walk_minutes: number;
}

/** Cafe Nomad ratings (0–5). null = no one has rated it. */
export interface WorkInfo {
  wifi: number | null;
  socket: number | null;
  quiet: number | null;
  seat: number | null;
  tasty: number | null;
  cheap: number | null;
  music: number | null;
  limited_time: "yes" | "no" | "maybe" | null;
  standing_desk: "yes" | "no" | null;
  open_time: string | null;
}

export interface Place {
  id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  rating?: number;
  user_ratings_total?: number;
  price_level?: string;
  url?: string;
  city?: string;
  district?: string;
  mrt_station?: string;
  mrt_distance_km?: number;
  mrt_walk_minutes?: number;
  transit_name?: string;
  transit_distance_km?: number;
  transit_walk_minutes?: number;
  google_maps_url?: string;
  open_now?: boolean | null;
  opening_hours?: string[] | null;
  /** null = the shop hasn't told Google (show as 未確認) */
  pet_friendly?: boolean | null;
  reservable?: boolean | null;
  good_for_groups?: boolean | null;
  outdoor_seating?: boolean | null;
  serves_dessert?: boolean | null;
  nearest_mrt?: NearestMrt;
  /** null when the shop isn't on Cafe Nomad */
  work?: WorkInfo | null;
  nomad?: { id: string; name: string; match_confidence: number } | null;
}

export interface PlaceRecommendation {
  cafe: Place;
  score: number | null;
  distance_km: number | null;
}

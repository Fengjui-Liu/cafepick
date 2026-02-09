export interface Cafe {
  id: string;
  name: string;
  city: string;
  address: string;
  latitude: number;
  longitude: number;
  url: string;
  mrt: string;
  open_time: string;
  wifi: number;
  socket: number;
  quiet: number;
  tasty: number;
  cheap: number;
  music: number;
  seat: number;
  limited_time: string;
  standing_desk: string;
}

export interface CafeRecommendation {
  cafe: Cafe;
  score: number;
  distance_km: number | null;
}

export interface Area {
  city: string;
  cafe_count: number;
  mrt_stations: string[];
}

export interface Filters {
  city: string;
  wifi: number;
  socket: number;
  quiet: number;
  cheap: number;
  limited_time: string;
  mrt: string;
}

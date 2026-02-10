export interface Cafe {
  id: string;
  name: string;
  city: string;
  district: string;
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
  has_reservation: string;
}

export interface CafeRecommendation {
  cafe: Cafe;
  score: number;
  distance_km: number | null;
}

export interface District {
  name: string;
  mrt_stations: string[];
}

export interface Area {
  city: string;
  city_name: string;
  cafe_count: number;
  districts: District[];
  mrt_stations: string[];
}

export type QuietLevel = "" | "quiet" | "moderate" | "lively";
export type PriceRange = "" | "budget" | "moderate" | "pricey";

export type SortBy = "score" | "quiet" | "price" | "wifi";

export interface Filters {
  city: string;
  district: string;
  mrt: string;
  name: string;
  has_wifi: boolean;
  has_socket: boolean;
  quiet_level: QuietLevel;
  price_range: PriceRange;
  limited_time: string;
  has_reservation: boolean;
}

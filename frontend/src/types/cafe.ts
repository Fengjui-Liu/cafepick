export interface Cafe {
  id: string;
  name: string;
  city: string;
  address: string;
  district?: string;
  latitude: number;
  longitude: number;
  url: string;
  mrt: string;
  mrt_station?: string;
  bus_stop?: string | null;
  open_time: string;
  wifi: number;
  socket: number;
  quiet: number;
  tasty: number;
  cheap: number;
  music: number;
  seat: number;
  price?: number | null;
  quiet_level?: "quiet" | "normal" | "loud";
  has_wifi?: boolean;
  has_socket?: boolean;
  reservable?: boolean | null;
  limited_time: string;
  standing_desk: string;
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
  cafe_count: number;
  city_name: string;
  districts: District[];
  mrt_stations: string[];
}

export interface Filters {
  city: string;
  district: string;
  keyword: string;
  mrt_station: string;
  bus_stop: string;
  wifi: boolean;
  socket: boolean;
  quiet_level: "" | "quiet" | "normal" | "loud";
  max_price: number | null;
  limited_time: string;
  reservable: boolean;
}

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
}

export interface PlaceRecommendation {
  cafe: Place;
  score: number | null;
  distance_km: number | null;
}

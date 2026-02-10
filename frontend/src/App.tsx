import { useState, useEffect } from "react";
import { GoogleMap } from "@/components/GoogleMap";
import { FilterPanel } from "@/components/FilterPanel";
import { PlaceCard } from "@/components/PlaceCard";
import { getRecommendations, getAreas, getArea, getTransitPoints } from "@/services/api";
import type { Filters, Area } from "@/types/cafe";
import type { PlaceRecommendation, Place } from "@/types/place";

const defaultFilters: Filters = {
  city: "taipei",
  district: "",
  mrt_station: "",
  bus_stop: "",
  wifi: false,
  socket: false,
  quiet_level: "",
  max_price: null,
  limited_time: "",
  reservable: false,
};

function App() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [recommendations, setRecommendations] = useState<PlaceRecommendation[]>(
    []
  );
  const [areas, setAreas] = useState<Area[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [transitPoints, setTransitPoints] = useState<Place[]>([]);
  const [selectedTransitId, setSelectedTransitId] = useState<string>("");
  const [transitQuery, setTransitQuery] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [highlightedId, setHighlightedId] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    getAreas()
      .then((areas) => {
        setAreas(areas);
        const initial = areas.find((a) => a.city === defaultFilters.city);
        if (initial) {
          getArea(initial.city)
            .then((detail) => {
              setDistricts(detail.districts?.map((d) => d.name) ?? []);
            })
            .catch(console.error);
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!filters.city) return;
    setSelectedTransitId("");
    getArea(filters.city)
      .then((detail) => {
        const districtNames = detail.districts?.map((d) => d.name) ?? [];
        setDistricts(districtNames);
        if (filters.district && !districtNames.includes(filters.district)) {
          setFilters((prev) => ({ ...prev, district: "" }));
        }
      })
      .catch(console.error);
  }, [filters.city]);

  useEffect(() => {
    if (!filters.city) return;
    const district = filters.district || undefined;
    getTransitPoints(filters.city, district)
      .then((points) => setTransitPoints(points))
      .catch(console.error);
  }, [filters.city, filters.district]);

  const handleSearch = async () => {
    setLoading(true);
    setHasSearched(true);
    try {
      const transit = transitPoints.find((p) => p.id === selectedTransitId);
      const results = await getRecommendations(
        filters.city,
        filters.district,
        8,
        transit
          ? { name: transit.name, latitude: transit.latitude, longitude: transit.longitude }
          : undefined,
        10
      );
      setRecommendations(results);
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleTransitSearch = async () => {
    if (!transitQuery.trim()) return;
    setSelectedTransitId("");
    try {
      const points = await getTransitPoints(filters.city, filters.district, transitQuery.trim());
      setTransitPoints(points);
    } catch (err) {
      console.error("Failed to fetch transit points:", err);
    }
  };

  const handleCafeClick = (cafe: Place) => {
    setHighlightedId(cafe.id);
  };

  const allPlaces = recommendations.map((r) => r.cafe);

  return (
    <div className="min-h-screen">
      <header className="border-b border-[var(--border)] bg-[var(--card)]/70 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-[var(--primary)] text-[var(--primary-foreground)] grid place-items-center shadow-sm">
              ☕️
            </div>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight font-display">
                CafePick
              </h1>
              <p className="text-sm text-[var(--muted-foreground)]">
                使用 Google Places 取得最新咖啡廳資訊
              </p>
            </div>
          </div>
        </div>
      </header>

      <section className="max-w-7xl mx-auto px-6 py-8">
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--card)]/80 hero-glow panel-shadow px-8 py-10">
          <h2 className="text-3xl md:text-4xl font-semibold font-display fade-up">
            CafePick
          </h2>
        </div>
      </section>

      <main className="max-w-7xl mx-auto px-6 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <aside className="lg:col-span-3">
            <div className="sticky top-6 rounded-2xl border border-[var(--border)] bg-[var(--card)]/90 p-5 panel-shadow fade-up delay-2">
              <h2 className="font-semibold text-lg mb-4 font-display">
                篩選條件
              </h2>
              <FilterPanel
                filters={filters}
                onChange={setFilters}
                onSearch={handleSearch}
                areas={areas}
                districts={districts}
                transitPoints={transitPoints}
                selectedTransitId={selectedTransitId}
                onTransitChange={setSelectedTransitId}
                transitQuery={transitQuery}
                onTransitQueryChange={setTransitQuery}
                onTransitSearch={handleTransitSearch}
                loading={loading}
              />
            </div>
          </aside>

          <div className="lg:col-span-9 space-y-6">
            <div className="rounded-2xl border border-[var(--border)] overflow-hidden h-[420px] panel-shadow fade-up">
              {hasSearched && allPlaces.length > 0 ? (
                <GoogleMap
                  places={allPlaces}
                  highlightedId={highlightedId ?? undefined}
                  onPlaceClick={handleCafeClick}
                />
              ) : (
                <div className="h-full flex items-center justify-center bg-[var(--muted)]">
                  <div className="text-center">
                    <p className="text-4xl mb-2">&#9749;</p>
                    <p className="text-[var(--muted-foreground)]">
                      選擇縣市後按「幫我推薦」開始探索
                    </p>
                  </div>
                </div>
              )}
            </div>

            {hasSearched && (
              <div>
                <h2 className="font-semibold text-lg mb-3 font-display">
                  {recommendations.length > 0
                    ? `為你推薦 ${recommendations.length} 間咖啡廳`
                    : "沒有找到符合條件的咖啡廳"}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {recommendations.map((rec, i) => (
                    <PlaceCard
                      key={rec.cafe.id}
                      recommendation={rec}
                      rank={i + 1}
                      isHighlighted={highlightedId === rec.cafe.id}
                      onHover={setHighlightedId}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

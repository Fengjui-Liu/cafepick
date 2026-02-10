import { useState, useEffect } from "react";
import { CafeMap } from "@/components/CafeMap";
import { FilterPanel } from "@/components/FilterPanel";
import { CafeCard } from "@/components/CafeCard";
import { getRecommendations, getAreas } from "@/services/api";
import type { Filters, CafeRecommendation, Cafe, Area } from "@/types/cafe";

const defaultFilters: Filters = {
  city: "taipei",
  district: "",
  mrt: "",
  has_wifi: false,
  has_socket: false,
  quiet_level: "",
  price_range: "",
  limited_time: "",
  has_reservation: false,
};

function App() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [recommendations, setRecommendations] = useState<
    CafeRecommendation[]
  >([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [loading, setLoading] = useState(false);
  const [highlightedId, setHighlightedId] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    getAreas()
      .then((data) => setAreas(data))
      .catch(console.error);
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    setHasSearched(true);
    try {
      const results = await getRecommendations(filters, 5);
      setRecommendations(results);
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCafeClick = (cafe: Cafe) => {
    setHighlightedId(cafe.id);
  };

  const allCafes = recommendations.map((r) => r.cafe);

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <header className="border-b border-[var(--border)] bg-[var(--card)]">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">CafePick</h1>
            <p className="text-sm text-[var(--muted-foreground)]">
              幫你找到最適合的咖啡廳
            </p>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Sidebar: Filters */}
          <aside className="lg:col-span-3">
            <div className="sticky top-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
              <h2 className="font-semibold text-lg mb-4">篩選條件</h2>
              <FilterPanel
                filters={filters}
                onChange={setFilters}
                onSearch={handleSearch}
                areas={areas}
                loading={loading}
              />
            </div>
          </aside>

          {/* Main content */}
          <div className="lg:col-span-9 space-y-6">
            {/* Map */}
            <div className="rounded-xl border border-[var(--border)] overflow-hidden h-[400px]">
              {hasSearched && allCafes.length > 0 ? (
                <CafeMap
                  cafes={allCafes}
                  highlightedId={highlightedId ?? undefined}
                  onCafeClick={handleCafeClick}
                />
              ) : (
                <div className="h-full flex items-center justify-center bg-[var(--muted)]">
                  <div className="text-center">
                    <p className="text-4xl mb-2">&#9749;</p>
                    <p className="text-[var(--muted-foreground)]">
                      設定你的需求，按下「幫我推薦」開始探索
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Results */}
            {hasSearched && (
              <div>
                <h2 className="font-semibold text-lg mb-3">
                  {recommendations.length > 0
                    ? `為你推薦 ${recommendations.length} 間咖啡廳`
                    : "沒有找到符合條件的咖啡廳"}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {recommendations.map((rec, i) => (
                    <CafeCard
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

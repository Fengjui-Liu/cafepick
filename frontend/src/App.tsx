import { useState, useEffect, useCallback, useMemo } from "react";
import { CafeMap } from "@/components/CafeMap";
import { FilterPanel } from "@/components/FilterPanel";
import { CafeCard } from "@/components/CafeCard";
import { CafeDetail } from "@/components/CafeDetail";
import { ResultsSkeleton } from "@/components/Skeleton";
import { Button } from "@/components/ui/Button";
import { getRecommendations, getAreas } from "@/services/api";
import type { Filters, CafeRecommendation, Cafe, Area, SortBy } from "@/types/cafe";

const defaultFilters: Filters = {
  city: "taipei",
  district: "",
  mrt: "",
  name: "",
  has_wifi: false,
  has_socket: false,
  quiet_level: "",
  price_range: "",
  limited_time: "",
  has_reservation: false,
};

const SORT_OPTIONS: { value: SortBy; label: string }[] = [
  { value: "score", label: "推薦分數" },
  { value: "quiet", label: "最安靜" },
  { value: "price", label: "最便宜" },
  { value: "wifi", label: "WiFi 最佳" },
];

function useFavorites() {
  const [favorites, setFavorites] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem("cafepick_favorites");
      return stored ? new Set(JSON.parse(stored)) : new Set();
    } catch {
      return new Set();
    }
  });

  const toggle = useCallback((id: string) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      localStorage.setItem("cafepick_favorites", JSON.stringify([...next]));
      return next;
    });
  }, []);

  return { favorites, toggle };
}

function App() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [recommendations, setRecommendations] = useState<CafeRecommendation[]>([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [loading, setLoading] = useState(false);
  const [highlightedId, setHighlightedId] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [sortBy, setSortBy] = useState<SortBy>("score");
  const [detailCafe, setDetailCafe] = useState<Cafe | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { favorites, toggle: toggleFavorite } = useFavorites();

  useEffect(() => {
    getAreas().then(setAreas).catch(console.error);
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    setHasSearched(true);
    setSidebarOpen(false);
    try {
      const results = await getRecommendations(filters, 10);
      setRecommendations(results);
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  const sortedRecommendations = useMemo(() => {
    const sorted = [...recommendations];
    switch (sortBy) {
      case "quiet":
        sorted.sort((a, b) => (b.cafe.quiet || 0) - (a.cafe.quiet || 0));
        break;
      case "price":
        sorted.sort((a, b) => (b.cafe.cheap || 0) - (a.cafe.cheap || 0));
        break;
      case "wifi":
        sorted.sort((a, b) => (b.cafe.wifi || 0) - (a.cafe.wifi || 0));
        break;
      default:
        sorted.sort((a, b) => b.score - a.score);
    }
    return sorted;
  }, [recommendations, sortBy]);

  const handleCafeClick = (cafe: Cafe) => {
    setHighlightedId(cafe.id);
  };

  const allCafes = recommendations.map((r) => r.cafe);

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <header className="border-b border-[var(--border)] bg-[var(--card)] sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">CafePick</h1>
            <p className="text-sm text-[var(--muted-foreground)] hidden sm:block">
              幫你找到最適合的咖啡廳
            </p>
          </div>
          {/* Mobile filter toggle */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-[var(--border)] text-sm hover:bg-[var(--accent)]"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 010 2H4a1 1 0 01-1-1zm4 6a1 1 0 011-1h8a1 1 0 010 2H8a1 1 0 01-1-1zm2 6a1 1 0 011-1h4a1 1 0 010 2h-4a1 1 0 01-1-1z" /></svg>
            篩選
          </button>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Sidebar: Filters */}
          <>
            {/* Mobile backdrop */}
            {sidebarOpen && (
              <div
                className="fixed inset-0 z-30 bg-black/30 lg:hidden"
                onClick={() => setSidebarOpen(false)}
              />
            )}
            <aside
              className={`
                fixed top-0 left-0 z-40 w-80 h-full overflow-y-auto bg-[var(--card)] border-r border-[var(--border)] p-5 pt-20 transition-transform duration-300
                lg:static lg:z-auto lg:w-auto lg:h-auto lg:overflow-visible lg:border-r-0 lg:pt-0 lg:p-0 lg:translate-x-0 lg:col-span-3
                ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
              `}
            >
              <div className="lg:sticky lg:top-20 rounded-xl lg:border lg:border-[var(--border)] lg:bg-[var(--card)] lg:p-5">
                <h2 className="font-semibold text-lg mb-4">篩選條件</h2>
                <FilterPanel
                  filters={filters}
                  defaultFilters={defaultFilters}
                  onChange={setFilters}
                  onSearch={handleSearch}
                  areas={areas}
                  loading={loading}
                />
              </div>
            </aside>
          </>

          {/* Main content */}
          <div className="lg:col-span-9 space-y-6">
            {/* Map */}
            <div className="rounded-xl border border-[var(--border)] overflow-hidden h-[350px] sm:h-[400px]">
              {hasSearched && allCafes.length > 0 ? (
                <CafeMap
                  cafes={allCafes}
                  highlightedId={highlightedId ?? undefined}
                  onCafeClick={handleCafeClick}
                />
              ) : (
                <div className="h-full flex items-center justify-center bg-[var(--muted)]">
                  <div className="text-center px-4">
                    <p className="text-4xl mb-2">&#9749;</p>
                    <p className="text-[var(--muted-foreground)]">
                      設定你的需求，按下「幫我推薦」開始探索
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Loading skeleton */}
            {loading && (
              <div>
                <h2 className="font-semibold text-lg mb-3">搜尋中...</h2>
                <ResultsSkeleton count={3} />
              </div>
            )}

            {/* Results */}
            {hasSearched && !loading && (
              <div>
                <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                  <h2 className="font-semibold text-lg">
                    {sortedRecommendations.length > 0
                      ? `為你推薦 ${sortedRecommendations.length} 間咖啡廳`
                      : "沒有找到符合條件的咖啡廳"}
                  </h2>
                  {sortedRecommendations.length > 1 && (
                    <div className="flex gap-1">
                      {SORT_OPTIONS.map((opt) => (
                        <Button
                          key={opt.value}
                          variant={sortBy === opt.value ? "primary" : "outline"}
                          size="sm"
                          onClick={() => setSortBy(opt.value)}
                        >
                          {opt.label}
                        </Button>
                      ))}
                    </div>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {sortedRecommendations.map((rec, i) => (
                    <CafeCard
                      key={rec.cafe.id}
                      recommendation={rec}
                      rank={i + 1}
                      isHighlighted={highlightedId === rec.cafe.id}
                      onHover={setHighlightedId}
                      onClick={() => setDetailCafe(rec.cafe)}
                      isFavorite={favorites.has(rec.cafe.id)}
                      onToggleFavorite={toggleFavorite}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Detail Modal */}
      {detailCafe && (
        <CafeDetail
          cafe={detailCafe}
          onClose={() => setDetailCafe(null)}
          isFavorite={favorites.has(detailCafe.id)}
          onToggleFavorite={toggleFavorite}
        />
      )}
    </div>
  );
}

export default App;

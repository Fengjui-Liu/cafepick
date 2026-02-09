import { useState, useEffect } from "react";
import { CafeMap } from "@/components/CafeMap";
import { FilterPanel } from "@/components/FilterPanel";
import { CafeCard } from "@/components/CafeCard";
import { getRecommendations, getAreas } from "@/services/api";
import type { Filters, CafeRecommendation, Cafe, Area } from "@/types/cafe";

const defaultFilters: Filters = {
  city: "taipei",
  district: "",
  mrt_station: "",
  bus_stop: "",
  wifi: false,
  socket: false,
  quiet_level: "",
  max_price: 0,
  limited_time: "",
  reservable: false,
};

function App() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [recommendations, setRecommendations] = useState<
    CafeRecommendation[]
  >([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [mrtStations, setMrtStations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [highlightedId, setHighlightedId] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    getAreas()
      .then((areas) => {
        setAreas(areas);
        const initial = areas.find((a) => a.city === defaultFilters.city);
        if (initial) {
          setMrtStations(initial.mrt_stations);
          setDistricts(initial.districts ?? []);
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    const selected = areas.find((a) => a.city === filters.city);
    if (!selected) return;
    setMrtStations(selected.mrt_stations);
    setDistricts(selected.districts ?? []);
    if (filters.district && !selected.districts?.includes(filters.district)) {
      setFilters((prev) => ({ ...prev, district: "" }));
    }
    if (
      filters.mrt_station &&
      !selected.mrt_stations.includes(filters.mrt_station)
    ) {
      setFilters((prev) => ({ ...prev, mrt_station: "" }));
    }
  }, [areas, filters.city]);

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
    <div className="min-h-screen">
      {/* Header */}
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
                以城市脈絡與工作節奏挑選你的下一杯咖啡
              </p>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-2 text-xs text-[var(--muted-foreground)]">
            <span className="px-3 py-1 rounded-full bg-[var(--secondary)]">
              Focus Mode
            </span>
            <span className="px-3 py-1 rounded-full bg-[var(--secondary)]">
              City-first
            </span>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 py-10">
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--card)]/80 hero-glow panel-shadow px-8 py-10 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-4 fade-up">
            <p className="uppercase tracking-[0.3em] text-xs text-[var(--muted-foreground)]">
              City to Neighborhood
            </p>
            <h2 className="text-3xl md:text-4xl font-semibold leading-tight font-display">
              從縣市到行政區，精準找到你今天要專注的那一間。
            </h2>
            <p className="text-sm md:text-base text-[var(--muted-foreground)] max-w-xl">
              以工作情境為導向：安靜程度、插座、WiFi、價格與訂位一次決定，搭配地圖把路線拉直。
            </p>
            <div className="flex flex-wrap gap-3">
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--secondary)] px-4 py-3 text-sm">
                <div className="text-xs text-[var(--muted-foreground)]">
                  推薦模型
                </div>
                <div className="font-semibold">多因子權重</div>
              </div>
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--secondary)] px-4 py-3 text-sm">
                <div className="text-xs text-[var(--muted-foreground)]">
                  篩選流程
                </div>
                <div className="font-semibold">縣市 → 行政區</div>
              </div>
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--secondary)] px-4 py-3 text-sm">
                <div className="text-xs text-[var(--muted-foreground)]">
                  地圖
                </div>
                <div className="font-semibold">即時標記</div>
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-5 space-y-3 fade-up delay-1">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold">推薦預覽</div>
              <span className="text-xs text-[var(--muted-foreground)]">
                即時更新
              </span>
            </div>
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-4 floaty">
              <div className="text-xs text-[var(--muted-foreground)] mb-1">
                今日最佳
              </div>
              <div className="text-base font-semibold">
                信義區 · 靜謐工作取向
              </div>
              <div className="text-xs text-[var(--muted-foreground)] mt-2">
                WiFi / 插座 / 可訂位
              </div>
            </div>
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-4">
              <div className="text-xs text-[var(--muted-foreground)] mb-1">
                次選
              </div>
              <div className="text-base font-semibold">
                大安區 · 交通便利
              </div>
              <div className="text-xs text-[var(--muted-foreground)] mt-2">
                捷運站步行 6 分鐘
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-6 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Sidebar: Filters */}
          <aside className="lg:col-span-3">
            <div className="sticky top-6 rounded-2xl border border-[var(--border)] bg-[var(--card)]/90 p-5 panel-shadow fade-up delay-2">
              <h2 className="font-semibold text-lg mb-4 font-display">
                篩選條件
              </h2>
              <FilterPanel
                filters={filters}
                onChange={setFilters}
                onSearch={handleSearch}
                cities={areas.length > 0 ? areas.map((a) => a.city) : [filters.city]}
                districts={districts}
                mrtStations={mrtStations}
                loading={loading}
              />
            </div>
          </aside>

          {/* Main content */}
          <div className="lg:col-span-9 space-y-6">
            {/* Map */}
            <div className="rounded-2xl border border-[var(--border)] overflow-hidden h-[420px] panel-shadow fade-up">
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
                <h2 className="font-semibold text-lg mb-3 font-display">
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

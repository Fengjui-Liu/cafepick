import { useMemo } from "react";
import { Button } from "@/components/ui/Button";
import { Toggle } from "@/components/ui/Toggle";
import type { Filters, Area, QuietLevel, PriceRange } from "@/types/cafe";

interface FilterPanelProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  onSearch: () => void;
  areas: Area[];
  loading?: boolean;
}

const QUIET_OPTIONS: { value: QuietLevel; label: string }[] = [
  { value: "", label: "不限" },
  { value: "quiet", label: "安靜" },
  { value: "moderate", label: "普通" },
  { value: "lively", label: "熱鬧" },
];

const PRICE_OPTIONS: { value: PriceRange; label: string }[] = [
  { value: "", label: "不限" },
  { value: "budget", label: "平價 < $100" },
  { value: "moderate", label: "中等 $100-200" },
  { value: "pricey", label: "較貴 > $200" },
];

export function FilterPanel({
  filters,
  onChange,
  onSearch,
  areas,
  loading,
}: FilterPanelProps) {
  const update = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    const next = { ...filters, [key]: value };
    // Reset child selections when parent changes
    if (key === "city") {
      next.district = "";
      next.mrt = "";
    }
    if (key === "district") {
      next.mrt = "";
    }
    onChange(next);
  };

  // Get current area data
  const currentArea = useMemo(
    () => areas.find((a) => a.city === filters.city),
    [areas, filters.city]
  );

  // Get districts for selected city
  const districts = useMemo(
    () => currentArea?.districts ?? [],
    [currentArea]
  );

  // Get MRT stations for selected district, or all if no district selected
  const mrtStations = useMemo(() => {
    if (filters.district) {
      const d = districts.find((d) => d.name === filters.district);
      return d?.mrt_stations ?? [];
    }
    return currentArea?.mrt_stations ?? [];
  }, [currentArea, districts, filters.district]);

  return (
    <div className="space-y-5">
      {/* Location: City → District → MRT */}
      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          地區
        </h3>
        <div className="space-y-2">
          <select
            value={filters.city}
            onChange={(e) => update("city", e.target.value)}
            className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          >
            {areas.map((area) => (
              <option key={area.city} value={area.city}>
                {area.city_name} ({area.cafe_count})
              </option>
            ))}
          </select>

          <select
            value={filters.district}
            onChange={(e) => update("district", e.target.value)}
            className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          >
            <option value="">全部行政區</option>
            {districts.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name}
              </option>
            ))}
          </select>

          <select
            value={filters.mrt}
            onChange={(e) => update("mrt", e.target.value)}
            className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          >
            <option value="">全部捷運站</option>
            {mrtStations.map((mrt) => (
              <option key={mrt} value={mrt}>
                {mrt}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Toggles: WiFi, Socket, Reservation */}
      <div>
        <h3 className="text-sm font-semibold mb-3 text-[var(--muted-foreground)]">
          設施需求
        </h3>
        <div className="space-y-3">
          <Toggle
            label="需要 WiFi"
            checked={filters.has_wifi}
            onChange={(v) => update("has_wifi", v)}
          />
          <Toggle
            label="需要插座"
            checked={filters.has_socket}
            onChange={(v) => update("has_socket", v)}
          />
          <Toggle
            label="可以訂位"
            checked={filters.has_reservation}
            onChange={(v) => update("has_reservation", v)}
          />
        </div>
      </div>

      {/* Quiet Level */}
      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          安靜程度
        </h3>
        <div className="flex flex-wrap gap-2">
          {QUIET_OPTIONS.map((opt) => (
            <Button
              key={opt.value}
              variant={
                filters.quiet_level === opt.value ? "primary" : "outline"
              }
              size="sm"
              onClick={() => update("quiet_level", opt.value)}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Price Range */}
      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          價格範圍
        </h3>
        <div className="flex flex-wrap gap-2">
          {PRICE_OPTIONS.map((opt) => (
            <Button
              key={opt.value}
              variant={
                filters.price_range === opt.value ? "primary" : "outline"
              }
              size="sm"
              onClick={() => update("price_range", opt.value)}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Time Limit */}
      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          限時
        </h3>
        <div className="flex gap-2">
          {[
            { value: "", label: "不限" },
            { value: "no", label: "不限時" },
            { value: "yes", label: "有限時" },
          ].map((opt) => (
            <Button
              key={opt.value}
              variant={
                filters.limited_time === opt.value ? "primary" : "outline"
              }
              size="sm"
              onClick={() => update("limited_time", opt.value)}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      <Button
        variant="primary"
        size="lg"
        className="w-full"
        onClick={onSearch}
        disabled={loading}
      >
        {loading ? "搜尋中..." : "幫我推薦"}
      </Button>
    </div>
  );
}

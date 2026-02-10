import { Button } from "@/components/ui/Button";
import type { Filters } from "@/types/cafe";

interface FilterPanelProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  onSearch: () => void;
  cities: string[];
  districts: string[];
  mrtStations: string[];
  loading?: boolean;
}

export function FilterPanel({
  filters,
  onChange,
  onSearch,
  cities,
  districts,
  mrtStations,
  loading,
}: FilterPanelProps) {
  const update = (key: keyof Filters, value: string | number | boolean) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          縣市
        </h3>
        <select
          value={filters.city}
          onChange={(e) => update("city", e.target.value)}
          className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
        >
          {cities.map((city) => (
            <option key={city} value={city}>
              {city}
            </option>
          ))}
        </select>
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          行政區
        </h3>
        <select
          value={filters.district}
          onChange={(e) => update("district", e.target.value)}
          className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
        >
          <option value="">全部行政區</option>
          {districts.map((district) => (
            <option key={district} value={district}>
              {district}
            </option>
          ))}
        </select>
      </div>

      {mrtStations.length > 0 ? (
        <div>
          <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
            捷運站
          </h3>
          <select
            value={filters.mrt_station}
            onChange={(e) => update("mrt_station", e.target.value)}
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
      ) : (
        <div className="text-xs text-[var(--muted-foreground)]">
          此縣市無捷運站資料
        </div>
      )}

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-[var(--muted-foreground)]">
          篩選條件
        </h3>
        <div>
          <div className="text-xs text-[var(--muted-foreground)] mb-2">WiFi</div>
          <div className="flex gap-2">
            {[
              { value: false, label: "不限" },
              { value: true, label: "有 WiFi" },
            ].map((opt) => (
              <Button
                key={String(opt.value)}
                variant={filters.wifi === opt.value ? "primary" : "outline"}
                size="sm"
                onClick={() => update("wifi", opt.value)}
              >
                {opt.label}
              </Button>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs text-[var(--muted-foreground)] mb-2">插座</div>
          <div className="flex gap-2">
            {[
              { value: false, label: "不限" },
              { value: true, label: "有插座" },
            ].map((opt) => (
              <Button
                key={String(opt.value)}
                variant={filters.socket === opt.value ? "primary" : "outline"}
                size="sm"
                onClick={() => update("socket", opt.value)}
              >
                {opt.label}
              </Button>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs text-[var(--muted-foreground)] mb-2">
            安靜程度
          </div>
          <select
            value={filters.quiet_level}
            onChange={(e) => update("quiet_level", e.target.value)}
            className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          >
            <option value="">不限</option>
            <option value="quiet">安靜</option>
            <option value="normal">一般</option>
            <option value="loud">偏吵</option>
          </select>
        </div>

        <div>
          <div className="text-xs text-[var(--muted-foreground)] mb-2">
            價格上限 (TWD)
          </div>
          <input
            type="number"
            min={0}
            value={filters.max_price || ""}
            onChange={(e) =>
              update("max_price", e.target.value ? Number(e.target.value) : 0)
            }
            className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            placeholder="例如 200"
          />
        </div>

        <div>
          <div className="text-xs text-[var(--muted-foreground)] mb-2">
            訂位
          </div>
          <div className="flex gap-2">
            {[
              { value: false, label: "不限" },
              { value: true, label: "可訂位" },
            ].map((opt) => (
              <Button
                key={String(opt.value)}
                variant={filters.reservable === opt.value ? "primary" : "outline"}
                size="sm"
                onClick={() => update("reservable", opt.value)}
              >
                {opt.label}
              </Button>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs text-[var(--muted-foreground)] mb-2">
            公車站 / 地標
          </div>
          <input
            type="text"
            value={filters.bus_stop}
            onChange={(e) => update("bus_stop", e.target.value)}
            className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            placeholder="輸入公車站或地標"
          />
        </div>
      </div>

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
              variant={filters.limited_time === opt.value ? "primary" : "outline"}
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

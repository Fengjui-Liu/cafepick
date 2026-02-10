import { Button } from "@/components/ui/Button";
import type { Filters, Area } from "@/types/cafe";
import type { Place } from "@/types/place";

interface FilterPanelProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  onSearch: () => void;
  areas: Area[];
  districts: string[];
  transitPoints: Place[];
  selectedTransitId: string;
  onTransitChange: (id: string) => void;
  transitQuery: string;
  onTransitQueryChange: (value: string) => void;
  onTransitSearch: () => void;
  loading?: boolean;
}

export function FilterPanel({
  filters,
  onChange,
  onSearch,
  areas,
  districts,
  transitPoints,
  selectedTransitId,
  onTransitChange,
  transitQuery,
  onTransitQueryChange,
  onTransitSearch,
  loading,
}: FilterPanelProps) {
  const update = (
    key: keyof Filters,
    value: string | number | boolean | null
  ) => {
    if (key === "city") {
      onChange({
        ...filters,
        city: String(value),
        district: "",
        mrt_station: "",
      });
      return;
    }
    if (key === "district") {
      onChange({ ...filters, district: String(value), mrt_station: "" });
      return;
    }
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
          {areas.map((area) => (
            <option key={area.city} value={area.city}>
              {area.city_name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          行政區（可選）
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

      {transitPoints.length > 0 ? (
        <div>
          <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
            大眾運輸點（可選）
          </h3>
          <select
            value={selectedTransitId}
            onChange={(e) => onTransitChange(e.target.value)}
            className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          >
            <option value="">不指定</option>
            {transitPoints.map((point) => (
              <option key={point.id} value={point.id}>
                {point.name}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          自訂地點（可選）
        </h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={transitQuery}
            onChange={(e) => onTransitQueryChange(e.target.value)}
            className="flex-1 h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            placeholder="輸入政大、板橋車站..."
          />
          <Button
            variant="outline"
            size="sm"
            onClick={onTransitSearch}
          >
            查詢
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-[var(--muted-foreground)]">
          提示
        </h3>
        <p className="text-xs text-[var(--muted-foreground)]">
          Google Places 僅提供基本資訊（名稱、地址、評分、價格等）。
          WiFi、插座、安靜程度、訂位等屬性需另行補充資料。
        </p>
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

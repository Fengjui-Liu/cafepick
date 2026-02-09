import { Slider } from "@/components/ui/Slider";
import { Button } from "@/components/ui/Button";
import type { Filters } from "@/types/cafe";

interface FilterPanelProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  onSearch: () => void;
  mrtStations: string[];
  loading?: boolean;
}

export function FilterPanel({
  filters,
  onChange,
  onSearch,
  mrtStations,
  loading,
}: FilterPanelProps) {
  const update = (key: keyof Filters, value: string | number) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-sm font-semibold mb-2 text-[var(--muted-foreground)]">
          捷運站
        </h3>
        <select
          value={filters.mrt}
          onChange={(e) => update("mrt", e.target.value)}
          className="w-full h-10 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
        >
          <option value="">全部區域</option>
          {mrtStations.map((mrt) => (
            <option key={mrt} value={mrt}>
              {mrt}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-[var(--muted-foreground)]">
          篩選條件
        </h3>
        <Slider
          label="WiFi 穩定度"
          value={filters.wifi}
          onChange={(v) => update("wifi", v)}
        />
        <Slider
          label="插座數量"
          value={filters.socket}
          onChange={(v) => update("socket", v)}
        />
        <Slider
          label="安靜程度"
          value={filters.quiet}
          onChange={(v) => update("quiet", v)}
        />
        <Slider
          label="價格便宜"
          value={filters.cheap}
          onChange={(v) => update("cheap", v)}
        />
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

import { useEffect, useState } from "react";
import { searchStations } from "@/services/api";

interface Station {
  name: string;
  lines: string[];
}

interface OriginPickerProps {
  message?: string;
  onUseLocation: () => void;
  onStation: (name: string) => void;
  onClose: () => void;
}

/** Bottom sheet on phones, centered dialog on desktop. */
export function OriginPicker({ message, onUseLocation, onStation, onClose }: OriginPickerProps) {
  const [query, setQuery] = useState("");
  const [found, setFound] = useState<{ query: string; stations: Station[] }>({
    query: "",
    stations: [],
  });
  const q = query.trim();
  // Only show results that belong to what's typed now.
  const stations = q && found.query === q ? found.stations : [];

  useEffect(() => {
    if (!q) return;
    const timer = setTimeout(() => {
      searchStations(q)
        .then((stations) => setFound({ query: q, stations }))
        .catch(() => setFound({ query: q, stations: [] }));
    }, 150);
    return () => clearTimeout(timer);
  }, [q]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-label="選擇出發地點"
        className="w-full sm:max-w-md max-h-[80vh] overflow-y-auto rounded-t-3xl sm:rounded-3xl bg-[var(--card)] p-5 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold font-display">從哪裡出發？</h2>
          <button
            type="button"
            onClick={onClose}
            className="h-9 w-9 rounded-full hover:bg-[var(--secondary)] cursor-pointer"
            aria-label="關閉"
          >
            ✕
          </button>
        </div>

        {message && (
          <p className="rounded-xl bg-amber-50 border border-amber-200 p-3 text-sm text-amber-900">
            {message}
          </p>
        )}

        <button
          type="button"
          onClick={onUseLocation}
          className="w-full rounded-2xl border border-[var(--border)] px-4 py-3 text-left hover:bg-[var(--secondary)] cursor-pointer"
        >
          📍 使用我的位置
        </button>

        <div>
          <label className="text-sm text-[var(--muted-foreground)]" htmlFor="station-search">
            或選一個捷運站
          </label>
          <input
            id="station-search"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="輸入站名，例如 忠孝、公館、板橋"
            className="mt-1 w-full h-12 rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 text-base focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          />
        </div>

        <ul className="divide-y divide-[var(--border)]">
          {stations.map((s) => (
            <li key={s.name}>
              <button
                type="button"
                onClick={() => onStation(s.name)}
                className="w-full py-3 text-left cursor-pointer hover:bg-[var(--secondary)] px-2 rounded-lg"
              >
                <span className="font-medium">🚇 {s.name}</span>
                <span className="ml-2 text-xs text-[var(--muted-foreground)]">
                  {s.lines.join("・")}
                </span>
              </button>
            </li>
          ))}
          {q && found.query === q && stations.length === 0 && (
            <li className="py-3 text-sm text-[var(--muted-foreground)]">找不到這個站</li>
          )}
        </ul>
      </div>
    </div>
  );
}

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { GoogleMap, type MapPin } from "@/components/GoogleMap";
import { ModePicker } from "@/components/ModePicker";
import { OriginPicker } from "@/components/OriginPicker";
import { ResultCard } from "@/components/ResultCard";
import { getCurrentPosition } from "@/lib/location";
import { recommend } from "@/services/api";
import type { Mode, Recommendation, RecommendResponse } from "@/types/place";

type Origin = { kind: "gps"; lat: number; lng: number } | { kind: "station"; name: string };

function App() {
  const [mode, setMode] = useState<Mode | null>(null);
  const [pet, setPet] = useState(false);
  const [origin, setOrigin] = useState<Origin | null>(null);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [pickerMessage, setPickerMessage] = useState("");

  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [shownIds, setShownIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const requestId = useRef(0);
  const cardRefs = useRef<Map<string, HTMLElement>>(new Map());

  const fetchResults = useCallback(
    async (exclude: string[]) => {
      if (!mode || !origin) return;
      const id = ++requestId.current;
      setLoading(true);
      setError("");
      try {
        const data = await recommend({
          mode,
          origin: origin.kind === "gps" ? { lat: origin.lat, lng: origin.lng } : { station: origin.name },
          pet,
          exclude,
        });
        if (id !== requestId.current) return; // a newer search started meanwhile
        setResult(data);
        setShownIds([...exclude, ...data.recommendations.map((r) => r.cafe.id)]);
        setSelectedId(null);
      } catch (err) {
        if (id !== requestId.current) return;
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (id === requestId.current) setLoading(false);
      }
    },
    [mode, origin, pet]
  );

  // New scenario, place or pet setting → fresh top 3.
  useEffect(() => {
    fetchResults([]);
  }, [fetchResults]);

  const locate = async () => {
    setLocating(true);
    try {
      const pos = await getCurrentPosition();
      setOrigin({ kind: "gps", ...pos });
      setPickerOpen(false);
    } catch (err) {
      setPickerMessage(err instanceof Error ? err.message : "定位失敗，請改選捷運站");
      setPickerOpen(true);
    } finally {
      setLocating(false);
    }
  };

  const chooseMode = (next: Mode) => {
    setMode(next);
    if (!origin && !locating) locate();
  };

  const openPicker = () => {
    setPickerMessage("");
    setPickerOpen(true);
  };

  const recs: Recommendation[] = useMemo(() => result?.recommendations ?? [], [result]);

  const pins: MapPin[] = useMemo(
    () =>
      recs.map((r) => ({
        id: r.cafe.id,
        name: r.cafe.name,
        latitude: r.cafe.latitude,
        longitude: r.cafe.longitude,
      })),
    [recs]
  );

  const mapOrigin = useMemo(() => {
    if (origin?.kind === "gps") return { lat: origin.lat, lng: origin.lng };
    const o = result?.origin;
    return o?.latitude != null && o?.longitude != null ? { lat: o.latitude, lng: o.longitude } : null;
  }, [origin, result]);

  const selectPin = useCallback((id: string) => {
    setSelectedId(id);
    cardRefs.current.get(id)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, []);

  const originLabel =
    origin?.kind === "station" ? `🚇 ${origin.name}站` : origin?.kind === "gps" ? "📍 目前位置" : "📍 選擇地點";

  const picker = pickerOpen && (
    <OriginPicker
      message={pickerMessage}
      onUseLocation={locate}
      onStation={(name) => {
        setOrigin({ kind: "station", name });
        setPickerOpen(false);
      }}
      onClose={() => setPickerOpen(false)}
    />
  );

  // ── Home: pick a scenario ────────────────────────────────────────────────
  if (!mode || !origin) {
    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col px-4 pt-10 pb-8">
        <h1 className="font-display text-4xl font-semibold">CaféPick</h1>
        <p className="mt-2 text-[var(--muted-foreground)]">現在要去咖啡廳做什麼？</p>

        <div className="mt-8">
          <ModePicker mode={mode} pet={pet} onMode={chooseMode} onPet={setPet} disabled={locating} />
        </div>

        <div className="mt-6 text-sm text-[var(--muted-foreground)]">
          {locating ? (
            "📍 定位中…"
          ) : (
            <>
              會從{origin ? <b> {originLabel} </b> : "你的目前位置"}找附近的店 ·{" "}
              <button type="button" onClick={openPicker} className="underline cursor-pointer">
                改選捷運站
              </button>
            </>
          )}
        </div>
        {picker}
      </div>
    );
  }

  // ── Results: map + 3 cards ───────────────────────────────────────────────
  return (
    <div className="flex min-h-screen flex-col md:h-screen">
      <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[var(--background)]/95 backdrop-blur px-4 py-3 space-y-2 md:flex md:items-center md:gap-6 md:space-y-0">
        <div className="flex items-center justify-between gap-3 md:contents">
          <button
            type="button"
            onClick={() => {
              setMode(null);
              setResult(null);
            }}
            className="font-display text-xl font-semibold cursor-pointer"
          >
            CaféPick
          </button>
          <button
            type="button"
            onClick={openPicker}
            className="md:order-3 md:ml-auto truncate rounded-full border border-[var(--border)] bg-[var(--card)] px-3 py-1.5 text-sm cursor-pointer"
          >
            {originLabel} ▾
          </button>
        </div>
        <div className="md:order-2">
          <ModePicker mode={mode} pet={pet} onMode={setMode} onPet={setPet} compact />
        </div>
      </header>

      <div className="flex flex-1 flex-col md:flex-row md:overflow-hidden">
        <div className="h-[38vh] md:order-2 md:h-auto md:flex-1">
          <GoogleMap pins={pins} origin={mapOrigin} highlightedId={selectedId} onPinClick={selectPin} />
        </div>

        <section className="flex-1 space-y-3 p-4 md:order-1 md:w-[420px] md:flex-none md:overflow-y-auto">
          {error && (
            <p className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800 break-all">
              {error}
            </p>
          )}

          {loading && recs.length === 0 && (
            <p className="py-8 text-center text-[var(--muted-foreground)]">幫你挑選中…</p>
          )}

          {!loading && !error && result && recs.length === 0 && (
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 text-sm">
              <p className="font-medium">附近沒有符合的店</p>
              <p className="mt-1 text-[var(--muted-foreground)]">
                {pet ? "可以試試關掉「帶毛孩」，或" : "可以"}
                <button type="button" onClick={openPicker} className="underline cursor-pointer">
                  換個地點
                </button>
                。
              </p>
            </div>
          )}

          <div className={`space-y-3 ${loading ? "opacity-50" : ""}`}>
            {recs.map((rec, i) => (
              <div
                key={rec.cafe.id}
                ref={(el) => {
                  if (el) cardRefs.current.set(rec.cafe.id, el);
                  else cardRefs.current.delete(rec.cafe.id);
                }}
              >
                <ResultCard
                  rec={rec}
                  rank={i + 1}
                  pet={pet}
                  highlighted={selectedId === rec.cafe.id}
                  onSelect={() => setSelectedId(rec.cafe.id)}
                />
              </div>
            ))}
          </div>

          {recs.length > 0 && (
            <button
              type="button"
              disabled={loading || !result?.has_more}
              onClick={() => fetchResults(shownIds)}
              className="h-12 w-full rounded-2xl border border-[var(--border)] bg-[var(--card)] font-medium cursor-pointer disabled:opacity-50 disabled:cursor-default"
            >
              {loading ? "挑選中…" : result?.has_more ? "都不喜歡？換 3 間" : "附近沒有更多了"}
            </button>
          )}
        </section>
      </div>
      {picker}
    </div>
  );
}

export default App;

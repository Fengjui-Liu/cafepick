import { useState } from "react";
import { directionsUrl } from "@/lib/location";
import type { Recommendation, WorkInfo } from "@/types/place";

interface ResultCardProps {
  rec: Recommendation;
  rank: number;
  pet: boolean;
  highlighted: boolean;
  onSelect: () => void;
}

const WORK_ROWS: { key: keyof WorkInfo; label: string }[] = [
  { key: "socket", label: "插座" },
  { key: "wifi", label: "WiFi" },
  { key: "quiet", label: "安靜" },
  { key: "seat", label: "座位" },
  { key: "tasty", label: "好喝" },
];

const LIMITED_TIME = { no: "不限時", maybe: "看情況", yes: "有限時" } as const;

function Dots({ value }: { value: number | null }) {
  if (value == null) return <span className="text-[var(--muted-foreground)]">未知</span>;
  const filled = Math.round(value);
  return (
    <span aria-label={`${value} / 5`} className="tracking-tight">
      {"●".repeat(filled)}
      <span className="opacity-25">{"●".repeat(5 - filled)}</span>
    </span>
  );
}

export function ResultCard({ rec, rank, pet, highlighted, onSelect }: ResultCardProps) {
  const [open, setOpen] = useState(false);
  const { cafe } = rec;
  const isGoogle = !cafe.id.startsWith("nomad:");
  const work = cafe.work;

  return (
    <article
      onClick={onSelect}
      className={`rounded-2xl border bg-[var(--card)] p-4 transition-shadow cursor-pointer ${
        highlighted ? "border-[var(--primary)] ring-2 ring-[var(--primary)]" : "border-[var(--border)]"
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[var(--primary)] text-sm font-bold text-[var(--primary-foreground)]">
          {rank}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold leading-snug">{cafe.name}</h3>
            <span
              className="shrink-0 rounded-full bg-[var(--secondary)] px-2 py-0.5 text-xs font-semibold"
              title="適合度（0–100）"
            >
              {rec.score}
            </span>
          </div>

          <p className="mt-1 text-sm">{rec.reasons.join("・")}</p>

          <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-[var(--muted-foreground)]">
            {cafe.rating != null && (
              <span>
                ★ {cafe.rating.toFixed(1)}
                {cafe.user_ratings_total ? ` (${cafe.user_ratings_total})` : ""}
              </span>
            )}
            {cafe.open_now === true && <span className="text-green-700">營業中</span>}
            {cafe.nearest_mrt && (
              <span>
                🚇 {cafe.nearest_mrt.name} {cafe.nearest_mrt.walk_minutes} 分
              </span>
            )}
            {pet && rec.pet_status === "yes" && <span className="text-amber-800">🐶 可帶寵物</span>}
            {pet && rec.pet_status === "unknown" && <span>🐶 未確認</span>}
          </div>

          {open && (
            <div className="mt-3 space-y-3 border-t border-[var(--border)] pt-3 text-sm">
              {cafe.address && <p className="text-[var(--muted-foreground)]">{cafe.address}</p>}

              {work ? (
                <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                  {WORK_ROWS.map((row) => (
                    <div key={row.key} className="flex justify-between">
                      <span>{row.label}</span>
                      <Dots value={work[row.key] as number | null} />
                    </div>
                  ))}
                  <div className="flex justify-between">
                    <span>限時</span>
                    <span>{work.limited_time ? LIMITED_TIME[work.limited_time] : "未知"}</span>
                  </div>
                </div>
              ) : (
                <p className="text-[var(--muted-foreground)]">
                  這間店不在 Cafe Nomad 上，WiFi、插座等工作條件未知。
                </p>
              )}

              {cafe.opening_hours && cafe.opening_hours.length > 0 && (
                <details>
                  <summary className="cursor-pointer">營業時間</summary>
                  <ul className="mt-1 text-[var(--muted-foreground)]">
                    {cafe.opening_hours.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                </details>
              )}

              {!isGoogle && (
                <p className="text-xs text-[var(--muted-foreground)]">
                  資料來自 Cafe Nomad 網友回報，出發前建議先確認有營業。
                </p>
              )}
            </div>
          )}

          <div className="mt-3 flex gap-2" onClick={(e) => e.stopPropagation()}>
            <a
              href={directionsUrl(cafe.latitude, cafe.longitude, isGoogle ? cafe.id : undefined)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-10 flex-1 items-center justify-center rounded-xl bg-[var(--primary)] text-sm font-medium text-[var(--primary-foreground)]"
            >
              導航
            </a>
            <button
              type="button"
              onClick={() => setOpen(!open)}
              aria-expanded={open}
              className="h-10 flex-1 rounded-xl border border-[var(--border)] text-sm cursor-pointer hover:bg-[var(--secondary)]"
            >
              {open ? "收起" : "詳細"}
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}

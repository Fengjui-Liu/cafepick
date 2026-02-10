import type { Cafe } from "@/types/cafe";

interface CafeDetailProps {
  cafe: Cafe;
  onClose: () => void;
  isFavorite: boolean;
  onToggleFavorite: (id: string) => void;
}

function getQuietLabel(score: number): string {
  if (score >= 3.5) return "安靜";
  if (score >= 2) return "普通";
  return "熱鬧";
}

function getPriceLabel(cheapScore: number): string {
  if (cheapScore >= 4) return "平價 (< $100)";
  if (cheapScore >= 2.5) return "中等 ($100-200)";
  return "較貴 (> $200)";
}

function getWalkingTime(km: number): string {
  const minutes = Math.round((km / 5) * 60);
  if (minutes <= 1) return "約 1 分鐘";
  return `約 ${minutes} 分鐘`;
}

function RatingRow({ label, value, max = 5 }: { label: string; value: number; max?: number }) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-16 text-sm text-[var(--muted-foreground)]">{label}</span>
      <div className="flex-1 h-2 rounded-full bg-[var(--muted)]">
        <div
          className="h-full rounded-full bg-[var(--primary)] transition-all"
          style={{ width: `${(value / max) * 100}%` }}
        />
      </div>
      <span className="w-8 text-sm text-right text-[var(--muted-foreground)]">{value}</span>
    </div>
  );
}

export function CafeDetail({ cafe, onClose, isFavorite, onToggleFavorite }: CafeDetailProps) {
  const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${cafe.latitude},${cafe.longitude}`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-[var(--card)] rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-[var(--card)] border-b border-[var(--border)] p-4 flex items-center justify-between rounded-t-2xl">
          <h2 className="text-lg font-bold">{cafe.name}</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onToggleFavorite(cafe.id)}
              className="p-2 rounded-full hover:bg-[var(--muted)] transition-colors"
              title={isFavorite ? "取消收藏" : "加入收藏"}
            >
              {isFavorite ? (
                <svg className="w-5 h-5 text-red-500 fill-current" viewBox="0 0 20 20"><path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" /></svg>
              ) : (
                <svg className="w-5 h-5 text-[var(--muted-foreground)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
              )}
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-[var(--muted)] transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        </div>

        <div className="p-5 space-y-5">
          {/* Location info */}
          <div className="space-y-2">
            <p className="text-sm text-[var(--muted-foreground)]">{cafe.address}</p>
            <div className="flex flex-wrap gap-2 text-sm">
              {cafe.district && (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-[var(--secondary)] text-[var(--secondary-foreground)]">
                  {cafe.district}
                </span>
              )}
              {cafe.mrt && (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-[var(--secondary)] text-[var(--secondary-foreground)]">
                  {cafe.mrt}站
                </span>
              )}
            </div>
          </div>

          {/* Feature tags */}
          <div className="flex flex-wrap gap-2">
            <span className={`text-xs px-2.5 py-1 rounded-full ${cafe.wifi >= 3 ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-500"}`}>
              WiFi {cafe.wifi >= 3 ? "有" : "無"}
            </span>
            <span className={`text-xs px-2.5 py-1 rounded-full ${cafe.socket >= 3 ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-500"}`}>
              插座 {cafe.socket >= 3 ? "有" : "無"}
            </span>
            <span className="text-xs px-2.5 py-1 rounded-full bg-blue-100 text-blue-800">
              {getQuietLabel(cafe.quiet)}
            </span>
            <span className="text-xs px-2.5 py-1 rounded-full bg-amber-100 text-amber-800">
              {getPriceLabel(cafe.cheap)}
            </span>
            {cafe.limited_time === "no" && (
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800">不限時</span>
            )}
            {cafe.has_reservation === "yes" && (
              <span className="text-xs px-2.5 py-1 rounded-full bg-purple-100 text-purple-800">可訂位</span>
            )}
            {cafe.standing_desk === "yes" && (
              <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-800">站立桌</span>
            )}
          </div>

          {/* Detailed ratings */}
          <div>
            <h3 className="text-sm font-semibold mb-3 text-[var(--muted-foreground)]">詳細評分</h3>
            <div className="space-y-2.5">
              <RatingRow label="WiFi" value={cafe.wifi} />
              <RatingRow label="插座" value={cafe.socket} />
              <RatingRow label="安靜" value={cafe.quiet} />
              <RatingRow label="美味" value={cafe.tasty} />
              <RatingRow label="音樂" value={cafe.music} />
              <RatingRow label="座位" value={cafe.seat} />
            </div>
          </div>

          {/* Opening hours */}
          {cafe.open_time && (
            <div>
              <h3 className="text-sm font-semibold mb-1 text-[var(--muted-foreground)]">營業時間</h3>
              <p className="text-sm">{cafe.open_time}</p>
            </div>
          )}

          {/* Walking time estimate (rough: based on MRT station typical distance) */}
          {cafe.mrt && (
            <div>
              <h3 className="text-sm font-semibold mb-1 text-[var(--muted-foreground)]">步行距離</h3>
              <p className="text-sm">
                從 {cafe.mrt}站 {getWalkingTime(0.4)}（估計）
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <a
              href={googleMapsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 inline-flex items-center justify-center gap-2 h-10 rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)] text-sm font-medium hover:opacity-90 transition-opacity"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              Google Maps 導航
            </a>
            {cafe.url && (
              <a
                href={cafe.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 h-10 px-4 rounded-lg border border-[var(--border)] text-sm font-medium hover:bg-[var(--accent)] transition-colors"
              >
                官網
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

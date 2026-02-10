import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { CafeRecommendation } from "@/types/cafe";

interface CafeCardProps {
  recommendation: CafeRecommendation;
  rank: number;
  isHighlighted: boolean;
  onHover: (id: string | null) => void;
  onClick: () => void;
  isFavorite: boolean;
  onToggleFavorite: (id: string) => void;
}

function getQuietLabel(score: number): string {
  if (score >= 3.5) return "安靜";
  if (score >= 2) return "普通";
  return "熱鬧";
}

function getPriceLabel(cheapScore: number): string {
  if (cheapScore >= 4) return "平價";
  if (cheapScore >= 2.5) return "中等";
  return "較貴";
}

export function CafeCard({
  recommendation,
  rank,
  isHighlighted,
  onHover,
  onClick,
  isFavorite,
  onToggleFavorite,
}: CafeCardProps) {
  const { cafe, score, distance_km } = recommendation;
  const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${cafe.latitude},${cafe.longitude}`;

  return (
    <Card
      className={`transition-all cursor-pointer ${
        isHighlighted
          ? "ring-2 ring-[var(--primary)] shadow-md"
          : "hover:shadow-md"
      }`}
    >
      <div
        onMouseEnter={() => onHover(cafe.id)}
        onMouseLeave={() => onHover(null)}
      >
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2 min-w-0 flex-1" onClick={onClick}>
              <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-[var(--primary)] text-[var(--primary-foreground)] text-xs font-bold">
                {rank}
              </span>
              <h3 className="font-semibold text-base truncate">{cafe.name}</h3>
            </div>
            <div className="flex items-center gap-1 flex-shrink-0 ml-2">
              <button
                onClick={(e) => { e.stopPropagation(); onToggleFavorite(cafe.id); }}
                className="p-1 rounded-full hover:bg-[var(--muted)] transition-colors"
                title={isFavorite ? "取消收藏" : "加入收藏"}
              >
                {isFavorite ? (
                  <svg className="w-4 h-4 text-red-500 fill-current" viewBox="0 0 20 20"><path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" /></svg>
                ) : (
                  <svg className="w-4 h-4 text-[var(--muted-foreground)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                )}
              </button>
              <Badge variant="success">{score}%</Badge>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2" onClick={onClick}>
            {cafe.mrt && <Badge>{cafe.mrt}</Badge>}
            {cafe.district && <Badge>{cafe.district}</Badge>}
            {cafe.limited_time === "no" && (
              <Badge variant="success">不限時</Badge>
            )}
            {distance_km !== null && <Badge>{distance_km} km</Badge>}
          </div>
        </CardHeader>
        <CardContent>
          <div onClick={onClick}>
            <p className="text-xs text-[var(--muted-foreground)] mb-3">
              {cafe.address}
            </p>

            <div className="flex flex-wrap gap-2 mb-3">
              <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${cafe.wifi >= 3 ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-500"}`}>
                WiFi {cafe.wifi >= 3 ? "有" : "無"}
              </span>
              <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${cafe.socket >= 3 ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-500"}`}>
                插座 {cafe.socket >= 3 ? "有" : "無"}
              </span>
              <span className="inline-flex items-center text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                {getQuietLabel(cafe.quiet)}
              </span>
              <span className="inline-flex items-center text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-800">
                {getPriceLabel(cafe.cheap)}
              </span>
              {cafe.has_reservation === "yes" && (
                <span className="inline-flex items-center text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800">
                  可訂位
                </span>
              )}
            </div>

            {cafe.open_time && (
              <p className="text-xs text-[var(--muted-foreground)] mb-2">
                {cafe.open_time}
              </p>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex gap-2 mt-2 pt-2 border-t border-[var(--border)]">
            <a
              href={googleMapsUrl}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="inline-flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)] hover:opacity-80 transition-opacity"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              導航
            </a>
            <button
              onClick={onClick}
              className="inline-flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)] hover:opacity-80 transition-opacity"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              詳情
            </button>
          </div>
        </CardContent>
      </div>
    </Card>
  );
}

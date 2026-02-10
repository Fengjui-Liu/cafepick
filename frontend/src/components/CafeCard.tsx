import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { CafeRecommendation } from "@/types/cafe";

interface CafeCardProps {
  recommendation: CafeRecommendation;
  rank: number;
  isHighlighted: boolean;
  onHover: (id: string | null) => void;
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
}: CafeCardProps) {
  const { cafe, score, distance_km } = recommendation;

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
            <div className="flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[var(--primary)] text-[var(--primary-foreground)] text-xs font-bold">
                {rank}
              </span>
              <h3 className="font-semibold text-base">{cafe.name}</h3>
            </div>
            <Badge variant="success">{score}%</Badge>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {cafe.mrt && <Badge>{cafe.mrt}</Badge>}
            {cafe.district && <Badge>{cafe.district}</Badge>}
            {cafe.limited_time === "no" && (
              <Badge variant="success">不限時</Badge>
            )}
            {distance_km !== null && <Badge>{distance_km} km</Badge>}
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-[var(--muted-foreground)] mb-3">
            {cafe.address}
          </p>

          {/* Feature tags */}
          <div className="flex flex-wrap gap-2 mb-3">
            <span
              className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
                cafe.wifi >= 3
                  ? "bg-green-100 text-green-800"
                  : "bg-gray-100 text-gray-500"
              }`}
            >
              WiFi {cafe.wifi >= 3 ? "有" : "無"}
            </span>
            <span
              className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
                cafe.socket >= 3
                  ? "bg-green-100 text-green-800"
                  : "bg-gray-100 text-gray-500"
              }`}
            >
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
            <p className="text-xs text-[var(--muted-foreground)]">
              {cafe.open_time}
            </p>
          )}
        </CardContent>
      </div>
    </Card>
  );
}

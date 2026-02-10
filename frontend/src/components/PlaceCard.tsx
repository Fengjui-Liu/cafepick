import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { PlaceRecommendation } from "@/types/place";

interface PlaceCardProps {
  recommendation: PlaceRecommendation;
  rank: number;
  isHighlighted: boolean;
  onHover: (id: string | null) => void;
}

function formatPriceLevel(level?: string): string | null {
  if (!level) return null;
  const map: Record<string, string> = {
    PRICE_LEVEL_INEXPENSIVE: "平價",
    PRICE_LEVEL_MODERATE: "中等",
    PRICE_LEVEL_EXPENSIVE: "偏高",
    PRICE_LEVEL_VERY_EXPENSIVE: "高價",
  };
  return map[level] || level;
}

export function PlaceCard({
  recommendation,
  rank,
  isHighlighted,
  onHover,
}: PlaceCardProps) {
  const { cafe } = recommendation;
  const priceLabel = formatPriceLevel(cafe.price_level);

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
            {cafe.rating ? (
              <Badge variant="success">{cafe.rating.toFixed(1)}</Badge>
            ) : null}
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {cafe.district ? <Badge>{cafe.district}</Badge> : null}
            {priceLabel ? <Badge>{priceLabel}</Badge> : null}
            {cafe.transit_name && cafe.transit_walk_minutes !== undefined ? (
              cafe.transit_walk_minutes <= 10 ? (
                <Badge>{`${cafe.transit_name} · 步行約 ${cafe.transit_walk_minutes} 分`}</Badge>
              ) : null
            ) : cafe.mrt_station && cafe.mrt_walk_minutes !== undefined ? (
              cafe.mrt_walk_minutes <= 10 ? (
                <Badge>{`${cafe.mrt_station} · 步行約 ${cafe.mrt_walk_minutes} 分`}</Badge>
              ) : null
            ) : null}
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-[var(--muted-foreground)] mb-3">
            {cafe.address}
          </p>
          {cafe.user_ratings_total ? (
            <p className="text-xs text-[var(--muted-foreground)]">
              {cafe.user_ratings_total} 則評論
            </p>
          ) : null}
        </CardContent>
      </div>
    </Card>
  );
}

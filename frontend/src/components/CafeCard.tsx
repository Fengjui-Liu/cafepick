import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { CafeRecommendation } from "@/types/cafe";

interface CafeCardProps {
  recommendation: CafeRecommendation;
  rank: number;
  isHighlighted: boolean;
  onHover: (id: string | null) => void;
}

function RatingBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-12 text-[var(--muted-foreground)]">{label}</span>
      <div className="flex-1 h-1.5 rounded-full bg-[var(--muted)]">
        <div
          className="h-full rounded-full bg-[var(--primary)] transition-all"
          style={{ width: `${(value / 5) * 100}%` }}
        />
      </div>
      <span className="w-6 text-right text-[var(--muted-foreground)]">
        {value}
      </span>
    </div>
  );
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
            <Badge variant="success">{score} 分</Badge>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {cafe.mrt && <Badge>{cafe.mrt}</Badge>}
            {cafe.limited_time === "no" && (
              <Badge variant="success">不限時</Badge>
            )}
            {cafe.standing_desk === "yes" && <Badge>站立桌</Badge>}
            {distance_km !== null && <Badge>{distance_km} km</Badge>}
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-[var(--muted-foreground)] mb-3">
            {cafe.address}
          </p>
          <div className="space-y-1.5">
            <RatingBar label="WiFi" value={cafe.wifi} />
            <RatingBar label="插座" value={cafe.socket} />
            <RatingBar label="安靜" value={cafe.quiet} />
            <RatingBar label="CP值" value={cafe.cheap} />
          </div>
          {cafe.open_time && (
            <p className="text-xs text-[var(--muted-foreground)] mt-3">
              {cafe.open_time}
            </p>
          )}
        </CardContent>
      </div>
    </Card>
  );
}

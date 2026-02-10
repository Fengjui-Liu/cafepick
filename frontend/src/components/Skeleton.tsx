export function CafeCardSkeleton() {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 animate-pulse">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-6 h-6 rounded-full bg-[var(--muted)]" />
        <div className="h-5 w-36 rounded bg-[var(--muted)]" />
        <div className="ml-auto h-5 w-12 rounded-full bg-[var(--muted)]" />
      </div>
      <div className="flex gap-1.5 mb-3">
        <div className="h-5 w-16 rounded-full bg-[var(--muted)]" />
        <div className="h-5 w-12 rounded-full bg-[var(--muted)]" />
      </div>
      <div className="h-3 w-48 rounded bg-[var(--muted)] mb-3" />
      <div className="flex flex-wrap gap-2">
        <div className="h-6 w-16 rounded-full bg-[var(--muted)]" />
        <div className="h-6 w-16 rounded-full bg-[var(--muted)]" />
        <div className="h-6 w-12 rounded-full bg-[var(--muted)]" />
        <div className="h-6 w-12 rounded-full bg-[var(--muted)]" />
      </div>
    </div>
  );
}

export function ResultsSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <CafeCardSkeleton key={i} />
      ))}
    </div>
  );
}

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export function Card({ className = "", children }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-[var(--border)] bg-[var(--card)] text-[var(--card-foreground)] shadow-sm ${className}`}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className = "", children }: CardProps) {
  return <div className={`p-4 pb-2 ${className}`}>{children}</div>;
}

export function CardContent({ className = "", children }: CardProps) {
  return <div className={`p-4 pt-2 ${className}`}>{children}</div>;
}

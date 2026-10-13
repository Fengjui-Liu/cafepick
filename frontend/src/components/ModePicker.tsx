import type { Mode } from "@/types/place";

const MODES: { value: Mode; icon: string; label: string; hint: string }[] = [
  { value: "work", icon: "💻", label: "工作", hint: "插座、WiFi、不限時、安靜" },
  { value: "date", icon: "💬", label: "約會", hint: "評價好、氣氛佳、可訂位" },
  { value: "quick", icon: "☕", label: "喝一杯", hint: "最近、現在有開" },
];

interface ModePickerProps {
  mode: Mode | null;
  pet: boolean;
  onMode: (mode: Mode) => void;
  onPet: (pet: boolean) => void;
  /** Big stacked cards on the home screen, a compact bar on the results screen. */
  compact?: boolean;
  disabled?: boolean;
}

export function ModePicker({ mode, pet, onMode, onPet, compact, disabled }: ModePickerProps) {
  return (
    <div className={compact ? "space-y-2 md:flex md:items-center md:gap-3 md:space-y-0" : "space-y-3"}>
      <div className={compact ? "grid grid-cols-3 gap-2 md:inline-grid md:w-[360px]" : "grid gap-3"}>
        {MODES.map((m) => {
          const active = m.value === mode;
          return (
            <button
              key={m.value}
              type="button"
              disabled={disabled}
              onClick={() => onMode(m.value)}
              aria-pressed={active}
              className={`rounded-2xl border text-left transition-colors cursor-pointer disabled:opacity-60 ${
                active
                  ? "border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]"
                  : "border-[var(--border)] bg-[var(--card)] hover:bg-[var(--secondary)]"
              } ${compact ? "px-2 py-2 text-center" : "px-5 py-4 panel-shadow"}`}
            >
              <span className={compact ? "text-sm font-semibold" : "text-lg font-semibold"}>
                {m.icon} {m.label}
              </span>
              {!compact && (
                <span className="block text-sm opacity-75 mt-1">{m.hint}</span>
              )}
            </button>
          );
        })}
      </div>
      <button
        type="button"
        onClick={() => onPet(!pet)}
        aria-pressed={pet}
        className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm cursor-pointer transition-colors ${
          pet
            ? "border-amber-600 bg-amber-100 text-amber-900"
            : "border-[var(--border)] bg-[var(--card)] text-[var(--muted-foreground)]"
        }`}
      >
        🐶 帶毛孩{pet ? "：開" : ""}
      </button>
    </div>
  );
}

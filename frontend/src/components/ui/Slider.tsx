interface SliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
}

export function Slider({
  label,
  value,
  onChange,
  min = 0,
  max = 5,
  step = 0.5,
}: SliderProps) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-[var(--foreground)]">{label}</span>
        <span className="text-[var(--muted-foreground)]">
          {value > 0 ? `${value}+` : "不限"}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 rounded-lg appearance-none cursor-pointer bg-[var(--muted)] accent-[var(--primary)]"
      />
    </div>
  );
}

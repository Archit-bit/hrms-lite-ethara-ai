interface SummaryCardProps {
  label: string;
  value: string | number;
  hint: string;
}

export function SummaryCard({ label, value, hint }: SummaryCardProps) {
  return (
    <article className="summary-card">
      <p className="summary-card__label">{label}</p>
      <strong className="summary-card__value">{value}</strong>
      <span className="summary-card__hint">{hint}</span>
    </article>
  );
}

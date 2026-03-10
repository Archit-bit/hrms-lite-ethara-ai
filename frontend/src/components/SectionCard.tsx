import { PropsWithChildren, ReactNode } from "react";

interface SectionCardProps extends PropsWithChildren {
  title: string;
  description: string;
  action?: ReactNode;
}

export function SectionCard({ title, description, action, children }: SectionCardProps) {
  return (
    <section className="section-card">
      <header className="section-card__header">
        <div>
          <p className="section-card__eyebrow">{title}</p>
          <h2>{description}</h2>
        </div>
        {action ? <div className="section-card__action">{action}</div> : null}
      </header>
      {children}
    </section>
  );
}

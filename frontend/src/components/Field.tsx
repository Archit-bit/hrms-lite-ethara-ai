import { PropsWithChildren } from "react";

interface FieldProps extends PropsWithChildren {
  label: string;
  htmlFor: string;
  hint?: string;
}

export function Field({ label, htmlFor, hint, children }: FieldProps) {
  return (
    <label className="field" htmlFor={htmlFor}>
      <span className="field__label">{label}</span>
      {children}
      {hint ? <span className="field__hint">{hint}</span> : null}
    </label>
  );
}

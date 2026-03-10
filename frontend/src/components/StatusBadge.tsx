import type { AttendanceStatus } from "../types";

interface StatusBadgeProps {
  status: AttendanceStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`status-badge status-badge--${status.toLowerCase()}`}>{status}</span>;
}

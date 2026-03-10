import type {
  ApiMessage,
  AttendanceRecord,
  AttendanceStatus,
  DashboardSummary,
  Employee,
} from "./types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

type QueryParams = Record<string, string | undefined>;

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function buildUrl(path: string, params?: QueryParams): string {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value) {
        url.searchParams.set(key, value);
      }
    });
  }
  return url.toString();
}

async function request<T>(path: string, init?: RequestInit, params?: QueryParams): Promise<T> {
  const response = await fetch(buildUrl(path, params), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const message =
      payload?.message ??
      payload?.detail ??
      (Array.isArray(payload?.errors) ? payload.errors.join(", ") : undefined) ??
      "Request failed.";
    throw new ApiError(message, response.status);
  }

  return payload as T;
}

export const api = {
  getEmployees: () => request<Employee[]>("/api/employees"),
  createEmployee: (payload: {
    employee_id: string;
    full_name: string;
    email_address: string;
    department: string;
  }) =>
    request<Employee>("/api/employees", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteEmployee: (employeeId: string) =>
    request<ApiMessage>(`/api/employees/${encodeURIComponent(employeeId)}`, {
      method: "DELETE",
    }),
  getAttendance: (filters?: { employeeId?: string; date?: string; status?: AttendanceStatus }) =>
    request<AttendanceRecord[]>(
      "/api/attendance",
      undefined,
      {
        employee_id: filters?.employeeId,
        date: filters?.date,
        status: filters?.status,
      },
    ),
  createAttendance: (payload: { employee_id: string; date: string; status: AttendanceStatus }) =>
    request<AttendanceRecord>("/api/attendance", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getDashboard: () => request<DashboardSummary>("/api/dashboard"),
};

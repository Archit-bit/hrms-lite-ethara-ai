export type AttendanceStatus = "PRESENT" | "ABSENT";

export interface Employee {
  employee_id: string;
  full_name: string;
  email_address: string;
  department: string;
  created_at: string;
  total_present_days: number;
}

export interface AttendanceRecord {
  id: number;
  employee_id: string;
  employee_name: string;
  department: string;
  date: string;
  status: AttendanceStatus;
  created_at: string;
}

export interface DashboardSummary {
  total_employees: number;
  total_attendance_records: number;
  present_today: number;
  absent_today: number;
}

export interface ApiMessage {
  message: string;
}

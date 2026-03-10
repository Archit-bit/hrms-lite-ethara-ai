import { FormEvent, useEffect, useMemo, useState } from "react";

import { ApiError, api } from "./api";
import { EmptyState } from "./components/EmptyState";
import { Field } from "./components/Field";
import { SectionCard } from "./components/SectionCard";
import { StatusBadge } from "./components/StatusBadge";
import { SummaryCard } from "./components/SummaryCard";
import type { AttendanceRecord, AttendanceStatus, DashboardSummary, Employee } from "./types";

function toLocalDateInputValue(referenceDate = new Date()) {
  const offsetInMilliseconds = referenceDate.getTimezoneOffset() * 60_000;
  return new Date(referenceDate.getTime() - offsetInMilliseconds).toISOString().slice(0, 10);
}

function toCalendarDate(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

const today = toLocalDateInputValue();

const initialEmployeeForm = {
  employee_id: "",
  full_name: "",
  email_address: "",
  department: "",
};

const initialAttendanceForm: {
  employee_id: string;
  date: string;
  status: AttendanceStatus;
} = {
  employee_id: "",
  date: today,
  status: "PRESENT",
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(toCalendarDate(value));
}

function formatRelativeTimestamp(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function App() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [filters, setFilters] = useState({ employeeId: "", date: "" });
  const [employeeForm, setEmployeeForm] = useState(initialEmployeeForm);
  const [attendanceForm, setAttendanceForm] = useState(initialAttendanceForm);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ kind: "success" | "error"; message: string } | null>(null);
  const [isCreatingEmployee, setIsCreatingEmployee] = useState(false);
  const [isCreatingAttendance, setIsCreatingAttendance] = useState(false);
  const [deletingEmployeeId, setDeletingEmployeeId] = useState<string | null>(null);

  const activeDateLabel = useMemo(() => {
    return new Intl.DateTimeFormat("en-IN", {
      weekday: "long",
      day: "2-digit",
      month: "long",
      year: "numeric",
    }).format(new Date());
  }, []);

  async function loadWorkspace(nextFilters = filters, showLoader = true) {
    if (showLoader) {
      setLoading(true);
    }
    setPageError(null);

    try {
      const [employeeList, attendanceList, dashboard] = await Promise.all([
        api.getEmployees(),
        api.getAttendance({
          employeeId: nextFilters.employeeId || undefined,
          date: nextFilters.date || undefined,
        }),
        api.getDashboard(),
      ]);

      setEmployees(employeeList);
      setAttendance(attendanceList);
      setSummary(dashboard);
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "The workspace could not be loaded. Please try again.";
      setPageError(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadWorkspace(filters);
  }, [filters.employeeId, filters.date]);

  useEffect(() => {
    if (employees.length === 0) {
      setAttendanceForm((current) => ({ ...current, employee_id: "" }));
      return;
    }

    setAttendanceForm((current) => {
      if (current.employee_id) {
        const employeeStillExists = employees.some((employee) => employee.employee_id === current.employee_id);
        if (employeeStillExists) {
          return current;
        }
      }

      return { ...current, employee_id: employees[0].employee_id };
    });

    setFilters((current) => {
      if (!current.employeeId) {
        return current;
      }
      const employeeStillExists = employees.some((employee) => employee.employee_id === current.employeeId);
      return employeeStillExists ? current : { ...current, employeeId: "" };
    });
  }, [employees]);

  async function handleCreateEmployee(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreatingEmployee(true);
    setNotice(null);

    try {
      await api.createEmployee(employeeForm);
      setEmployeeForm(initialEmployeeForm);
      setNotice({ kind: "success", message: "Employee added successfully." });
      await loadWorkspace(filters, false);
    } catch (error) {
      setNotice({
        kind: "error",
        message: error instanceof ApiError ? error.message : "Unable to add employee.",
      });
    } finally {
      setIsCreatingEmployee(false);
    }
  }

  async function handleCreateAttendance(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreatingAttendance(true);
    setNotice(null);

    try {
      await api.createAttendance(attendanceForm);
      setAttendanceForm((current) => ({ ...current, status: "PRESENT" }));
      setNotice({ kind: "success", message: "Attendance recorded successfully." });
      await loadWorkspace(filters, false);
    } catch (error) {
      setNotice({
        kind: "error",
        message: error instanceof ApiError ? error.message : "Unable to record attendance.",
      });
    } finally {
      setIsCreatingAttendance(false);
    }
  }

  async function handleDeleteEmployee(employeeId: string) {
    const confirmed = window.confirm(`Delete employee ${employeeId}? Their attendance records will be removed too.`);
    if (!confirmed) {
      return;
    }

    setDeletingEmployeeId(employeeId);
    setNotice(null);

    try {
      await api.deleteEmployee(employeeId);
      setNotice({ kind: "success", message: "Employee removed successfully." });
      await loadWorkspace(filters, false);
    } catch (error) {
      setNotice({
        kind: "error",
        message: error instanceof ApiError ? error.message : "Unable to delete employee.",
      });
    } finally {
      setDeletingEmployeeId(null);
    }
  }

  const summaryItems = [
    {
      label: "Employees",
      value: summary?.total_employees ?? "0",
      hint: "Tracked across departments",
    },
    {
      label: "Attendance Entries",
      value: summary?.total_attendance_records ?? "0",
      hint: "Historical attendance records",
    },
    {
      label: "Present Today",
      value: summary?.present_today ?? "0",
      hint: "Marked as present today",
    },
    {
      label: "Absent Today",
      value: summary?.absent_today ?? "0",
      hint: "Marked as absent today",
    },
  ];

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero__content">
          <p className="hero__eyebrow">HRMS Lite / Admin Console</p>
          <h1>Employee records and attendance management</h1>
          <p className="hero__copy">
            Manage employee profiles, record daily attendance, and review workforce status from one internal
            dashboard.
          </p>
        </div>
        <aside className="hero__panel">
          <span className="hero__panel-label">Workspace Date</span>
          <strong>{activeDateLabel}</strong>
          <p>Operational snapshot for employee records, attendance updates, and current totals.</p>
          <dl className="hero__stats">
            <div>
              <dt>Employees</dt>
              <dd>{summary?.total_employees ?? 0}</dd>
            </div>
            <div>
              <dt>Present Today</dt>
              <dd>{summary?.present_today ?? 0}</dd>
            </div>
          </dl>
        </aside>
      </header>

      {notice ? (
        <div className={`notice notice--${notice.kind}`}>
          <span>{notice.message}</span>
          <button type="button" className="ghost-button" onClick={() => setNotice(null)}>
            Dismiss
          </button>
        </div>
      ) : null}

      {pageError ? (
        <div className="notice notice--error">
          <span>{pageError}</span>
          <button type="button" className="ghost-button" onClick={() => void loadWorkspace(filters)}>
            Retry
          </button>
        </div>
      ) : null}

      <section className="summary-grid">
        {summaryItems.map((item) => (
          <SummaryCard key={item.label} label={item.label} value={item.value} hint={item.hint} />
        ))}
      </section>

      <section className="content-grid content-grid--forms">
        <SectionCard title="Employee Management" description="Add employee records with clean validation.">
          <form className="form-grid" onSubmit={handleCreateEmployee}>
            <Field label="Employee ID" htmlFor="employee_id" hint="Must be unique across the organisation.">
              <input
                id="employee_id"
                value={employeeForm.employee_id}
                onChange={(event) =>
                  setEmployeeForm((current) => ({ ...current, employee_id: event.target.value }))
                }
                placeholder="EMP-1001"
                required
              />
            </Field>
            <Field label="Full Name" htmlFor="full_name">
              <input
                id="full_name"
                value={employeeForm.full_name}
                onChange={(event) => setEmployeeForm((current) => ({ ...current, full_name: event.target.value }))}
                placeholder="Ava Carter"
                required
              />
            </Field>
            <Field label="Email Address" htmlFor="email_address">
              <input
                id="email_address"
                type="email"
                value={employeeForm.email_address}
                onChange={(event) =>
                  setEmployeeForm((current) => ({ ...current, email_address: event.target.value }))
                }
                placeholder="ava.carter@company.com"
                required
              />
            </Field>
            <Field label="Department" htmlFor="department">
              <input
                id="department"
                value={employeeForm.department}
                onChange={(event) => setEmployeeForm((current) => ({ ...current, department: event.target.value }))}
                placeholder="Operations"
                required
              />
            </Field>
            <button className="primary-button" type="submit" disabled={isCreatingEmployee}>
              {isCreatingEmployee ? "Saving..." : "Add Employee"}
            </button>
          </form>
        </SectionCard>

        <SectionCard title="Attendance Management" description="Mark daily presence or absence in one step.">
          <form className="form-grid" onSubmit={handleCreateAttendance}>
            <Field label="Employee" htmlFor="attendance_employee" hint="Employees are pulled from the live directory.">
              <select
                id="attendance_employee"
                value={attendanceForm.employee_id}
                onChange={(event) =>
                  setAttendanceForm((current) => ({ ...current, employee_id: event.target.value }))
                }
                required
                disabled={employees.length === 0}
              >
                {employees.length === 0 ? <option value="">No employees available</option> : null}
                {employees.map((employee) => (
                  <option key={employee.employee_id} value={employee.employee_id}>
                    {employee.full_name} ({employee.employee_id})
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Date" htmlFor="attendance_date">
              <input
                id="attendance_date"
                type="date"
                value={attendanceForm.date}
                onChange={(event) => setAttendanceForm((current) => ({ ...current, date: event.target.value }))}
                required
              />
            </Field>
            <Field label="Status" htmlFor="attendance_status">
              <select
                id="attendance_status"
                value={attendanceForm.status}
                onChange={(event) =>
                  setAttendanceForm((current) => ({
                    ...current,
                    status: event.target.value as AttendanceStatus,
                  }))
                }
              >
                <option value="PRESENT">Present</option>
                <option value="ABSENT">Absent</option>
              </select>
            </Field>
            <button className="primary-button" type="submit" disabled={isCreatingAttendance || employees.length === 0}>
              {isCreatingAttendance ? "Saving..." : "Record Attendance"}
            </button>
          </form>
        </SectionCard>
      </section>

      <section className="content-grid">
        <SectionCard
          title="Employee Directory"
          description="Review employees and present-day totals at a glance."
          action={<span className="section-card__meta">{employees.length} records</span>}
        >
          {loading ? (
            <div className="loading-state">Loading employees...</div>
          ) : employees.length === 0 ? (
            <EmptyState
              title="No employees yet"
              body="Create the first employee record to start tracking attendance."
            />
          ) : (
            <div className="table-wrapper">
              <table className="data-table data-table--directory">
                <thead>
                  <tr>
                    <th className="column-employee">Employee</th>
                    <th className="column-department">Department</th>
                    <th className="column-email">Email</th>
                    <th className="column-count">Present Days</th>
                    <th className="column-date">Added</th>
                    <th className="column-action" />
                  </tr>
                </thead>
                <tbody>
                  {employees.map((employee) => (
                    <tr key={employee.employee_id}>
                      <td className="column-employee">
                        <div className="table-primary">
                          <strong>{employee.full_name}</strong>
                          <span>{employee.employee_id}</span>
                        </div>
                      </td>
                      <td className="column-department">{employee.department}</td>
                      <td className="column-email">{employee.email_address}</td>
                      <td className="column-count">{employee.total_present_days}</td>
                      <td className="column-date">{formatRelativeTimestamp(employee.created_at)}</td>
                      <td className="table-actions column-action">
                        <button
                          type="button"
                          className="danger-button"
                          onClick={() => void handleDeleteEmployee(employee.employee_id)}
                          disabled={deletingEmployeeId === employee.employee_id}
                        >
                          {deletingEmployeeId === employee.employee_id ? "Removing..." : "Delete"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Attendance Log"
          description="Inspect daily records with optional employee and date filters."
          action={
            <div className="filters-inline">
              <select
                aria-label="Filter by employee"
                value={filters.employeeId}
                onChange={(event) => setFilters((current) => ({ ...current, employeeId: event.target.value }))}
              >
                <option value="">All employees</option>
                {employees.map((employee) => (
                  <option key={employee.employee_id} value={employee.employee_id}>
                    {employee.full_name}
                  </option>
                ))}
              </select>
              <input
                aria-label="Filter by date"
                type="date"
                value={filters.date}
                onChange={(event) => setFilters((current) => ({ ...current, date: event.target.value }))}
              />
              <button
                type="button"
                className="ghost-button"
                onClick={() => setFilters({ employeeId: "", date: "" })}
                disabled={!filters.employeeId && !filters.date}
              >
                Clear
              </button>
            </div>
          }
        >
          {loading ? (
            <div className="loading-state">Loading attendance...</div>
          ) : attendance.length === 0 ? (
            <EmptyState
              title="No attendance records found"
              body="Mark attendance to populate the log, or clear filters to view more results."
            />
          ) : (
            <div className="table-wrapper">
              <table className="data-table data-table--attendance">
                <thead>
                  <tr>
                    <th className="column-employee">Employee</th>
                    <th className="column-department">Department</th>
                    <th className="column-date">Date</th>
                    <th className="column-status">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {attendance.map((record) => (
                    <tr key={record.id}>
                      <td className="column-employee">
                        <div className="table-primary">
                          <strong>{record.employee_name}</strong>
                          <span>{record.employee_id}</span>
                        </div>
                      </td>
                      <td className="column-department">{record.department}</td>
                      <td className="column-date">{formatDate(record.date)}</td>
                      <td className="column-status">
                        <StatusBadge status={record.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>
      </section>
    </div>
  );
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...options.headers,
    },
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path),
  post: <T>(path: string, body?: unknown) =>
    apiFetch<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put: <T>(path: string, body?: unknown) =>
    apiFetch<T>(path, { method: "PUT", body: JSON.stringify(body) }),
};

export type ActivityEvent = {
  id: number;
  agent_type: string;
  action: string;
  summary: string;
  level: "info" | "success" | "warning" | "error";
  created_at: string;
};

export type DashboardSummary = {
  tasks_today_total: number;
  tasks_today_completed: number;
  tasks_today_pending: number;
  tasks_today_failed: number;
  active_agents: string[];
  kpis: Record<string, unknown>;
  last_report_date: string | null;
};

export type Task = {
  id: number;
  title: string;
  agent_type: string;
  status: string;
  priority: number;
  created_at: string;
};

export type AgentStatus = {
  agent_type: string;
  last_run_at: string | null;
  last_run_status: string | null;
  tasks_today: number;
  tasks_total: number;
};

export type FinanceSummary = {
  mrr_cents: number;
  arr_cents: number;
  active_subscribers: number;
  total_ad_spend_usd: number;
  total_expenses_month_cents: number;
  stripe_balance_cents: number;
  last_snapshot_date: string | null;
};

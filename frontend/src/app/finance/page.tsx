import { MetricsCard } from "@/components/dashboard/MetricsCard";
import { api, type FinanceSummary } from "@/lib/api";

async function getFinanceSummary(): Promise<FinanceSummary | null> {
  try {
    return await api.get<FinanceSummary>("/finance/summary");
  } catch {
    return null;
  }
}

function formatCents(cents: number): string {
  return `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default async function FinancePage() {
  const summary = await getFinanceSummary();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Finance</h1>
        {summary?.last_snapshot_date && (
          <p className="text-gray-400 text-sm">Last snapshot: {summary.last_snapshot_date}</p>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <MetricsCard
          title="MRR"
          value={summary ? formatCents(summary.mrr_cents) : "—"}
          trend="up"
        />
        <MetricsCard
          title="ARR"
          value={summary ? formatCents(summary.arr_cents) : "—"}
          trend="up"
        />
        <MetricsCard
          title="Active Subscribers"
          value={summary?.active_subscribers ?? "—"}
        />
        <MetricsCard
          title="Stripe Balance"
          value={summary ? formatCents(summary.stripe_balance_cents) : "—"}
        />
        <MetricsCard
          title="Total Ad Spend"
          value={summary ? `$${summary.total_ad_spend_usd.toFixed(2)}` : "—"}
          trend="neutral"
        />
        <MetricsCard
          title="Expenses (Month)"
          value={summary ? formatCents(summary.total_expenses_month_cents) : "—"}
          trend="neutral"
        />
      </div>
    </div>
  );
}

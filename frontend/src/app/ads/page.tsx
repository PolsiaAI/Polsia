import { api } from "@/lib/api";

type Campaign = { id: number; platform: string; name: string; status: string; daily_budget_usd: number; total_spent_usd: number };

async function getCampaigns() {
  try { return await api.get<Campaign[]>("/ads/campaigns"); } catch { return []; }
}

export default async function AdsPage() {
  const campaigns = await getCampaigns();
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold text-white">Ad Campaigns</h1>
      <div className="space-y-3">
        {campaigns.length === 0 && <p className="text-gray-400">No campaigns yet.</p>}
        {campaigns.map((c) => (
          <div key={c.id} className="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
            <div>
              <p className="text-white font-medium">{c.name}</p>
              <p className="text-gray-400 text-sm capitalize">{c.platform} · {c.status}</p>
            </div>
            <div className="text-right">
              <p className="text-white">${c.total_spent_usd.toFixed(2)} spent</p>
              <p className="text-gray-400 text-sm">${c.daily_budget_usd}/day budget</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

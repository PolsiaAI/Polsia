"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Config = {
  name: string;
  mission: string | null;
  vision: string | null;
  description: string | null;
  target_market: string | null;
  value_prop: string | null;
  website_url: string | null;
  industry: string | null;
  product_type: string | null;
  timezone: string;
  daily_cycle_hour: number;
};

export default function SettingsPage() {
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.get<Config>("/config").then(setConfig).finally(() => setLoading(false));
  }, []);

  const save = async () => {
    if (!config) return;
    setSaving(true);
    try {
      const updated = await api.put<Config>("/config", config);
      setConfig(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-6 text-gray-400">Loading…</div>;
  if (!config) return <div className="p-6 text-red-400">Failed to load config</div>;

  const field = (label: string, key: keyof Config, type: "text" | "number" = "text") => (
    <div key={key}>
      <label className="block text-sm text-gray-400 mb-1">{label}</label>
      <input
        type={type}
        value={(config[key] as string | number) ?? ""}
        onChange={(e) =>
          setConfig((c) => c ? { ...c, [key]: type === "number" ? Number(e.target.value) : e.target.value } : c)
        }
        className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm border border-gray-600 focus:border-indigo-500 focus:outline-none"
      />
    </div>
  );

  return (
    <div className="p-6 max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      {saved && (
        <div className="bg-green-900/50 border border-green-500 text-green-300 px-4 py-2 rounded text-sm">
          Settings saved successfully
        </div>
      )}

      <div className="bg-gray-800 rounded-lg p-5 space-y-4">
        <h2 className="text-white font-semibold">Company Profile</h2>
        {field("Company Name", "name")}
        {field("Industry", "industry")}
        {field("Product Type", "product_type")}
        {field("Website URL", "website_url")}
        {field("Mission", "mission")}
        {field("Vision", "vision")}
        {field("Description", "description")}
        {field("Target Market", "target_market")}
        {field("Value Proposition", "value_prop")}
      </div>

      <div className="bg-gray-800 rounded-lg p-5 space-y-4">
        <h2 className="text-white font-semibold">Scheduler</h2>
        {field("Timezone", "timezone")}
        {field("Morning Cycle Hour (UTC)", "daily_cycle_hour", "number")}
      </div>

      <button
        onClick={save}
        disabled={saving}
        className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-md text-sm"
      >
        {saving ? "Saving…" : "Save Settings"}
      </button>
    </div>
  );
}

"use client";
import { useState } from "react";
import { useAgentStatus } from "@/hooks/useAgentStatus";
import { api } from "@/lib/api";

const AGENT_DESCRIPTIONS: Record<string, string> = {
  orchestrator: "Generates daily task plans and evening summaries",
  business_planning: "Analyzes strategy, updates KPIs, identifies opportunities",
  competitor_research: "Researches competitors and market positioning",
  social_media: "Drafts and posts tweets, monitors engagement",
  ads_management: "Manages Google and Meta ad campaigns",
  email_outreach: "Finds prospects and sends personalized cold emails",
  code_generation: "Writes code, commits to GitHub, deploys",
  customer_support: "Reads inbox and drafts customer replies",
  finance: "Monitors Stripe revenue, expenses, and alerts",
};

export default function AgentsPage() {
  const { statuses, loading } = useAgentStatus();
  const [triggering, setTriggering] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const trigger = async (agentType: string) => {
    setTriggering(agentType);
    setMessage(null);
    try {
      const result = await api.post<{ message: string }>(`/agents/${agentType}/trigger`);
      setMessage(result.message);
    } catch (e) {
      setMessage(String(e));
    } finally {
      setTriggering(null);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white">Agents</h1>

      {message && (
        <div className="bg-indigo-900/50 border border-indigo-500 rounded-lg px-4 py-3 text-indigo-200 text-sm">
          {message}
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="h-20 bg-gray-800 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {statuses.map((s) => (
            <div
              key={s.agent_type}
              className="bg-gray-800 rounded-lg p-4 flex items-center justify-between"
            >
              <div>
                <h3 className="text-white font-medium capitalize">
                  {s.agent_type.replace(/_/g, " ")}
                </h3>
                <p className="text-gray-400 text-sm">
                  {AGENT_DESCRIPTIONS[s.agent_type] ?? ""}
                </p>
                <p className="text-gray-500 text-xs mt-1">
                  Last run: {s.last_run_at ? new Date(s.last_run_at).toLocaleString() : "Never"} ·{" "}
                  {s.tasks_today} tasks today
                </p>
              </div>
              <button
                onClick={() => trigger(s.agent_type)}
                disabled={triggering === s.agent_type}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm rounded-md transition-colors"
              >
                {triggering === s.agent_type ? "Triggering…" : "Run Now"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

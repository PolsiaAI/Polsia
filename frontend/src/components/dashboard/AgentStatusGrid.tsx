"use client";
import { useAgentStatus } from "@/hooks/useAgentStatus";

const STATUS_STYLE: Record<string, string> = {
  completed: "bg-green-500/20 text-green-400",
  running: "bg-blue-500/20 text-blue-400 animate-pulse",
  failed: "bg-red-500/20 text-red-400",
};

const AGENT_LABELS: Record<string, string> = {
  orchestrator: "Orchestrator",
  business_planning: "Strategy",
  competitor_research: "Research",
  social_media: "Social",
  ads_management: "Ads",
  email_outreach: "Outreach",
  code_generation: "Code",
  customer_support: "Support",
  finance: "Finance",
};

export function AgentStatusGrid() {
  const { statuses, loading } = useAgentStatus();

  if (loading) {
    return (
      <div className="grid grid-cols-3 gap-3">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="h-20 bg-gray-700 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-3">
      {statuses.map((s) => {
        const statusStyle = STATUS_STYLE[s.last_run_status ?? ""] ?? "bg-gray-700/40 text-gray-400";
        return (
          <div key={s.agent_type} className="bg-gray-800 rounded-lg p-3">
            <p className="text-white text-sm font-medium">
              {AGENT_LABELS[s.agent_type] ?? s.agent_type}
            </p>
            <span className={`inline-block px-2 py-0.5 rounded text-xs mt-1 ${statusStyle}`}>
              {s.last_run_status ?? "idle"}
            </span>
            <p className="text-gray-400 text-xs mt-1">{s.tasks_today} tasks today</p>
          </div>
        );
      })}
    </div>
  );
}

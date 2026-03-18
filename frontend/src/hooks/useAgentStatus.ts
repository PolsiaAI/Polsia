"use client";
import { useEffect, useState } from "react";
import { api, type AgentStatus } from "@/lib/api";

export function useAgentStatus(pollIntervalMs = 30000) {
  const [statuses, setStatuses] = useState<AgentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetch = async () => {
      try {
        const data = await api.get<AgentStatus[]>("/agents/status");
        if (!cancelled) {
          setStatuses(data);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) setError(String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetch();
    const interval = setInterval(fetch, pollIntervalMs);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [pollIntervalMs]);

  return { statuses, loading, error };
}

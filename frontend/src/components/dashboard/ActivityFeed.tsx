"use client";
import { useActivityFeed } from "@/hooks/useActivityFeed";

const LEVEL_STYLES: Record<string, string> = {
  success: "text-green-400",
  error: "text-red-400",
  warning: "text-yellow-400",
  info: "text-blue-400",
};

const LEVEL_DOT: Record<string, string> = {
  success: "bg-green-400",
  error: "bg-red-400",
  warning: "bg-yellow-400",
  info: "bg-blue-400",
};

export function ActivityFeed() {
  const { events, connected } = useActivityFeed();

  return (
    <div className="bg-gray-800 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-white font-semibold text-sm">Live Activity</h2>
        <span className={`flex items-center gap-1 text-xs ${connected ? "text-green-400" : "text-gray-500"}`}>
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-green-400 animate-pulse" : "bg-gray-500"}`} />
          {connected ? "Live" : "Reconnecting…"}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-2 text-sm">
        {events.length === 0 && (
          <p className="text-gray-500 text-xs">No activity yet — agents will post here.</p>
        )}
        {events.map((e) => (
          <div key={e.id} className="flex gap-2 items-start">
            <span
              className={`mt-1.5 w-2 h-2 flex-shrink-0 rounded-full ${LEVEL_DOT[e.level] ?? "bg-gray-400"}`}
            />
            <div>
              <span className={`font-medium ${LEVEL_STYLES[e.level] ?? "text-gray-300"}`}>
                {e.agent_type}
              </span>
              <span className="text-gray-400 mx-1">·</span>
              <span className="text-gray-200">{e.summary}</span>
              <div className="text-gray-500 text-xs">
                {new Date(e.created_at).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

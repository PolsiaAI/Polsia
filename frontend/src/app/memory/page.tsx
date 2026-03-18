"use client";
import { useState } from "react";
import { api } from "@/lib/api";

type Memory = { id: number; category: string; title: string; content: string; created_at: string };

export default function MemoryPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await api.get<Memory[]>(`/memory?q=${encodeURIComponent(query)}&limit=20`);
      setResults(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white">Memory</h1>
      <div className="flex gap-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
          placeholder="Search company memory…"
          className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 border border-gray-700 focus:border-indigo-500 focus:outline-none"
        />
        <button
          onClick={search}
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm disabled:opacity-50"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </div>
      <div className="space-y-3">
        {results.map((m) => (
          <div key={m.id} className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs bg-indigo-600/30 text-indigo-300 px-2 py-0.5 rounded">
                {m.category}
              </span>
              <span className="text-gray-500 text-xs">{new Date(m.created_at).toLocaleDateString()}</span>
            </div>
            <p className="text-white font-medium text-sm">{m.title}</p>
            <p className="text-gray-400 text-sm mt-1 line-clamp-3">{m.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

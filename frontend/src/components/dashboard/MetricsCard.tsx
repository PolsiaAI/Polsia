interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  loading?: boolean;
}

export function MetricsCard({ title, value, subtitle, trend, loading }: MetricsCardProps) {
  const trendColor =
    trend === "up" ? "text-green-400" : trend === "down" ? "text-red-400" : "text-gray-400";

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <p className="text-gray-400 text-xs uppercase tracking-wider">{title}</p>
      {loading ? (
        <div className="h-8 bg-gray-700 rounded animate-pulse mt-2" />
      ) : (
        <p className="text-white text-2xl font-bold mt-1">{value}</p>
      )}
      {subtitle && (
        <p className={`text-xs mt-1 ${trendColor}`}>{subtitle}</p>
      )}
    </div>
  );
}

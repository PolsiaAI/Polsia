"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart2,
  Bot,
  BriefcaseBusiness,
  DollarSign,
  Mail,
  Megaphone,
  MessageSquare,
  Settings,
  Twitter,
  Database,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart2 },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/tasks", label: "Tasks", icon: BriefcaseBusiness },
  { href: "/social", label: "Social", icon: Twitter },
  { href: "/outreach", label: "Outreach", icon: Mail },
  { href: "/ads", label: "Ads", icon: Megaphone },
  { href: "/finance", label: "Finance", icon: DollarSign },
  { href: "/memory", label: "Memory", icon: Database },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 min-h-screen bg-gray-900 text-white flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-bold text-indigo-400">Polsia</h1>
        <p className="text-xs text-gray-400">AI Business Agent</p>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-indigo-600 text-white"
                  : "text-gray-300 hover:bg-gray-700"
              }`}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

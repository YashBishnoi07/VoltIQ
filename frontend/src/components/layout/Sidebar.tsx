import React from "react";
import {
  LayoutDashboard,
  TrendingUp,
  MapPin,
  Cpu,
  FlaskConical,
  Award,
  Sparkles,
  FileSpreadsheet,
} from "lucide-react";

export type PageId =
  | "overview"
  | "demand"
  | "explorer"
  | "classifier"
  | "analytics"
  | "arena"
  | "insights"
  | "batch";

interface SidebarProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onSelectPage }) => {
  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "demand", label: "Demand Forecast", icon: TrendingUp },
    { id: "explorer", label: "Station Explorer", icon: MapPin },
    { id: "classifier", label: "Utilization Classifier", icon: Cpu },
    { id: "analytics", label: "Analytics Lab", icon: FlaskConical },
    { id: "arena", label: "Model Arena", icon: Award },
    { id: "insights", label: "Insights & Ethics", icon: Sparkles },
    { id: "batch", label: "Batch Scoring", icon: FileSpreadsheet },
  ] as const;

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#080B10]/90 p-4 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-mono tracking-widest uppercase text-slate-500">
          Core Platform
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id as PageId)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-cyan-950/40 text-cyan-400 border border-cyan-800/60 shadow-lg shadow-cyan-950/50"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-500"}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800 text-xs text-slate-400 space-y-1">
        <div className="font-semibold text-slate-300">Dataset Active</div>
        <div className="text-[11px] text-slate-500 font-mono">ACN Synthetic Engine</div>
        <div className="text-[11px] text-emerald-400 font-mono">50,000 sessions loaded</div>
      </div>
    </aside>
  );
};

import React from "react";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: string;
  badgeColor?: "cyan" | "lime" | "violet" | "amber";
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  badgeColor = "cyan",
}) => {
  const badgeClasses = {
    cyan: "bg-cyan-950/60 text-cyan-400 border-cyan-800/60",
    lime: "bg-lime-950/60 text-lime-400 border-lime-800/60",
    violet: "bg-violet-950/60 text-violet-400 border-violet-800/60",
    amber: "bg-amber-950/60 text-amber-400 border-amber-800/60",
  }[badgeColor];

  return (
    <div className="glass-panel glass-panel-hover p-5 rounded-xl transition-all relative overflow-hidden group">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 group-hover:text-cyan-400 group-hover:border-cyan-500/30 transition-colors">
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-3xl font-bold font-mono text-slate-100 tracking-tight">
          {value}
        </span>
        {badge && (
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${badgeClasses}`}>
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs text-slate-400 font-sans">{subtitle}</p>
      )}
    </div>
  );
};

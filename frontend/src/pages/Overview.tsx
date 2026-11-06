import React, { useEffect, useState } from "react";
import { Zap, BatteryCharging, Gauge, Flame, Layers } from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { StatCard } from "../components/ui/StatCard";
import { api } from "../services/api";
import { HourlyDemandPoint, OverviewMetrics } from "../types";

export const Overview: React.FC = () => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [hourlyData, setHourlyData] = useState<HourlyDemandPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, h] = await Promise.all([api.getOverview(), api.getHourlyDemand()]);
        setMetrics(m);
        setHourlyData(h.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-cyan-400 font-mono animate-pulse">
        Initializing VoltIQ Intelligence Hub...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Hero Header */}
      <div>
        <h1 className="text-2xl font-orbitron font-bold text-slate-100 flex items-center space-x-2">
          <span>Command Center</span>
          <span className="text-xs font-mono font-normal text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full">
            LIVE ANALYTICS
          </span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Real-time network telemetry, spatial utilization patterns, and automated capacity alerts.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Sessions"
          value={metrics?.total_sessions.toLocaleString() ?? "—"}
          subtitle="Processed charging events"
          icon={Zap}
          badge="+14.2%"
          badgeColor="cyan"
        />
        <StatCard
          title="Energy Delivered"
          value={`${((metrics?.total_kwh ?? 0) / 1000).toFixed(1)} MWh`}
          subtitle="Total power transmitted"
          icon={BatteryCharging}
          badge="High Efficiency"
          badgeColor="lime"
        />
        <StatCard
          title="Average Utilization"
          value={`${((metrics?.avg_utilization ?? 0) * 100).toFixed(1)}%`}
          subtitle="Network port occupancy"
          icon={Gauge}
          badge="Balanced"
          badgeColor="violet"
        />
        <StatCard
          title="Peak Demand Hour"
          value={`${metrics?.peak_hour ?? 18}:00`}
          subtitle="Highest concurrency slot"
          icon={Flame}
          badge="Evening Peak"
          badgeColor="amber"
        />
      </div>

      {/* Primary Chart */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-orbitron font-semibold text-slate-200">
              Diurnal Demand Profile (Sessions / Hour)
            </h3>
            <p className="text-xs text-slate-400">
              Aggregate 24-hour demand curve comparing Weekday commute waves vs Weekend leisure cycles.
            </p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <div className="flex items-center space-x-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
              <span className="text-slate-300">Weekday</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-lime-400"></span>
              <span className="text-slate-300">Weekend</span>
            </div>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={hourlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="cyanGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#00F0FF" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="limeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#39FF14" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#39FF14" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="hour" stroke="#64748B" tickFormatter={(h) => `${h}h`} />
              <YAxis stroke="#64748B" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0E131F",
                  borderColor: "#1E293B",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Area
                type="monotone"
                dataKey="weekday_avg"
                stroke="#00F0FF"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#cyanGrad)"
                name="Weekday Avg"
              />
              <Area
                type="monotone"
                dataKey="weekend_avg"
                stroke="#39FF14"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#limeGrad)"
                name="Weekend Avg"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

import React, { useEffect, useState } from "react";
import { FlaskConical, CheckCircle } from "lucide-react";
import { api } from "../services/api";
import { HeatmapCell, StatTestResult } from "../types";

export const AnalyticsLab: React.FC = () => {
  const [heatmap, setHeatmap] = useState<HeatmapCell[]>([]);
  const [stats, setStats] = useState<StatTestResult[]>([]);
  const [hoveredCell, setHoveredCell] = useState<{ day: string; hour: number; val: number } | null>(null);

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  useEffect(() => {
    // Load heatmap independently
    api.getHeatmap()
      .then((res) => {
        if (res && res.data) setHeatmap(res.data);
      })
      .catch((err) => console.error("Error loading heatmap:", err));

    // Load stats independently
    api.getStats()
      .then((res) => {
        if (Array.isArray(res)) setStats(res);
      })
      .catch((err) => console.error("Error loading stats:", err));
  }, []);

  const getHeatmapVal = (dow: number, hr: number): number => {
    const cell = heatmap.find((c) => c.day_of_week === dow && c.hour === hr);
    return cell ? cell.avg_sessions : 0;
  };

  const values = heatmap.map((c) => c.avg_sessions).filter((v) => v > 0);
  const minVal = values.length > 0 ? Math.min(...values) : 0;
  const maxVal = values.length > 0 ? Math.max(...values) : 1;
  const range = maxVal - minVal > 0 ? maxVal - minVal : 1;

  // Compute cell color gradient from deep navy -> bright cyan -> electric lime
  const getCellColor = (val: number): { bg: string; glow: string } => {
    if (val === 0) return { bg: "#0B111E", glow: "none" };

    const ratio = Math.max(0, Math.min(1, (val - minVal) / range));

    if (ratio < 0.35) {
      // Low: Dark blue / teal
      const alpha = 0.25 + ratio * 0.5;
      return { bg: `rgba(0, 150, 255, ${alpha.toFixed(2)})`, glow: "none" };
    } else if (ratio < 0.75) {
      // Medium: Bright electric cyan
      const alpha = 0.5 + (ratio - 0.35) * 1.0;
      return { bg: `rgba(0, 240, 255, ${Math.min(alpha, 0.9).toFixed(2)})`, glow: "0 0 6px rgba(0, 240, 255, 0.3)" };
    } else {
      // Peak: Electric lime / neon cyan-lime
      const alpha = 0.7 + (ratio - 0.75) * 1.2;
      return { bg: `rgba(57, 255, 20, ${Math.min(alpha, 1.0).toFixed(2)})`, glow: "0 0 10px rgba(57, 255, 20, 0.5)" };
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-orbitron font-bold text-slate-100 flex items-center space-x-2">
          <FlaskConical className="w-6 h-6 text-cyan-400" />
          <span>Analytics & Statistical Lab</span>
        </h1>
        <p className="text-sm text-slate-400">
          Rigorous hypothesis testing, normality validation, and 7×24 diurnal demand heatmap.
        </p>
      </div>

      {/* Heatmap Section */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-orbitron font-semibold text-slate-200">
              7×24 Day-and-Hour Concurrency Matrix
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              {hoveredCell ? (
                <span className="text-cyan-400 font-mono">
                  <b>{hoveredCell.day}</b> at <b>{hoveredCell.hour}:00</b> —{" "}
                  <b className="text-lime-300">{hoveredCell.val.toFixed(3)} avg sessions/hr</b>
                </span>
              ) : (
                "Hover over any hour cell to inspect network concurrency volume"
              )}
            </p>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono text-slate-400">
            <span className="text-[11px]">Low ({minVal.toFixed(2)})</span>
            <div
              className="h-3 w-36 rounded border border-slate-700"
              style={{
                background: "linear-gradient(to right, rgba(0, 150, 255, 0.3), rgba(0, 240, 255, 0.8), rgba(57, 255, 20, 1.0))",
              }}
            />
            <span className="text-[11px] text-lime-400 font-bold">Peak ({maxVal.toFixed(2)})</span>
          </div>
        </div>

        <div className="overflow-x-auto pb-4">
          <div className="min-w-[760px] space-y-1.5 pt-2">
            {/* Header: Hour labels */}
            <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400">
              <span className="w-12 text-right pr-2 text-slate-500 font-bold uppercase">Day</span>
              <div
                className="flex-1 gap-1"
                style={{ display: "grid", gridTemplateColumns: "repeat(24, minmax(0, 1fr))" }}
              >
                {hours.map((h) => (
                  <div key={h} className="text-center font-mono">
                    {h % 2 === 0 ? `${h}h` : ""}
                  </div>
                ))}
              </div>
            </div>

            {/* Matrix rows: Mon -> Sun */}
            {days.map((dayName, dow) => (
              <div key={dayName} className="flex items-center space-x-2">
                <span className="w-12 text-xs font-mono font-semibold text-cyan-300 text-right pr-2">
                  {dayName}
                </span>
                <div
                  className="flex-1 gap-1"
                  style={{ display: "grid", gridTemplateColumns: "repeat(24, minmax(0, 1fr))" }}
                >
                  {hours.map((h) => {
                    const val = getHeatmapVal(dow, h);
                    const { bg, glow } = getCellColor(val);
                    return (
                      <div
                        key={h}
                        onMouseEnter={() => setHoveredCell({ day: dayName, hour: h, val })}
                        onMouseLeave={() => setHoveredCell(null)}
                        className="h-7 rounded transition-all hover:scale-125 hover:z-20 cursor-pointer border border-slate-900/40"
                        style={{
                          backgroundColor: bg,
                          boxShadow: glow,
                        }}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Hypothesis Testing Cards */}
      <div className="space-y-3">
        <h3 className="font-orbitron font-semibold text-slate-200">
          Statistical Hypothesis Testing Suite
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stats.length > 0 ? (
            stats.map((test) => (
              <div
                key={test.test_name}
                className="glass-panel p-5 rounded-xl space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-orbitron font-bold text-sm text-cyan-400">
                      {test.test_name}
                    </span>
                    {test.significant ? (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 flex items-center space-x-1">
                        <CheckCircle className="w-3 h-3" />
                        <span>p &lt; 0.05</span>
                      </span>
                    ) : (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        Not Sig
                      </span>
                    )}
                  </div>

                  <div className="flex items-baseline space-x-3 text-xs font-mono text-slate-300 py-1">
                    <span>
                      Stat: <b className="text-slate-100">{test.statistic.toFixed(3)}</b>
                    </span>
                    <span>
                      p-value: <b className="text-cyan-300">{test.p_value.toFixed(5)}</b>
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {test.interpretation}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-800/80 text-[10px] font-mono text-slate-500">
                  Confidence Level: 95% (α = 0.05)
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 text-xs font-mono text-slate-500">
              Evaluating hypothesis tests...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

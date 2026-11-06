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
    async function load() {
      try {
        const [h, s] = await Promise.all([api.getHeatmap(), api.getStats()]);
        setHeatmap(h.data);
        setStats(s);
      } catch (e) {
        console.error(e);
      }
    }
    load();
  }, []);

  const getHeatmapVal = (dow: number, hr: number): number => {
    const cell = heatmap.find((c) => c.day_of_week === dow && c.hour === hr);
    return cell ? cell.avg_sessions : 0;
  };

  const maxVal = Math.max(...heatmap.map((c) => c.avg_sessions), 1.0);

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
            <p className="text-xs text-slate-400">
              {hoveredCell ? (
                <span className="text-cyan-400 font-mono">
                  {hoveredCell.day} at {hoveredCell.hour}:00 —{" "}
                  <b>{hoveredCell.val.toFixed(2)} sessions/hr</b>
                </span>
              ) : (
                "Hover over any hour cell to inspect network concurrency volume"
              )}
            </p>
          </div>
          <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
            <span>Low (0)</span>
            <div className="flex h-3 w-28 rounded bg-gradient-to-r from-slate-900 via-cyan-900 to-cyan-400 border border-slate-800"></div>
            <span>Peak ({maxVal.toFixed(1)})</span>
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
            {days.map((dayName, dow) => {
              return (
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
                      const ratio = maxVal > 0 ? val / maxVal : 0;
                      return (
                        <div
                          key={h}
                          onMouseEnter={() => setHoveredCell({ day: dayName, hour: h, val })}
                          onMouseLeave={() => setHoveredCell(null)}
                          className="h-7 rounded transition-all hover:scale-125 hover:z-10 cursor-pointer border border-slate-900/40"
                          style={{
                            backgroundColor:
                              val === 0
                                ? "#0E131F"
                                : `rgba(0, 240, 255, ${Math.max(ratio, 0.15)})`,
                            boxShadow: ratio > 0.7 ? "0 0 8px rgba(0, 240, 255, 0.4)" : "none",
                          }}
                        />
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Hypothesis Testing Cards */}
      <div className="space-y-3">
        <h3 className="font-orbitron font-semibold text-slate-200">
          Statistical Hypothesis Testing Suite
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stats.map((test) => (
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
          ))}
        </div>
      </div>
    </div>
  );
};

import React, { useEffect, useState } from "react";
import { FlaskConical, CheckCircle, AlertTriangle } from "lucide-react";
import { api } from "../services/api";
import { HeatmapCell, StatTestResult } from "../types";

export const AnalyticsLab: React.FC = () => {
  const [heatmap, setHeatmap] = useState<HeatmapCell[]>([]);
  const [stats, setStats] = useState<StatTestResult[]>([]);
  const [loading, setLoading] = useState(true);

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
      } finally {
        setLoading(false);
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
          Rigorous hypothesis testing, normality validation, and 7x24 spatio-temporal concurrency heatmaps.
        </p>
      </div>

      {/* Heatmap */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-orbitron font-semibold text-slate-200">
            Hour-of-Week Concurrency Matrix (Heatmap)
          </h3>
          <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
            <span>Low</span>
            <div className="flex h-3 w-24 rounded bg-gradient-to-r from-slate-900 via-cyan-900 to-cyan-400"></div>
            <span>High Peak</span>
          </div>
        </div>

        <div className="overflow-x-auto pb-2">
          <div className="min-w-[650px] space-y-1">
            {/* Header hours */}
            <div className="grid grid-cols-25 gap-1 text-[10px] font-mono text-slate-500 pl-10">
              {hours.map((h) => (
                <div key={h} className="text-center">
                  {h % 3 === 0 ? h : ""}
                </div>
              ))}
            </div>

            {/* Matrix rows */}
            {days.map((dayName, dow) => (
              <div key={dayName} className="flex items-center space-x-2">
                <span className="w-8 text-xs font-mono text-slate-400">{dayName}</span>
                <div className="grid grid-cols-24 gap-1 flex-1">
                  {hours.map((h) => {
                    const val = getHeatmapVal(dow, h);
                    const opacity = Math.min(Math.max(val / maxVal, 0.1), 1);
                    return (
                      <div
                        key={h}
                        title={`${dayName} ${h}:00 — ${val.toFixed(2)} sessions/hr`}
                        className="h-6 rounded-sm transition-all hover:scale-110 cursor-pointer"
                        style={{
                          backgroundColor:
                            val === 0
                              ? "rgba(15, 23, 42, 0.5)"
                              : `rgba(0, 240, 255, ${opacity})`,
                        }}
                      ></div>
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

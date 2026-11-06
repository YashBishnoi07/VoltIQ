import React, { useEffect, useState } from "react";
import { Sparkles, Shield, AlertTriangle, CheckCircle2 } from "lucide-react";
import { api } from "../services/api";
import { Station } from "../types";

export const Insights: React.FC = () => {
  const [underserved, setUnderserved] = useState<{
    stations: Station[];
    total: number;
    recommendation: string;
  } | null>(null);
  const [fairness, setFairness] = useState<{
    disparity_analysis: Record<string, any>;
    ethical_framework: string;
    disclaimer: string;
  } | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [u, f] = await Promise.all([api.getUnderserved(), api.getFairness()]);
        setUnderserved(u);
        setFairness(f);
      } catch (e) {
        console.error(e);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-orbitron font-bold text-slate-100 flex items-center space-x-2">
          <Sparkles className="w-6 h-6 text-cyan-400" />
          <span>Strategic Insights & Ethical Governance</span>
        </h1>
        <p className="text-sm text-slate-400">
          Algorithmic fairness audits, geographic disparity mitigation, and capacity allocation advice.
        </p>
      </div>

      {/* Ethics & Legal Notice Banner */}
      <div className="p-5 rounded-xl bg-cyan-950/20 border border-cyan-800/40 space-y-2">
        <div className="flex items-center space-x-2 text-cyan-400 font-orbitron text-sm font-semibold">
          <Shield className="w-5 h-5 text-cyan-400" />
          <span>VoltIQ Responsible AI Guarantee & Policy Notice</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          {fairness?.disclaimer ??
            "DECISION-SUPPORT NOTICE: Model outputs are statistical estimates with confidence intervals. They must not be used as sole justifications for capital allocation without field validation."}
        </p>
      </div>

      {/* Disparity Analysis by Region */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <h3 className="font-orbitron font-semibold text-slate-200">
          Spatial Fairness Audit (Relative Error by Density Cohort)
        </h3>
        <p className="text-xs text-slate-400">
          Validating that the demand forecasting error is balanced across urban and rural corridors,
          preventing reinforcement of infrastructure deserts.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {fairness?.disparity_analysis &&
            Object.entries(fairness.disparity_analysis).map(([region, metrics]) => (
              <div key={region} className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-mono font-bold text-sm text-slate-200 capitalize">
                    {region} Setting
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                    n = {metrics.n_samples}
                  </span>
                </div>
                <div className="space-y-1 text-xs font-mono">
                  <div className="flex justify-between text-slate-400">
                    <span>Mean Absolute Error:</span>
                    <span className="text-slate-200">{metrics.mae.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Mean Demand:</span>
                    <span className="text-slate-200">{metrics.mean_demand.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Relative Error Ratio:</span>
                    <span className="text-emerald-400 font-bold">
                      {(metrics.relative_mae * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Underserved Station Recommendations */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-orbitron font-semibold text-slate-200">
              Capacity Expansion Recommendations
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Identified candidate stations exhibiting high demand volatility relative to peer clusters.
            </p>
          </div>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/60 px-2.5 py-1 rounded">
            {underserved?.total ?? 0} Priority Stations
          </span>
        </div>

        {underserved && underserved.stations.length > 0 ? (
          <div className="divide-y divide-slate-800/60 border border-slate-800 rounded-lg overflow-hidden">
            {underserved.stations.map((st) => (
              <div key={st.station_id} className="p-3.5 flex items-center justify-between text-xs font-mono">
                <div>
                  <span className="font-bold text-slate-200">{st.station_id}</span>
                  <span className="ml-2 text-slate-500">
                    {st.location_type} • {st.region} • {st.power_kw} kW
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-cyan-400 font-semibold">
                    {((st.mean_utilization ?? 0) * 100).toFixed(1)}% util
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-800/40 text-xs text-emerald-300 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              All current network stations operate within balanced variance bounds. No severe disparity detected.
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

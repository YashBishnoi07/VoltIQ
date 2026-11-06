import React, { useEffect, useState } from "react";
import { Award, Zap, BarChart2 } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { api } from "../services/api";
import { ModelComparisonResponse } from "../types";

export const ModelArena: React.FC = () => {
  const [data, setData] = useState<ModelComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.getModelComparison();
        setData(res);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-cyan-400 font-mono animate-pulse">
        Benchmarking Arena Models...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-orbitron font-bold text-slate-100 flex items-center space-x-2">
          <Award className="w-6 h-6 text-lime-400" />
          <span>Model Benchmark Arena</span>
        </h1>
        <p className="text-sm text-slate-400">
          Cross-validated performance leaderboard with time-based splits and SHAP explainability.
        </p>
      </div>

      {/* Regression Leaderboard */}
      <div className="glass-panel rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-orbitron font-semibold text-slate-200">
            Demand Regression Leaderboard (Time-Series Split)
          </h3>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded">
            Champion: {data.best_regression_model}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/60 text-slate-400 border-b border-slate-800 uppercase">
              <tr>
                <th className="p-3">Rank</th>
                <th className="p-3">Model</th>
                <th className="p-3">RMSE ↓</th>
                <th className="p-3">MAE ↓</th>
                <th className="p-3">MAPE (%) ↓</th>
                <th className="p-3">R² Score ↑</th>
                <th className="p-3">Features</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {data.regression_leaderboard.map((m, idx) => (
                <tr
                  key={m.model}
                  className={idx === 0 ? "bg-cyan-950/20 text-cyan-300 font-bold" : "text-slate-300"}
                >
                  <td className="p-3 text-slate-500">#{idx + 1}</td>
                  <td className="p-3 font-semibold flex items-center space-x-1.5">
                    {idx === 0 && <Award className="w-3.5 h-3.5 text-lime-400" />}
                    <span>{m.model}</span>
                  </td>
                  <td className="p-3 text-cyan-400">{m.rmse.toFixed(4)}</td>
                  <td className="p-3">{m.mae.toFixed(4)}</td>
                  <td className="p-3">{m.mape.toFixed(2)}%</td>
                  <td className="p-3">{m.r2.toFixed(4)}</td>
                  <td className="p-3 text-slate-500">{m.feature_count ?? 25}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Classification Leaderboard */}
      <div className="glass-panel rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-orbitron font-semibold text-slate-200">
            Utilization Classifier Leaderboard (Balanced Multiclass)
          </h3>
          <span className="text-xs font-mono text-lime-400 bg-lime-950/60 border border-lime-800/60 px-2 py-0.5 rounded">
            Champion: {data.best_classification_model}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/60 text-slate-400 border-b border-slate-800 uppercase">
              <tr>
                <th className="p-3">Rank</th>
                <th className="p-3">Model</th>
                <th className="p-3">Accuracy ↑</th>
                <th className="p-3">Macro F1 ↑</th>
                <th className="p-3">Confusion Matrix</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {data.classification_leaderboard.map((m, idx) => (
                <tr key={m.model} className="text-slate-300">
                  <td className="p-3 text-slate-500">#{idx + 1}</td>
                  <td className="p-3 font-semibold text-slate-200">{m.model}</td>
                  <td className="p-3 text-lime-400">{(m.accuracy * 100).toFixed(1)}%</td>
                  <td className="p-3 font-bold text-cyan-400">{(m.f1_macro * 100).toFixed(1)}%</td>
                  <td className="p-3 text-slate-400 font-mono text-[10px]">
                    {JSON.stringify(m.confusion_matrix)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* SHAP Feature Importance */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <h3 className="font-orbitron font-semibold text-slate-200 flex items-center space-x-2">
          <BarChart2 className="w-4 h-4 text-cyan-400" />
          <span>SHAP Global Feature Importance (Top Predictors)</span>
        </h3>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data.shap_importance}
              layout="vertical"
              margin={{ top: 5, right: 20, left: 60, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis type="number" stroke="#64748B" />
              <YAxis dataKey="feature" type="category" stroke="#94A3B8" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0E131F",
                  borderColor: "#1E293B",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="importance" fill="#00F0FF" radius={[0, 4, 4, 0]} name="SHAP Value" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

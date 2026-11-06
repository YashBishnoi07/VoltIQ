import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Area,
  ComposedChart,
} from "recharts";
import { AlertCircle, Clock, Zap } from "lucide-react";
import { api } from "../services/api";
import { DemandForecastResponse, Station } from "../types";

export const DemandForecast: React.FC = () => {
  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState("STN-0001");
  const [horizon, setHorizon] = useState(24);
  const [forecast, setForecast] = useState<DemandForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function init() {
      const st = await api.getStations();
      setStations(st.stations);
      if (st.stations.length > 0) {
        setSelectedStation(st.stations[0].station_id);
      }
    }
    init();
  }, []);

  useEffect(() => {
    async function runForecast() {
      if (!selectedStation) return;
      setLoading(true);
      try {
        const res = await api.predictDemand(selectedStation, horizon);
        setForecast(res);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    runForecast();
  }, [selectedStation, horizon]);

  const formattedData =
    forecast?.forecast.map((pt, i) => {
      const date = new Date(pt.datetime);
      return {
        ...pt,
        hourLabel: `${date.getHours()}:00`,
        range: [pt.lower_bound, pt.upper_bound],
      };
    }) ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-orbitron font-bold text-slate-100">
            Demand Forecaster
          </h1>
          <p className="text-sm text-slate-400">
            Multi-horizon regression time-series with 95% bootstrap confidence bounds.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-3">
          <select
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 font-mono focus:border-cyan-500 focus:outline-none"
          >
            {stations.map((s) => (
              <option key={s.station_id} value={s.station_id}>
                {s.station_id} ({s.station_type} • {s.location_type})
              </option>
            ))}
          </select>

          <select
            value={horizon}
            onChange={(e) => setHorizon(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 font-mono focus:border-cyan-500 focus:outline-none"
          >
            <option value={12}>12 Hours Horizon</option>
            <option value={24}>24 Hours Horizon</option>
            <option value={48}>48 Hours Horizon</option>
            <option value={72}>72 Hours Horizon</option>
          </select>
        </div>
      </div>

      {/* Uncertainty Notice */}
      <div className="p-3.5 rounded-lg bg-cyan-950/30 border border-cyan-800/50 flex items-start space-x-3 text-xs text-cyan-300">
        <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-cyan-400" />
        <div>
          <span className="font-semibold">Decision-Support Notice: </span>
          {forecast?.uncertainty_note ??
            "Predictions carry statistical confidence intervals. Always validate against local events."}
        </div>
      </div>

      {/* Forecast Chart */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <h3 className="font-orbitron font-semibold text-slate-200">
              Station {selectedStation} — Expected Sessions ({horizon}h)
            </h3>
          </div>
          <div className="text-xs font-mono text-slate-400">
            Model: <span className="text-cyan-400">{forecast?.model_used}</span>
          </div>
        </div>

        <div className="h-80 w-full">
          {loading ? (
            <div className="flex items-center justify-center h-full text-slate-500 font-mono">
              Computing inference...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="hourLabel" stroke="#64748B" />
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
                  dataKey="upper_bound"
                  stroke="transparent"
                  fill="#00F0FF"
                  fillOpacity={0.15}
                  name="Confidence Band"
                />
                <Area
                  type="monotone"
                  dataKey="lower_bound"
                  stroke="transparent"
                  fill="#080B10"
                  fillOpacity={1}
                />
                <Line
                  type="monotone"
                  dataKey="predicted_sessions"
                  stroke="#00F0FF"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: "#00F0FF" }}
                  name="Predicted Sessions"
                />
              </ComposedChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};

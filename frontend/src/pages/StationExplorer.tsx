import React, { useEffect, useState } from "react";
import { Filter, Zap, MapPin, CheckCircle, ChevronRight } from "lucide-react";
import { api } from "../services/api";
import { Station } from "../types";

export const StationExplorer: React.FC = () => {
  const [stations, setStations] = useState<Station[]>([]);
  const [filterType, setFilterType] = useState<string>("");
  const [filterRegion, setFilterRegion] = useState<string>("");
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);

  useEffect(() => {
    async function load() {
      const res = await api.getStations({
        station_type: filterType || undefined,
        region: filterRegion || undefined,
      });
      setStations(res.stations);
      if (res.stations.length > 0 && !selectedStation) {
        setSelectedStation(res.stations[0]);
      }
    }
    load();
  }, [filterType, filterRegion]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-orbitron font-bold text-slate-100">
            Station Explorer & Spatial Network
          </h1>
          <p className="text-sm text-slate-400">
            Geographic directory, connector profiles, and port concurrency telemetry.
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-3">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-sm rounded-lg px-3 py-2 font-mono"
          >
            <option value="">All Charger Types</option>
            <option value="L1">Level 1 (Slow)</option>
            <option value="L2">Level 2 (Commercial)</option>
            <option value="DC_Fast">DC Fast (Ultra)</option>
          </select>

          <select
            value={filterRegion}
            onChange={(e) => setFilterRegion(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-sm rounded-lg px-3 py-2 font-mono"
          >
            <option value="">All Regions</option>
            <option value="East">East</option>
            <option value="Midwest">Midwest</option>
            <option value="Mountain">Mountain</option>
            <option value="West">West</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* List Table */}
        <div className="lg:col-span-2 glass-panel rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase">
              Stations ({stations.length})
            </span>
          </div>

          <div className="divide-y divide-slate-800/60 max-h-[600px] overflow-y-auto">
            {stations.map((st) => {
              const isSelected = selectedStation?.station_id === st.station_id;
              return (
                <div
                  key={st.station_id}
                  onClick={() => setSelectedStation(st)}
                  className={`p-4 flex items-center justify-between cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-cyan-950/30 border-l-4 border-cyan-400"
                      : "hover:bg-slate-900/40"
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-slate-200">
                        {st.station_id}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {st.station_type}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-800/60">
                        {st.location_type}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 font-mono">
                      {st.region} • {st.num_ports} Ports • {st.power_kw} kW
                    </div>
                  </div>

                  <div className="text-right space-y-1">
                    <div className="text-xs font-mono font-semibold text-slate-300">
                      {((st.mean_utilization ?? 0) * 100).toFixed(1)}% util
                    </div>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                        st.utilization_class === "High"
                          ? "bg-rose-950/60 text-rose-400 border border-rose-800/60"
                          : st.utilization_class === "Medium"
                          ? "bg-amber-950/60 text-amber-400 border border-amber-800/60"
                          : "bg-emerald-950/60 text-emerald-400 border border-emerald-800/60"
                      }`}
                    >
                      {st.utilization_class ?? "Low"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Detail Panel */}
        <div className="glass-panel p-6 rounded-xl space-y-6">
          {selectedStation ? (
            <>
              <div>
                <span className="text-xs font-mono text-cyan-400">Station Detail</span>
                <h2 className="text-2xl font-orbitron font-bold text-slate-100">
                  {selectedStation.station_id}
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-0.5">
                  Lat: {selectedStation.latitude}° • Lon: {selectedStation.longitude}°
                </p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-sm py-2 border-b border-slate-800">
                  <span className="text-slate-400">Power Rating</span>
                  <span className="font-mono font-semibold text-cyan-400">
                    {selectedStation.power_kw} kW
                  </span>
                </div>
                <div className="flex justify-between text-sm py-2 border-b border-slate-800">
                  <span className="text-slate-400">Charging Ports</span>
                  <span className="font-mono font-semibold text-slate-200">
                    {selectedStation.num_ports} Ports
                  </span>
                </div>
                <div className="flex justify-between text-sm py-2 border-b border-slate-800">
                  <span className="text-slate-400">Connector Interface</span>
                  <span className="font-mono font-semibold text-slate-200">
                    {selectedStation.connector_type ?? "CCS / J1772"}
                  </span>
                </div>
                <div className="flex justify-between text-sm py-2 border-b border-slate-800">
                  <span className="text-slate-400">Average Daily Sessions</span>
                  <span className="font-mono font-semibold text-slate-200">
                    {((selectedStation.mean_sessions ?? 0) * 24).toFixed(1)} sessions/day
                  </span>
                </div>
                <div className="flex justify-between text-sm py-2 border-b border-slate-800">
                  <span className="text-slate-400">Classification Tier</span>
                  <span className="font-mono font-semibold text-lime-400">
                    {selectedStation.utilization_class ?? "Low"} Utilization
                  </span>
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-400 space-y-1">
                <div className="font-semibold text-slate-300">Port Capacity Metric</div>
                <p className="text-[11px] leading-relaxed">
                  Utilization is calculated hourly as sessions divided by available hardware ports,
                  benchmarked against regional cohorts.
                </p>
              </div>
            </>
          ) : (
            <div className="text-slate-500 font-mono text-sm">Select a station to view details.</div>
          )}
        </div>
      </div>
    </div>
  );
};

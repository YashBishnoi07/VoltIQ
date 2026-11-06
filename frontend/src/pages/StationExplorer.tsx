import React, { useEffect, useState } from "react";
import { Filter, Zap, MapPin, Search } from "lucide-react";
import { api } from "../services/api";
import { Station } from "../types";

export const StationExplorer: React.FC = () => {
  const [stations, setStations] = useState<Station[]>([]);
  const [filterType, setFilterType] = useState<string>("");
  const [filterRegion, setFilterRegion] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await api.getStations({
          station_type: filterType || undefined,
          region: filterRegion || undefined,
        });
        setStations(res.stations || []);
        if (res.stations && res.stations.length > 0) {
          setSelectedStation((prev) =>
            prev && res.stations.some((s) => s.station_id === prev.station_id)
              ? prev
              : res.stations[0]
          );
        } else {
          setSelectedStation(null);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [filterType, filterRegion]);

  const filteredStations = stations.filter((st) =>
    st.station_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    st.region.toLowerCase().includes(searchTerm.toLowerCase()) ||
    st.location_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

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

        {/* Filters & Search */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search station or region..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-lg pl-9 pr-3 py-2 font-mono focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-3 py-2 font-mono focus:outline-none"
          >
            <option value="">All Charger Types</option>
            <option value="L1">Level 1 (AC Slow)</option>
            <option value="L2">Level 2 (Commercial)</option>
            <option value="DC_Fast">DC Fast (Ultra)</option>
          </select>

          <select
            value={filterRegion}
            onChange={(e) => setFilterRegion(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-3 py-2 font-mono focus:outline-none"
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
        {/* Stations List Column */}
        <div className="lg:col-span-2 glass-panel rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase">
              Stations ({filteredStations.length} of {stations.length})
            </span>
            <span className="text-xs text-slate-500 font-mono">
              Click any station to inspect hardware telemetry
            </span>
          </div>

          <div className="divide-y divide-slate-800/60 max-h-[620px] overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-cyan-400 font-mono text-xs animate-pulse">
                Loading station directory...
              </div>
            ) : filteredStations.length === 0 ? (
              <div className="p-8 text-center text-slate-500 font-mono text-xs">
                No stations match the selected filters.
              </div>
            ) : (
              filteredStations.map((st) => {
                const isSelected = selectedStation?.station_id === st.station_id;
                return (
                  <div
                    key={st.station_id}
                    onClick={() => setSelectedStation(st)}
                    className={`p-4 flex items-center justify-between cursor-pointer transition-all ${
                      isSelected
                        ? "bg-cyan-950/40 border-l-4 border-cyan-400 shadow-inner"
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
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
                          {st.location_type}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 font-mono">
                        {st.region} • {st.num_ports} Ports • {st.power_kw} kW
                      </div>
                    </div>

                    <div className="text-right space-y-1">
                      <div className="text-xs font-mono font-semibold text-slate-200">
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
              })
            )}
          </div>
        </div>

        {/* Station Detail Drawer */}
        <div className="glass-panel p-6 rounded-xl space-y-6 flex flex-col justify-between">
          {selectedStation ? (
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-cyan-400 font-semibold tracking-wider uppercase">
                    Station Telemetry
                  </span>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      selectedStation.utilization_class === "High"
                        ? "bg-rose-950/60 text-rose-400 border border-rose-800/60"
                        : selectedStation.utilization_class === "Medium"
                        ? "bg-amber-950/60 text-amber-400 border border-amber-800/60"
                        : "bg-emerald-950/60 text-emerald-400 border border-emerald-800/60"
                    }`}
                  >
                    {selectedStation.utilization_class ?? "Low"} Utilization
                  </span>
                </div>
                <h2 className="text-2xl font-orbitron font-bold text-slate-100 mt-1">
                  {selectedStation.station_id}
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-0.5 flex items-center space-x-1">
                  <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <span>
                    {selectedStation.region} Region • ({selectedStation.latitude.toFixed(4)}°, {selectedStation.longitude.toFixed(4)}°)
                  </span>
                </p>
              </div>

              {/* Hardware Specifications */}
              <div className="space-y-3">
                <div className="flex justify-between text-xs py-2 border-b border-slate-800/80">
                  <span className="text-slate-400 font-mono">Charger Rating</span>
                  <span className="font-mono font-bold text-cyan-400">
                    {selectedStation.power_kw} kW Max Output
                  </span>
                </div>
                <div className="flex justify-between text-xs py-2 border-b border-slate-800/80">
                  <span className="text-slate-400 font-mono">Physical Ports</span>
                  <span className="font-mono font-semibold text-slate-200">
                    {selectedStation.num_ports} Concurrent Plugs
                  </span>
                </div>
                <div className="flex justify-between text-xs py-2 border-b border-slate-800/80">
                  <span className="text-slate-400 font-mono">Connector Interface</span>
                  <span className="font-mono font-semibold text-slate-200">
                    {selectedStation.connector_type || "CCS / J1772"}
                  </span>
                </div>
                <div className="flex justify-between text-xs py-2 border-b border-slate-800/80">
                  <span className="text-slate-400 font-mono">Density Tier</span>
                  <span className="font-mono capitalize text-slate-200">
                    {selectedStation.location_type} Setting
                  </span>
                </div>
                <div className="flex justify-between text-xs py-2 border-b border-slate-800/80">
                  <span className="text-slate-400 font-mono">Mean Hourly Demand</span>
                  <span className="font-mono font-semibold text-slate-200">
                    {(selectedStation.mean_sessions ?? 0).toFixed(2)} sessions/hr
                  </span>
                </div>
                <div className="flex justify-between text-xs py-2 border-b border-slate-800/80">
                  <span className="text-slate-400 font-mono">Daily Throughput</span>
                  <span className="font-mono font-semibold text-slate-200">
                    {((selectedStation.mean_sessions ?? 0) * 24).toFixed(0)} sessions/day
                  </span>
                </div>
                <div className="flex justify-between text-xs py-2 border-b border-slate-800/80">
                  <span className="text-slate-400 font-mono">Mean Energy Delivered</span>
                  <span className="font-mono font-semibold text-lime-400">
                    {(selectedStation.mean_energy ?? 0).toFixed(1)} kWh/session
                  </span>
                </div>
              </div>

              {/* Port Visualization */}
              <div className="space-y-2">
                <span className="text-xs font-mono text-slate-400">
                  Physical Bay Status ({selectedStation.num_ports} bays)
                </span>
                <div className="grid grid-cols-4 gap-2">
                  {Array.from({ length: selectedStation.num_ports }).map((_, idx) => (
                    <div
                      key={idx}
                      className="p-2 rounded bg-slate-900 border border-cyan-800/40 text-center font-mono text-[10px] text-cyan-300 flex flex-col items-center space-y-1"
                    >
                      <Zap className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Bay #{idx + 1}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500 font-mono text-xs">
              <MapPin className="w-8 h-8 text-slate-700 mb-2" />
              <span>Select any station on the left to inspect hardware details</span>
            </div>
          )}

          <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 leading-relaxed font-mono">
            * Capacity metric calculated as average concurrency against maximum bay capacity.
          </div>
        </div>
      </div>
    </div>
  );
};

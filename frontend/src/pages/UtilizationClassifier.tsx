import React, { useState } from "react";
import { Cpu, ShieldCheck, Zap } from "lucide-react";
import { api } from "../services/api";
import { UtilizationPrediction } from "../types";

export const UtilizationClassifier: React.FC = () => {
  const [stationType, setStationType] = useState("DC_Fast");
  const [locationType, setLocationType] = useState("urban");
  const [powerKw, setPowerKw] = useState(120);
  const [numPorts, setNumPorts] = useState(6);
  const [meanSessions, setMeanSessions] = useState(3.5);
  const [stdSessions, setStdSessions] = useState(1.2);
  const [meanEnergy, setMeanEnergy] = useState(42.5);
  const [meanUtil, setMeanUtil] = useState(0.55);

  const [result, setResult] = useState<UtilizationPrediction | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.predictUtilization({
        station_type: stationType,
        location_type: locationType,
        power_kw: powerKw,
        num_ports: numPorts,
        mean_sessions: meanSessions,
        std_sessions: stdSessions,
        mean_energy: meanEnergy,
        mean_utilization: meanUtil,
      });
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-orbitron font-bold text-slate-100">
          Station Utilization Classifier
        </h1>
        <p className="text-sm text-slate-400">
          Predict Low / Medium / High network concurrency with multiclass probability distribution.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-xl space-y-4">
          <h3 className="font-orbitron font-semibold text-slate-200 flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>Station Specification</span>
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Station Type
              </label>
              <select
                value={stationType}
                onChange={(e) => setStationType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 font-mono"
              >
                <option value="L1">Level 1 (AC 1.4-1.9 kW)</option>
                <option value="L2">Level 2 (AC 6.2-11.5 kW)</option>
                <option value="DC_Fast">DC Fast (DC 50-150 kW)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Location Setting
              </label>
              <select
                value={locationType}
                onChange={(e) => setLocationType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 font-mono"
              >
                <option value="urban">Urban Dense</option>
                <option value="suburban">Suburban Transit</option>
                <option value="highway">Highway Corridor</option>
                <option value="rural">Rural Remote</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Power Output (kW): {powerKw}
              </label>
              <input
                type="range"
                min={1}
                max={250}
                value={powerKw}
                onChange={(e) => setPowerKw(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Port Concurrency: {numPorts}
              </label>
              <input
                type="range"
                min={1}
                max={16}
                value={numPorts}
                onChange={(e) => setNumPorts(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Mean Sessions/Hr: {meanSessions.toFixed(1)}
              </label>
              <input
                type="range"
                min={0}
                max={10}
                step={0.1}
                value={meanSessions}
                onChange={(e) => setMeanSessions(Number(e.target.value))}
                className="w-full accent-lime-400"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Std Demand Dev: {stdSessions.toFixed(1)}
              </label>
              <input
                type="range"
                min={0}
                max={5}
                step={0.1}
                value={stdSessions}
                onChange={(e) => setStdSessions(Number(e.target.value))}
                className="w-full accent-lime-400"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-semibold text-sm transition-all shadow-lg shadow-cyan-500/20 font-orbitron"
          >
            {loading ? "Evaluating Network..." : "Predict Utilization Category"}
          </button>
        </form>

        {/* Results Card */}
        <div className="glass-panel p-6 rounded-xl flex flex-col justify-between space-y-6">
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              Classifier Output
            </span>
            <h3 className="font-orbitron font-semibold text-slate-200 mt-1">
              Station Classification Result
            </h3>
          </div>

          {result ? (
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div
                  className={`text-4xl font-orbitron font-black px-4 py-2 rounded-xl border ${
                    result.predicted_class === "High"
                      ? "text-rose-400 bg-rose-950/40 border-rose-800"
                      : result.predicted_class === "Medium"
                      ? "text-amber-400 bg-amber-950/40 border-amber-800"
                      : "text-emerald-400 bg-emerald-950/40 border-emerald-800"
                  }`}
                >
                  {result.predicted_class}
                </div>
                <div>
                  <div className="text-xs text-slate-400 font-mono">Confidence Level</div>
                  <div className="text-xl font-bold font-mono text-slate-100">
                    {(result.confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    Model: {result.model_used}
                  </div>
                </div>
              </div>

              {/* Probabilities Bars */}
              <div className="space-y-2">
                <span className="text-xs font-mono text-slate-400">Class Probabilities</span>
                {Object.entries(result.probabilities).map(([cls, prob]) => (
                  <div key={cls} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-300">{cls}</span>
                      <span className="text-cyan-400">{(prob * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-500 to-lime-400 rounded-full transition-all duration-500"
                        style={{ width: `${prob * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-400 space-y-1">
                <div className="font-semibold text-slate-300 flex items-center space-x-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Ethics & Policy Notice</span>
                </div>
                <p className="text-[11px] leading-relaxed">{result.ethics_notice}</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500 space-y-2 font-mono text-xs">
              <Zap className="w-8 h-8 text-slate-700" />
              <span>Configure station parameters and run prediction</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

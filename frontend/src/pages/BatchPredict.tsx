import React, { useState } from "react";
import { FileSpreadsheet, Upload, Download, CheckCircle } from "lucide-react";

export const BatchPredict: React.FC = () => {
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [rowCount, setRowCount] = useState<number | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setDownloadUrl(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/predict/batch-csv`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Failed to process batch predictions.");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);

      const text = await blob.text();
      const lines = text.trim().split("\n");
      setRowCount(Math.max(lines.length - 1, 0));
    } catch (err) {
      console.error(err);
      alert("Error scoring CSV. Please check formatting.");
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadSample = () => {
    const sampleCsv = `station_id,station_type,location_type,power_kw,num_ports,mean_sessions,std_sessions,mean_energy,mean_utilization
TEST-001,DC_Fast,urban,100,4,3.2,1.1,45.0,0.65
TEST-002,L2,suburban,11.5,8,1.4,0.5,18.0,0.25
TEST-003,L1,rural,1.9,2,0.6,0.2,8.0,0.15
TEST-004,DC_Fast,highway,150,6,4.5,1.8,60.0,0.80`;

    const blob = new Blob([sampleCsv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "voltiq_sample_stations.csv";
    a.click();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-orbitron font-bold text-slate-100 flex items-center space-x-2">
          <FileSpreadsheet className="w-6 h-6 text-cyan-400" />
          <span>Batch Inference Engine</span>
        </h1>
        <p className="text-sm text-slate-400">
          Upload bulk station metadata CSV files to generate concurrent demand classifications.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload form */}
        <form onSubmit={handleUpload} className="glass-panel p-6 rounded-xl space-y-4">
          <h3 className="font-orbitron font-semibold text-slate-200">
            Upload Station CSV
          </h3>
          <p className="text-xs text-slate-400">
            Accepts standard CSV with station attributes. Download our starter template if needed.
          </p>

          <div className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-xl p-8 text-center transition-colors">
            <Upload className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-cyan-950 file:text-cyan-400 hover:file:bg-cyan-900"
            />
            {file && (
              <div className="mt-2 text-xs font-mono text-cyan-400">
                Selected: {file.name}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3 pt-2">
            <button
              type="submit"
              disabled={!file || uploading}
              className="flex-1 py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-black font-semibold text-sm disabled:opacity-50 font-orbitron shadow-lg shadow-cyan-500/20"
            >
              {uploading ? "Scoring CSV File..." : "Run Batch Scoring"}
            </button>
            <button
              type="button"
              onClick={handleDownloadSample}
              className="py-2.5 px-4 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-400 text-sm font-mono"
            >
              Get Template
            </button>
          </div>
        </form>

        {/* Results Box */}
        <div className="glass-panel p-6 rounded-xl flex flex-col justify-between space-y-4">
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase">
              Pipeline Status
            </span>
            <h3 className="font-orbitron font-semibold text-slate-200 mt-1">
              Scored Output Ready
            </h3>
          </div>

          {downloadUrl ? (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-emerald-950/30 border border-emerald-800/60 text-xs text-emerald-300 flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
                <div>
                  <div className="font-bold">Scoring Completed Successfully</div>
                  <div className="text-[11px] text-emerald-400/80 font-mono">
                    {rowCount} rows scored with confidence & class probabilities
                  </div>
                </div>
              </div>

              <a
                href={downloadUrl}
                download="voltiq_scored_predictions.csv"
                className="w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg bg-cyan-400 hover:bg-cyan-300 text-black font-bold font-orbitron text-sm transition-colors shadow-lg shadow-cyan-400/20"
              >
                <Download className="w-4 h-4" />
                <span>Download Enriched CSV</span>
              </a>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500 space-y-2 font-mono text-xs">
              <FileSpreadsheet className="w-8 h-8 text-slate-700" />
              <span>Scored dataset download link will appear here</span>
            </div>
          )}

          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 font-mono">
            Output includes: predicted_utilization_class, confidence, prob_Low, prob_Medium, prob_High
          </div>
        </div>
      </div>
    </div>
  );
};

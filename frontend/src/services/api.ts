import {
  DemandForecastResponse,
  HeatmapCell,
  HourlyDemandPoint,
  ModelComparisonResponse,
  OverviewMetrics,
  StatTestResult,
  Station,
  UtilizationPrediction,
} from "../types";

const API_BASE = "http://localhost:8000";

export const api = {
  async getOverview(): Promise<OverviewMetrics> {
    const res = await fetch(`${API_BASE}/analytics/overview`);
    return res.json();
  },

  async getStations(params?: {
    station_type?: string;
    region?: string;
    utilization_class?: string;
  }): Promise<{ stations: Station[]; total: number }> {
    const cleanParams: Record<string, string> = {};
    if (params) {
      for (const [key, val] of Object.entries(params)) {
        if (val) cleanParams[key] = val;
      }
    }
    const query = new URLSearchParams(cleanParams).toString();
    const url = query ? `${API_BASE}/stations?${query}` : `${API_BASE}/stations`;
    const res = await fetch(url);
    return res.json();
  },

  async getHourlyDemand(): Promise<{ data: HourlyDemandPoint[] }> {
    const res = await fetch(`${API_BASE}/analytics/hourly`);
    return res.json();
  },

  async getHeatmap(): Promise<{ data: HeatmapCell[] }> {
    const res = await fetch(`${API_BASE}/analytics/heatmap`);
    return res.json();
  },

  async getStats(): Promise<StatTestResult[]> {
    const res = await fetch(`${API_BASE}/analytics/stats`);
    return res.json();
  },

  async predictDemand(
    station_id: string,
    horizon_hours: number = 24
  ): Promise<DemandForecastResponse> {
    const res = await fetch(`${API_BASE}/predict/demand`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ station_id, horizon_hours }),
    });
    return res.json();
  },

  async predictUtilization(features: {
    station_type: string;
    location_type: string;
    power_kw: number;
    num_ports: number;
    mean_sessions: number;
    std_sessions: number;
    mean_energy: number;
    mean_utilization: number;
  }): Promise<UtilizationPrediction> {
    const res = await fetch(`${API_BASE}/predict/utilization`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(features),
    });
    return res.json();
  },

  async getModelComparison(): Promise<ModelComparisonResponse> {
    const res = await fetch(`${API_BASE}/models/comparison`);
    return res.json();
  },

  async getUnderserved(): Promise<{ stations: Station[]; total: number; recommendation: string }> {
    const res = await fetch(`${API_BASE}/insights/underserved`);
    return res.json();
  },

  async getFairness(): Promise<{
    disparity_analysis: Record<string, any>;
    ethical_framework: string;
    disclaimer: string;
  }> {
    const res = await fetch(`${API_BASE}/insights/fairness`);
    return res.json();
  },
};

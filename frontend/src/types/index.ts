export interface Station {
  station_id: str;
  station_type: string;
  location_type: string;
  connector_type?: string;
  power_kw: number;
  latitude: number;
  longitude: number;
  num_ports: number;
  region: string;
  mean_utilization?: number;
  utilization_class?: "Low" | "Medium" | "High";
  mean_sessions?: number;
  total_sessions?: number;
  mean_energy?: number;
}

type str = string;

export interface OverviewMetrics {
  total_sessions: number;
  total_kwh: number;
  avg_utilization: number;
  peak_hour: number;
  total_stations: number;
  high_util_stations: number;
  low_util_stations: number;
}

export interface HourlyDemandPoint {
  hour: number;
  avg_sessions: number;
  weekday_avg: number;
  weekend_avg: number;
}

export interface HeatmapCell {
  hour: number;
  day_of_week: number;
  avg_sessions: number;
}

export interface ForecastPoint {
  datetime: string;
  predicted_sessions: number;
  lower_bound: number;
  upper_bound: number;
  is_peak: boolean;
}

export interface DemandForecastResponse {
  station_id: string;
  horizon_hours: number;
  forecast: ForecastPoint[];
  model_used: string;
  uncertainty_note: string;
}

export interface UtilizationPrediction {
  predicted_class: "Low" | "Medium" | "High";
  probabilities: Record<string, number>;
  confidence: number;
  model_used: string;
  ethics_notice: string;
}

export interface RegressionModelResult {
  model: string;
  mae: number;
  rmse: number;
  mape: number;
  r2: number;
  feature_count?: number;
}

export interface ClassificationModelResult {
  model: string;
  accuracy: number;
  f1_macro: number;
  roc_auc?: number;
  confusion_matrix: number[][];
  class_labels: string[];
}

export interface ModelComparisonResponse {
  regression_leaderboard: RegressionModelResult[];
  classification_leaderboard: ClassificationModelResult[];
  best_regression_model: string;
  best_classification_model: string;
  shap_importance: { feature: string; importance: number }[];
}

export interface StatTestResult {
  test_name: string;
  statistic: number;
  p_value: number;
  significant: boolean;
  interpretation: string;
}

import React, { useState } from "react";
import { Navbar } from "./components/layout/Navbar";
import { Sidebar, PageId } from "./components/layout/Sidebar";
import { Overview } from "./pages/Overview";
import { DemandForecast } from "./pages/DemandForecast";
import { StationExplorer } from "./pages/StationExplorer";
import { UtilizationClassifier } from "./pages/UtilizationClassifier";
import { AnalyticsLab } from "./pages/AnalyticsLab";
import { ModelArena } from "./pages/ModelArena";
import { Insights } from "./pages/Insights";
import { BatchPredict } from "./pages/BatchPredict";

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<PageId>("overview");
  const [darkMode, setDarkMode] = useState(true);

  const renderPage = () => {
    switch (currentPage) {
      case "overview":
        return <Overview />;
      case "demand":
        return <DemandForecast />;
      case "explorer":
        return <StationExplorer />;
      case "classifier":
        return <UtilizationClassifier />;
      case "analytics":
        return <AnalyticsLab />;
      case "arena":
        return <ModelArena />;
      case "insights":
        return <Insights />;
      case "batch":
        return <BatchPredict />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className={`min-h-screen ${darkMode ? "dark bg-[#080B10]" : "bg-slate-950"} text-slate-100 flex flex-col`}>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

      <div className="flex flex-1">
        <Sidebar currentPage={currentPage} onSelectPage={setCurrentPage} />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

export default App;

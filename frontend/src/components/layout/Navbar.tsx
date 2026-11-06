import React from "react";
import { Zap, Moon, Sun, Activity } from "lucide-react";

interface NavbarProps {
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ darkMode, setDarkMode }) => {
  return (
    <header className="sticky top-0 z-50 h-16 border-b border-slate-800 bg-[#080B10]/80 backdrop-blur-md px-6 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-lime-400 p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <div className="w-full h-full bg-[#080B10] rounded-[7px] flex items-center justify-center">
            <Zap className="w-5 h-5 text-cyan-400 fill-cyan-400/20" />
          </div>
        </div>
        <div>
          <span className="font-orbitron font-extrabold text-xl tracking-wider bg-gradient-to-r from-cyan-400 via-sky-300 to-lime-300 bg-clip-text text-transparent">
            VOLTIQ
          </span>
          <span className="ml-2 text-xs font-mono text-cyan-400/80 bg-cyan-950/60 border border-cyan-800/60 px-1.5 py-0.5 rounded">
            v0.1.0-ML
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Engine: Ridge + XGBoost</span>
        </div>

        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-400 hover:border-cyan-500/40 transition-colors"
          title="Toggle Theme"
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
};

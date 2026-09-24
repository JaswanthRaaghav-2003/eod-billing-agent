import React from 'react';
import { 
  Calculator, 
  BarChart3, 
  MessageSquareCode, 
  UploadCloud, 
  Settings, 
  Calendar, 
  Activity, 
  AlertCircle,
  FileCheck2,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { DaySummary } from '../types';

interface LayoutProps {
  currentTab: 'reconciliation' | 'analytics' | 'narrative';
  setCurrentTab: (tab: 'reconciliation' | 'analytics' | 'narrative') => void;
  selectedDate: string;
  setSelectedDate: (date: string) => void;
  availableDays: DaySummary[];
  onOpenUpload: () => void;
  onOpenSettings: () => void;
  onResetData: () => void;
  clinicName: string;
  hasValidationError?: boolean;
  onViewValidationErrors?: () => void;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({
  currentTab,
  setCurrentTab,
  selectedDate,
  setSelectedDate,
  availableDays,
  onOpenUpload,
  onOpenSettings,
  onResetData,
  clinicName,
  hasValidationError,
  onViewValidationErrors,
  children
}) => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100 font-sans">
      {/* Shared Persistent Sidebar */}
      <aside className="w-16 md:w-20 bg-white border-r border-slate-200/90 flex flex-col items-center py-5 justify-between shrink-0 shadow-sm z-20">
        <div className="flex flex-col items-center gap-7 w-full">
          {/* Clinic Brand Emblem */}
          <div 
            className="w-10 h-10 md:w-11 md:h-11 rounded-full bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-teal-500/20 cursor-pointer hover:scale-105 transition-all"
            title="SwasthiQ Kaagazy Agent"
          >
            <Activity className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col items-center gap-3 w-full px-2">
            {/* Screen 1: Reconciliation */}
            <button
              onClick={() => setCurrentTab('reconciliation')}
              className={`w-11 h-11 md:w-12 md:h-12 rounded-2xl flex items-center justify-center transition-all ${
                currentTab === 'reconciliation'
                  ? 'bg-slate-900 text-white shadow-md shadow-slate-900/20 scale-100'
                  : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
              }`}
              title="1. EOD Reconciliation Dashboard"
            >
              <Calculator className="w-5 h-5" />
            </button>

            {/* Screen 2: Analytics */}
            <button
              onClick={() => setCurrentTab('analytics')}
              className={`w-11 h-11 md:w-12 md:h-12 rounded-2xl flex items-center justify-center transition-all ${
                currentTab === 'analytics'
                  ? 'bg-slate-900 text-white shadow-md shadow-slate-900/20 scale-100'
                  : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
              }`}
              title="2. Analytics & Hourly Insights"
            >
              <BarChart3 className="w-5 h-5" />
            </button>

            {/* Screen 3: AI Narrative Summary */}
            <button
              onClick={() => setCurrentTab('narrative')}
              className={`w-11 h-11 md:w-12 md:h-12 rounded-2xl flex items-center justify-center transition-all relative ${
                currentTab === 'narrative'
                  ? 'bg-slate-900 text-white shadow-md shadow-slate-900/20 scale-100'
                  : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
              }`}
              title="3. AI Narrative Summary & Traced Figures"
            >
              <MessageSquareCode className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-indigo-500 rounded-full ring-2 ring-white"></span>
            </button>

            <div className="w-8 h-[1px] bg-slate-200 my-1"></div>

            {/* Ingestion Upload */}
            <button
              onClick={onOpenUpload}
              className="w-11 h-11 md:w-12 md:h-12 rounded-2xl flex items-center justify-center text-slate-500 hover:text-teal-600 hover:bg-teal-50 transition-all"
              title="Upload New Billing Log"
            >
              <UploadCloud className="w-5 h-5" />
            </button>
          </nav>
        </div>

        {/* Bottom Actions */}
        <div className="flex flex-col items-center gap-3">
          <button
            onClick={onResetData}
            className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all"
            title="Reload Sample Datasets"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={onOpenSettings}
            className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all"
            title="AI & Agent Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header Bar */}
        <header className="bg-white/80 backdrop-blur-md sticky top-0 z-10 border-b border-slate-200/80 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold tracking-wide uppercase bg-teal-50 text-teal-700 border border-teal-200/60">
                  Clinic EOD Portal
                </span>
                <span className="text-slate-300">?</span>
                <span className="text-xs text-slate-500 font-mono">CLN-KNP-014</span>
              </div>
              <h2 className="text-sm font-semibold text-slate-800 tracking-tight mt-0.5">
                {clinicName}
              </h2>
            </div>
          </div>

          {/* Quick Date Switcher Pills */}
          <div className="flex items-center gap-2">
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80">
              <button
                onClick={() => setSelectedDate('2026-07-27')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedDate === '2026-07-27'
                    ? 'bg-white text-slate-900 shadow-sm font-semibold'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                27 Jul <span className="text-[10px] text-teal-600 font-bold ml-1">18 Visits</span>
              </button>

              <button
                onClick={() => setSelectedDate('2026-07-25')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedDate === '2026-07-25'
                    ? 'bg-white text-slate-900 shadow-sm font-semibold'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                25 Jul <span className="text-[10px] text-amber-600 font-bold ml-1">Refunds</span>
              </button>

              <button
                onClick={() => setSelectedDate('2026-07-26')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedDate === '2026-07-26'
                    ? 'bg-white text-slate-900 shadow-sm font-semibold'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                26 Jul <span className="text-[10px] text-slate-400 font-bold ml-1">Closed</span>
              </button>
            </div>

            <button
              onClick={onOpenUpload}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-teal-700 bg-teal-50 hover:bg-teal-100 border border-teal-200 rounded-xl transition-all"
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Upload Log</span>
            </button>
          </div>
        </header>

        {/* Actionable Error Banner if malformed row was rejected (e.g. visit 19) */}
        {hasValidationError && selectedDate === '2026-07-27' && (
          <div className="bg-amber-50 border-b border-amber-200 px-6 py-2.5 flex items-center justify-between text-xs text-amber-900">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                <strong>Edge Case Handled:</strong> 1 malformed row rejected in 2026-07-27 dataset (Visit <code>V-20260727-019</code>: missing <code>payment_mode</code>). 18 valid visits processed deterministically.
              </span>
            </div>
            {onViewValidationErrors && (
              <button
                onClick={onViewValidationErrors}
                className="underline hover:text-amber-950 font-semibold ml-4 shrink-0"
              >
                Inspect Error Details
              </button>
            )}
          </div>
        )}

        {/* Screen View Container */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  );
};

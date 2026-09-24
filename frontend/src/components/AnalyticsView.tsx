import React, { useState } from 'react';
import { AnalyticsReport } from '../types';
import { TrendingUp, AlertCircle, Sparkles } from 'lucide-react';

interface AnalyticsViewProps {
  report: AnalyticsReport | null;
  loading: boolean;
  error?: string | null;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({
  report,
  loading,
  error
}) => {
  const [hoveredHour, setHoveredHour] = useState<number | null>(null);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center max-w-lg mx-auto mt-10">
        <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
        <h3 className="text-red-800 font-semibold text-base">Failed to load analytics</h3>
        <p className="text-red-600 text-sm mt-1">{error || 'No analytics data available'}</p>
      </div>
    );
  }

  // Calculate highest revenue for bar scaling
  const maxRevenue = Math.max(...report.revenue_by_hour.map((h) => h.revenue_paise), 1);

  return (
    <div className="space-y-7 animate-in fade-in duration-300">
      {/* Title Header Matching Screen 2 */}
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900">
          Analytics
        </h1>
        <p className="text-sm text-slate-500 mt-1 font-medium">
          {report.clinic_name} ? {report.formatted_date}
        </p>
      </div>

      {/* Main Chart Card: Revenue by Hour of Day */}
      <div className="bg-white rounded-2xl p-6 md:p-8 border border-slate-200/80 shadow-xs relative">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-base font-bold text-slate-900 tracking-tight">
            Revenue by Hour of Day
          </h2>
          <span className="text-xs text-slate-400 font-medium">Peak transaction window</span>
        </div>

        {/* Empty state check */}
        {report.revenue_by_hour.length === 0 || maxRevenue <= 1 ? (
          <div className="py-16 text-center text-slate-400 text-sm">
            No hourly revenue transactions logged for this date.
          </div>
        ) : (
          <div className="relative pt-12 pb-2">
            {/* Bars Container */}
            <div className="flex items-end justify-between gap-2 md:gap-4 h-56 px-2 border-b border-slate-100">
              {report.revenue_by_hour.map((item) => {
                const heightPct = Math.max((item.revenue_paise / maxRevenue) * 100, 3);
                const isPeak = item.is_peak;
                const isHovered = hoveredHour === item.hour;

                return (
                  <div
                    key={item.hour}
                    className="flex-1 flex flex-col items-center h-full justify-end relative group cursor-pointer"
                    onMouseEnter={() => setHoveredHour(item.hour)}
                    onMouseLeave={() => setHoveredHour(null)}
                  >
                    {/* Peak Callout Bubble (Matching Screen 2 Mockup!) */}
                    {isPeak && (
                      <div className="absolute -top-12 z-20 flex flex-col items-center pointer-events-none animate-bounce-subtle">
                        <div className="bg-slate-900 text-white text-[11px] font-semibold py-1 px-3 rounded-lg shadow-md whitespace-nowrap tracking-wide">
                          {report.peak_hour?.callout_text || `Peak: ${item.hour_range} ? ${item.revenue_formatted}`}
                        </div>
                        <div className="w-2 h-2 bg-slate-900 rotate-45 -mt-1"></div>
                      </div>
                    )}

                    {/* Interactive Tooltip for Non-Peak or on Hover */}
                    {isHovered && !isPeak && (
                      <div className="absolute -top-10 z-20 flex flex-col items-center pointer-events-none">
                        <div className="bg-slate-800 text-white text-[10px] py-1 px-2.5 rounded shadow whitespace-nowrap">
                          {item.hour_range}: {item.revenue_formatted} ({item.visit_count} visits)
                        </div>
                        <div className="w-1.5 h-1.5 bg-slate-800 rotate-45 -mt-1"></div>
                      </div>
                    )}

                    {/* The Bar */}
                    <div
                      className={`w-full max-w-[46px] rounded-t-lg transition-all duration-300 ${
                        isPeak
                          ? 'bg-blue-600 shadow-md shadow-blue-500/20'
                          : isHovered
                          ? 'bg-blue-400'
                          : 'bg-blue-100 hover:bg-blue-200'
                      }`}
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                );
              })}
            </div>

            {/* X-Axis Hour Labels */}
            <div className="flex justify-between gap-2 md:gap-4 mt-3 px-2 text-center">
              {report.revenue_by_hour.map((item) => (
                <div
                  key={item.hour}
                  className={`flex-1 text-[11px] font-medium transition-colors ${
                    item.is_peak ? 'text-blue-700 font-bold' : 'text-slate-400'
                  }`}
                >
                  {item.hour_label}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Two Distinct Side-by-Side Ranking Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Card: Top Medicines ? by Quantity */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900 tracking-tight">
              Top Medicines ? by Quantity
            </h2>
            <span className="text-[11px] text-slate-400 font-medium">Volume Movers</span>
          </div>

          {report.top_medicines_by_quantity.length === 0 ? (
            <p className="text-xs text-slate-400 py-6 text-center">No dispense records available.</p>
          ) : (
            <div className="space-y-3.5">
              {report.top_medicines_by_quantity.map((med) => (
                <div
                  key={`qty-${med.rank}-${med.drug_name}`}
                  className="flex items-center justify-between text-sm py-1 hover:bg-slate-50/70 px-2 rounded-lg transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <span className="w-5 text-xs font-bold text-slate-400 font-mono">
                      {med.rank}
                    </span>
                    <span className="font-semibold text-slate-800 tracking-tight text-xs uppercase">
                      {med.drug_name}
                    </span>
                  </div>
                  <span className="font-medium text-slate-500 text-xs font-mono">
                    {med.formatted_qty}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Card: Top Medicines ? by Revenue */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900 tracking-tight">
              Top Medicines ? by Revenue
            </h2>
            <span className="text-[11px] text-slate-400 font-medium">Financial Value</span>
          </div>

          {report.top_medicines_by_revenue.length === 0 ? (
            <p className="text-xs text-slate-400 py-6 text-center">No revenue records available.</p>
          ) : (
            <div className="space-y-3.5">
              {report.top_medicines_by_revenue.map((med) => (
                <div
                  key={`rev-${med.rank}-${med.drug_name}`}
                  className="flex items-center justify-between text-sm py-1 hover:bg-slate-50/70 px-2 rounded-lg transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <span className="w-5 text-xs font-bold text-slate-400 font-mono">
                      {med.rank}
                    </span>
                    <span className="font-semibold text-slate-800 tracking-tight text-xs uppercase">
                      {med.drug_name}
                    </span>
                  </div>
                  <span className="font-semibold text-slate-900 text-xs font-mono">
                    {med.formatted_revenue}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

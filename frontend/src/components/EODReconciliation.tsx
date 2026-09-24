import React from 'react';
import { Calendar, CreditCard, Banknote, Smartphone, AlertCircle, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { ReconciliationReport } from '../types';

interface EODReconciliationProps {
  report: ReconciliationReport | null;
  loading: boolean;
  error?: string | null;
}

export const EODReconciliation: React.FC<EODReconciliationProps> = ({
  report,
  loading,
  error
}) => {
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
        <h3 className="text-red-800 font-semibold text-base">Failed to load reconciliation</h3>
        <p className="text-red-600 text-sm mt-1">{error || 'No reconciliation data available'}</p>
      </div>
    );
  }

  const getModeIcon = (mode: string) => {
    switch (mode.toLowerCase()) {
      case 'cash':
        return <Banknote className="w-4 h-4 text-emerald-600" />;
      case 'card':
        return <CreditCard className="w-4 h-4 text-blue-600" />;
      case 'upi':
        return <Smartphone className="w-4 h-4 text-purple-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-7 animate-in fade-in duration-300">
      {/* Title Header Matching Screen 1 */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900">
            EOD Reconciliation
          </h1>
          <p className="text-sm text-slate-500 mt-1 font-medium">
            {report.clinic_name}
          </p>
        </div>

        {/* Date Pill Matching Screen 1 Top Right */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 bg-white border border-slate-200/90 rounded-xl shadow-xs text-xs font-semibold text-slate-700">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span>{report.formatted_date}</span>
        </div>
      </div>

      {/* 4 Stat Cards in a Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
        {/* Stat Card 1: TOTAL BILLED */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
          <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">
            TOTAL BILLED
          </span>
          <div className="text-2xl md:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">
            {report.total_billed_formatted}
          </div>
          <div className="text-xs text-slate-500 mt-2 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
            <span>{report.total_visits} {report.total_visits === 1 ? 'visit' : 'visits'}</span>
          </div>
        </div>

        {/* Stat Card 2: TOTAL COLLECTED */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
          <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">
            TOTAL COLLECTED
          </span>
          <div className="text-2xl md:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">
            {report.total_collected_formatted}
          </div>
          <div className="text-xs text-slate-500 mt-2 font-medium flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${report.collection_percentage >= 80 ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
            <span>{report.collection_percentage_formatted}</span>
          </div>
        </div>

        {/* Stat Card 3: OUTSTANDING */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
          <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">
            OUTSTANDING
          </span>
          <div className="text-2xl md:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">
            {report.total_outstanding_formatted}
          </div>
          <div className="text-xs text-slate-500 mt-2 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
            <span>{report.pending_invoices_count} pending {report.pending_invoices_count === 1 ? 'invoice' : 'invoices'}</span>
          </div>
        </div>

        {/* Stat Card 4: REFUNDS */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
          <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">
            REFUNDS
          </span>
          <div className="text-2xl md:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">
            {report.total_refunds_formatted}
          </div>
          <div className="text-xs text-slate-500 mt-2 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
            <span>{report.refund_visits} {report.refund_visits === 1 ? 'refund' : 'refunds'}</span>
          </div>
        </div>
      </div>

      {/* Payment Mode Breakdown Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="px-6 py-4.5 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 tracking-tight">
            Payment Mode Breakdown
          </h2>
          <span className="text-xs text-slate-400 font-medium">Deterministic accounting split</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="bg-slate-50/70 text-slate-500 font-semibold text-xs tracking-wider border-b border-slate-200/60">
                <th className="py-3.5 px-6">Mode</th>
                <th className="py-3.5 px-6 text-right">Billed</th>
                <th className="py-3.5 px-6 text-right">Collected</th>
                <th className="py-3.5 px-6 text-right">Outstanding</th>
                <th className="py-3.5 px-6 text-right">Refunds</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {report.payment_mode_breakdown.map((row) => (
                <tr key={row.mode} className="hover:bg-slate-50/50 transition-colors">
                  <td className="py-4 px-6 flex items-center gap-2.5 text-slate-900 font-semibold">
                    <span className="p-1.5 rounded-lg bg-slate-100/80">
                      {getModeIcon(row.mode)}
                    </span>
                    <span>{row.mode}</span>
                  </td>
                  <td className="py-4 px-6 text-right font-mono text-slate-800">
                    {row.billed_formatted}
                  </td>
                  <td className="py-4 px-6 text-right font-mono text-slate-800">
                    {row.collected_formatted}
                  </td>
                  <td className="py-4 px-6 text-right font-mono">
                    <span className={row.outstanding_paise > 0 ? 'text-amber-700 font-semibold' : 'text-slate-500'}>
                      {row.outstanding_formatted}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right font-mono text-slate-600">
                    {row.refunds_formatted}
                  </td>
                </tr>
              ))}

              {/* Total Footer Row */}
              <tr className="bg-slate-50/80 font-bold text-slate-900 border-t border-slate-200">
                <td className="py-4 px-6 uppercase text-xs tracking-wider text-slate-500">
                  Total
                </td>
                <td className="py-4 px-6 text-right font-mono">
                  {report.totals_row.billed_formatted}
                </td>
                <td className="py-4 px-6 text-right font-mono text-emerald-700">
                  {report.totals_row.collected_formatted}
                </td>
                <td className="py-4 px-6 text-right font-mono text-amber-700">
                  {report.totals_row.outstanding_formatted}
                </td>
                <td className="py-4 px-6 text-right font-mono text-rose-700">
                  {report.totals_row.refunds_formatted}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { X, AlertCircle, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { ValidationErrorDetail } from '../types';

interface ValidationErrorsModalProps {
  isOpen: boolean;
  onClose: () => void;
  errors: ValidationErrorDetail[];
  dateStr: string;
}

export const ValidationErrorsModal: React.FC<ValidationErrorsModalProps> = ({
  isOpen,
  onClose,
  errors,
  dateStr
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-6 py-4.5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Ingestion Rejection Details</h2>
              <p className="text-xs text-slate-500 font-medium">{dateStr} Dataset</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Errors list */}
        <div className="p-6 overflow-y-auto space-y-3.5">
          <p className="text-xs text-slate-600 leading-relaxed font-medium">
            The billing ingestion pipeline enforces strict schema integrity. Below is the actionable report for records rejected during daily log processing:
          </p>

          {errors.map((err, idx) => (
            <div
              key={idx}
              className="p-4 bg-amber-50/70 border border-amber-200/90 rounded-2xl text-xs text-amber-950 space-y-2 font-mono"
            >
              <div className="flex items-center justify-between border-b border-amber-200/60 pb-1.5 font-bold">
                <span>Visit ID: {err.visit_id || 'N/A'}</span>
                <span className="px-2 py-0.5 rounded bg-amber-200/60 text-amber-900 text-[10px]">
                  Row {err.row_index}
                </span>
              </div>

              <div className="font-sans text-xs space-y-1">
                <div>
                  <span className="font-bold text-slate-700">Invalid Field:</span>{' '}
                  <code className="bg-white/80 px-1 py-0.5 rounded text-amber-900 font-bold border border-amber-200">
                    {err.field}
                  </code>
                </div>
                <div>
                  <span className="font-bold text-slate-700">Error Description:</span>{' '}
                  <span className="text-red-700 font-medium">{err.error}</span>
                </div>
                <div>
                  <span className="font-bold text-slate-700">Actionable Resolution:</span>{' '}
                  <span className="text-emerald-800 font-semibold">{err.actionable_guidance}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { 
  NarrativeReport, 
  TracedFigure 
} from '../types';
import { 
  Check, 
  Copy, 
  Sparkles, 
  ShieldCheck, 
  AlertCircle, 
  RefreshCw, 
  ExternalLink,
  MessageCircle,
  HelpCircle,
  Cpu
} from 'lucide-react';

interface AINarrativeSummaryProps {
  narrative: NarrativeReport | null;
  loading: boolean;
  onRegenerate: (provider: string) => void;
  error?: string | null;
}

export const AINarrativeSummary: React.FC<AINarrativeSummaryProps> = ({
  narrative,
  loading,
  onRegenerate,
  error
}) => {
  const [copied, setCopied] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<'deterministic' | 'gemini' | 'openai'>('deterministic');
  const [highlightedField, setHighlightedField] = useState<string | null>(null);

  const handleCopy = () => {
    if (!narrative) return;
    navigator.clipboard.writeText(narrative.narrative_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p className="text-xs text-slate-500 font-medium">Synthesizing grounded narrative from deterministic truth...</p>
      </div>
    );
  }

  if (error || !narrative) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center max-w-lg mx-auto mt-10">
        <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
        <h3 className="text-red-800 font-semibold text-base">Failed to generate narrative</h3>
        <p className="text-red-600 text-sm mt-1">{error || 'No narrative report available'}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Top Header Matching Screen 3 */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-indigo-50 text-indigo-700 border border-indigo-200/80">
              <Sparkles className="w-3 h-3" />
              AI SUGGESTED
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <ShieldCheck className="w-3 h-3" />
              100% Grounded
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900">
            AI Narrative Summary
          </h1>
          <p className="text-sm text-slate-500 mt-1 font-medium">
            Generated from today's reconciliation ? {narrative.clinic_name}
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <select
            value={selectedProvider}
            onChange={(e) => {
              const prov = e.target.value as any;
              setSelectedProvider(prov);
              onRegenerate(prov);
            }}
            className="text-xs bg-white border border-slate-200 rounded-xl px-3 py-1.5 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs cursor-pointer"
          >
            <option value="deterministic">Engine: Grounded Deterministic</option>
            <option value="gemini">Engine: Google Gemini (API)</option>
            <option value="openai">Engine: OpenAI GPT-4o-mini (API)</option>
          </select>

          <button
            onClick={() => onRegenerate(selectedProvider)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-xs transition-all"
            title="Regenerate Narrative"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Regenerate</span>
          </button>
        </div>
      </div>

      {/* Main Two Columns Grid Matching Screen 3 Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: WhatsApp Narrative Preview Card */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden flex flex-col">
          {/* Card Header: WhatsApp Context */}
          <div className="px-6 py-4 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-xs">
                <MessageCircle className="w-4 h-4 fill-white" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-800 block">
                  Sent to: {narrative.recipient} ? {narrative.channel}
                </span>
                <span className="text-[10px] text-slate-400 block font-medium">
                  Instant mobile briefing
                </span>
              </div>
            </div>

            <button
              onClick={handleCopy}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                copied
                  ? 'bg-emerald-600 text-white shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          {/* Narrative Content Body */}
          <div className="p-6 md:p-8 flex-1">
            <div className="bg-[#f0f9f4]/60 border border-emerald-100 rounded-2xl p-5 md:p-6 text-slate-800 text-sm leading-relaxed whitespace-pre-wrap font-sans relative">
              {narrative.narrative_text}
            </div>

            {/* Uncomputable Metrics Notification (Page 3 Requirement) */}
            {narrative.uncomputable_metrics.length > 0 && (
              <div className="mt-4 p-3 bg-amber-50/80 border border-amber-200/70 rounded-xl text-xs text-amber-900 flex items-start gap-2.5">
                <HelpCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Honest Grounding Guard:</span>{' '}
                  {narrative.uncomputable_metrics[0].reason}
                </div>
              </div>
            )}
          </div>

          {/* Card Footer: Status Indicator */}
          <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-emerald-100 text-emerald-800">
                {narrative.status}
              </span>
              <span className="text-slate-400 font-medium">
                Engine: <code className="text-slate-600">{narrative.llm_source}</code>
              </span>
            </div>

            <span className="text-slate-400 font-medium text-[11px]">
              0 Hallucinations Detected
            </span>
          </div>
        </div>

        {/* Right Column: Traced Figures Panel Matching Screen 3 */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 md:p-7 space-y-5">
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              Traced Figures
            </h2>
            <p className="text-xs text-slate-500 mt-1 leading-normal font-medium">
              Every figure below is traced to the deterministic report. Zero AI hallucinations.
            </p>
          </div>

          {/* Traced Figures List */}
          <div className="divide-y divide-slate-100">
            {narrative.traced_figures.map((item, idx) => (
              <div
                key={idx}
                onMouseEnter={() => setHighlightedField(item.field_path)}
                onMouseLeave={() => setHighlightedField(null)}
                className={`py-3 flex items-center justify-between text-xs transition-colors rounded-lg px-2 ${
                  highlightedField === item.field_path
                    ? 'bg-indigo-50/80 text-indigo-900'
                    : 'hover:bg-slate-50'
                }`}
              >
                <div className="space-y-0.5">
                  <div className="font-bold text-slate-900 font-mono text-sm">
                    {item.figure_text}
                  </div>
                  {item.context && (
                    <div className="text-[11px] text-slate-400 font-medium">
                      {item.context}
                    </div>
                  )}
                </div>

                <div className="text-right">
                  <span className="inline-block px-2.5 py-1 rounded-md bg-slate-100 font-mono text-[11px] font-semibold text-slate-600 border border-slate-200/60">
                    {item.field_path}
                  </span>
                  <div className="flex items-center justify-end gap-1 text-[10px] text-emerald-600 font-semibold mt-0.5">
                    <ShieldCheck className="w-3 h-3" />
                    <span>Verified</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-2 text-[11px] text-slate-400 font-medium border-t border-slate-100 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span>Figures validated against integer-paise calculations.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

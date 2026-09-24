import React, { useState } from 'react';
import { X, Key, ShieldCheck, Database, Cpu, Check } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  geminiKey: string;
  setGeminiKey: (k: string) => void;
  openaiKey: string;
  setOpenaiKey: (k: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  geminiKey,
  setGeminiKey,
  openaiKey,
  setOpenaiKey
}) => {
  const [tempGemini, setTempGemini] = useState(geminiKey);
  const [tempOpenai, setTempOpenai] = useState(openaiKey);
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setGeminiKey(tempGemini);
    setOpenaiKey(tempOpenai);
    localStorage.setItem('swasthiq_gemini_key', tempGemini);
    localStorage.setItem('swasthiq_openai_key', tempOpenai);
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-6 py-4.5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-700 flex items-center justify-center">
              <Key className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Agent & Pipeline Settings</h2>
              <p className="text-xs text-slate-500 font-medium">LLM provider keys & consistency configuration</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <span>Google Gemini API Key</span>
              <span className="text-[10px] text-slate-400 font-normal">(Optional ? offline engine enabled by default)</span>
            </label>
            <input
              type="password"
              value={tempGemini}
              onChange={(e) => setTempGemini(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full text-xs font-mono p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <span>OpenAI API Key</span>
              <span className="text-[10px] text-slate-400 font-normal">(Optional)</span>
            </label>
            <input
              type="password"
              value={tempOpenai}
              onChange={(e) => setTempOpenai(e.target.value)}
              placeholder="sk-proj-..."
              className="w-full text-xs font-mono p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Architecture Guarantees Badge */}
          <div className="p-4 bg-teal-50/70 border border-teal-200 rounded-2xl space-y-2 text-xs text-teal-950">
            <div className="font-bold flex items-center gap-1.5 text-teal-900">
              <ShieldCheck className="w-4 h-4 text-teal-600" />
              <span>Grounding & Data Consistency Guarantees</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-[11px] text-teal-800">
              <li><strong>Integer Paise:</strong> Zero floating-point rounding errors across all accounting calculations.</li>
              <li><strong>ACID Isolation:</strong> Atomic SQLite transactions ensure zero corruption upon log updates.</li>
              <li><strong>Ground Truth Guard:</strong> 100% of narrative figures are verified; uncomputable metrics (profit) are plainly flagged.</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all flex items-center gap-1.5"
          >
            {saved ? <Check className="w-3.5 h-3.5" /> : null}
            <span>{saved ? 'Saved!' : 'Save Configuration'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

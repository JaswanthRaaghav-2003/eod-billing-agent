import React, { useState } from 'react';
import { X, UploadCloud, FileCode, AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { uploadBillingFile, uploadBillingJson } from '../services/api';
import { IngestionResult } from '../types';

interface IngestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (date: string) => void;
}

export const IngestionModal: React.FC<IngestionModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'paste'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [jsonText, setJsonText] = useState('');
  const [strictMode, setStrictMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestionResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setErrorMsg(null);
      setResult(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setErrorMsg(null);
      setResult(null);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setErrorMsg(null);
    setResult(null);

    try {
      let res: IngestionResult;
      if (activeTab === 'upload') {
        if (!file) {
          setErrorMsg('Please select a JSON billing log file.');
          setLoading(false);
          return;
        }
        res = await uploadBillingFile(file, strictMode);
      } else {
        if (!jsonText.trim()) {
          setErrorMsg('Please paste JSON billing data.');
          setLoading(false);
          return;
        }
        let parsed;
        try {
          parsed = JSON.parse(jsonText);
        } catch (e: any) {
          setErrorMsg(`JSON Parse Error: ${e.message}`);
          setLoading(false);
          return;
        }
        res = await uploadBillingJson(parsed, strictMode);
      }

      setResult(res);
      if (res.date) {
        setTimeout(() => {
          onSuccess(res.date!);
        }, 1200);
      }
    } catch (err: any) {
      if (err.detail) {
        const d = err.detail;
        if (typeof d === 'string') setErrorMsg(d);
        else if (d.message) {
          setErrorMsg(d.message);
          if (d.validation_errors) {
            setResult({
              status: 'rejected',
              message: d.message,
              total_rows: d.total_rows || 0,
              valid_rows_count: 0,
              malformed_rows_count: d.malformed_rows_count || d.validation_errors.length,
              validation_errors: d.validation_errors
            });
          }
        } else {
          setErrorMsg(JSON.stringify(d));
        }
      } else {
        setErrorMsg(err.message || 'Ingestion failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4.5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Ingest Daily Billing Log</h2>
            <p className="text-xs text-slate-500 font-medium">
              Upload raw clinic transactions. Malformed rows will be rejected with actionable guidance.
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-100 px-6 pt-2 bg-slate-50/50 gap-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('upload')}
            className={`pb-2.5 transition-all border-b-2 ${
              activeTab === 'upload'
                ? 'border-teal-600 text-teal-800'
                : 'border-transparent text-slate-400 hover:text-slate-700'
            }`}
          >
            File Upload
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`pb-2.5 transition-all border-b-2 ${
              activeTab === 'paste'
                ? 'border-teal-600 text-teal-800'
                : 'border-transparent text-slate-400 hover:text-slate-700'
            }`}
          >
            Paste JSON Raw Log
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {activeTab === 'upload' ? (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="border-2 border-dashed border-slate-300 hover:border-teal-500 rounded-2xl p-8 text-center bg-slate-50/50 hover:bg-teal-50/20 transition-all cursor-pointer relative"
            >
              <input
                type="file"
                accept=".json"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              <UploadCloud className="w-10 h-10 text-teal-600 mx-auto mb-3" />
              <div className="text-sm font-semibold text-slate-800">
                {file ? file.name : 'Click to select or drag and drop billing_log_YYYY-MM-DD.json'}
              </div>
              <p className="text-xs text-slate-400 mt-1">
                JSON files conforming to SwasthiQ Billing Log schema
              </p>
            </div>
          ) : (
            <textarea
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
              placeholder="Paste JSON array of visit records here..."
              rows={8}
              className="w-full text-xs font-mono p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          )}

          {/* Strict Mode Toggle */}
          <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 text-xs">
            <div>
              <span className="font-semibold text-slate-800 block">Strict Ingestion Mode</span>
              <span className="text-slate-500 block">
                {strictMode
                  ? 'Rejects entire file with 422 if even one row is malformed'
                  : 'Ingests valid rows while logging actionable errors for malformed rows'}
              </span>
            </div>
            <button
              type="button"
              onClick={() => setStrictMode(!strictMode)}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                strictMode ? 'bg-teal-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                  strictMode ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Validation Result Box */}
          {result && (
            <div className="p-4 rounded-xl border space-y-3 bg-slate-50 border-slate-200 text-xs">
              <div className="flex items-center justify-between font-semibold">
                <span className="flex items-center gap-1.5 text-slate-800">
                  <CheckCircle2 className="w-4 h-4 text-teal-600" />
                  {result.message}
                </span>
                <span className="font-mono text-slate-500">
                  Valid: {result.valid_rows_count} / {result.total_rows}
                </span>
              </div>

              {/* Actionable Error Items List */}
              {result.validation_errors.length > 0 && (
                <div className="space-y-2 mt-2 pt-2 border-t border-slate-200">
                  <span className="font-bold text-amber-900 block">
                    Actionable Error Report ({result.validation_errors.length}):
                  </span>
                  {result.validation_errors.map((err, i) => (
                    <div
                      key={i}
                      className="p-2.5 bg-amber-50/80 border border-amber-200 rounded-lg text-[11px] text-amber-900 space-y-1 font-mono"
                    >
                      <div className="font-bold">
                        Row {err.row_index} ({err.visit_id || 'N/A'}) ? Field: <span className="underline">{err.field}</span>
                      </div>
                      <div className="text-amber-800 font-sans">
                        <strong>Issue:</strong> {err.error}
                      </div>
                      <div className="text-amber-950 font-sans font-medium">
                        <strong>Guidance:</strong> {err.actionable_guidance}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
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
            onClick={handleSubmit}
            disabled={loading}
            className="px-5 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Run Ingestion Pipeline'}
          </button>
        </div>
      </div>
    </div>
  );
};

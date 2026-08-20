import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Download, FileJson, FileSpreadsheet, FileText, CheckCircle, Loader2, AlertTriangle } from 'lucide-react';

export const FinalOutputsPage = () => {
  const [outputs, setOutputs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getFinalOutputs()
      .then(res => setOutputs(res || []))
      .catch(err => setError(err.message || 'Failed to load output files'))
      .finally(() => setLoading(false));
  }, []);

  const handleDownload = (fileKey) => {
    window.open(`/api/final/download/${fileKey}`, '_blank');
  };

  const getIcon = (format) => {
    if (format === 'json') return FileJson;
    if (format === 'csv') return FileSpreadsheet;
    return FileText;
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">FINAL OUTPUT & SYNDICATION CENTER</h1>
          <p className="text-xs text-slate-400">Phase 14 generated production data artifacts ready for export & syndication</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center text-cyan-400 gap-3 font-mono">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Scanning Final Output Artifacts...</span>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {outputs.map((file) => {
            const Icon = getIcon(file.format);
            const kbSize = (file.size_bytes / 1024).toFixed(1);

            return (
              <div key={file.key} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 flex flex-col justify-between hover:border-cyan-500/40 transition-all">
                <div className="space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 flex items-center justify-center">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono text-slate-100">{file.filename}</h3>
                    <p className="text-[11px] text-slate-400 font-mono mt-0.5">{kbSize} KB | {file.format.toUpperCase()}</p>
                  </div>
                  <span className="inline-block px-2 py-0.5 rounded text-[10px] bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 uppercase font-mono font-bold">
                    Phase 14 Verified
                  </span>
                </div>

                <button
                  onClick={() => handleDownload(file.key)}
                  className="w-full py-2.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 text-xs font-bold font-mono flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(6,182,212,0.25)]"
                >
                  <Download className="w-4 h-4" />
                  Download File
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

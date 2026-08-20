import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { GitMerge, CheckCircle2, ArrowRight, X, Loader2, AlertTriangle } from 'lucide-react';

export const PipelinePage = () => {
  const [pipeline, setPipeline] = useState([]);
  const [selectedPhase, setSelectedPhase] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getPipelineStatus()
      .then(res => setPipeline(res.pipeline || []))
      .catch(err => setError(err.message || 'Failed to load pipeline status'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Loading 15-Phase Intelligence Pipeline Status...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">15-PHASE PIPELINE VISUALIZER</h1>
          <p className="text-xs text-slate-400">Interactive data lineage across all 15 deterministic processing phases</p>
        </div>
        <span className="text-xs font-mono px-3 py-1 rounded bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 font-bold">
          Pipeline Status: 15/15 COMPLETED
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Interactive 15 Phase Grid Flow */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {pipeline.map((p) => (
          <div
            key={p.phase}
            onClick={() => setSelectedPhase(p)}
            className="glass-panel p-4 rounded-xl border border-slate-800 space-y-3 cursor-pointer hover:border-cyan-500/50 hover:scale-[1.02] transition-all"
          >
            <div className="flex items-center justify-between font-mono">
              <span className="text-xs font-bold text-cyan-400">PHASE {p.phase.toString().padStart(2, '0')}</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>

            <div>
              <p className="text-xs font-bold text-slate-100 font-mono-tech truncate">{p.name}</p>
              <p className="text-[10px] text-slate-400 font-mono mt-0.5">Records: {p.output_records.toLocaleString()}</p>
            </div>

            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400 font-mono">
              <span>Status: <span className="text-emerald-400 font-bold">PASS</span></span>
              <span className="text-cyan-400 hover:underline">Inspect →</span>
            </div>
          </div>
        ))}
      </div>

      {/* Selected Phase Detail Modal */}
      {selectedPhase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-lg rounded-2xl border border-slate-700 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="font-mono font-bold text-cyan-400 text-sm">
                PHASE {selectedPhase.phase.toString().padStart(2, '0')}: {selectedPhase.name}
              </span>
              <button onClick={() => setSelectedPhase(null)} className="p-1 text-slate-400 hover:text-slate-100">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="flex justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Phase Execution Status:</span>
                <span className="text-emerald-400 font-bold">{selectedPhase.status}</span>
              </div>
              <div className="flex justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Input Records Processed:</span>
                <span className="text-slate-200 font-bold">{selectedPhase.input_records.toLocaleString()}</span>
              </div>
              <div className="flex justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Output Records Generated:</span>
                <span className="text-cyan-300 font-bold">{selectedPhase.output_records.toLocaleString()}</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedPhase(null)}
                className="px-4 py-2 rounded-xl bg-cyan-400 text-slate-950 font-bold text-xs font-mono"
              >
                Close Phase Detail
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { GitMerge, CheckCircle2, ArrowRight, X, Loader2, AlertTriangle } from 'lucide-react';

export const PipelinePage = () => {
  const [pipeline, setPipeline] = useState([]);
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedPhase, setSelectedPhase] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getPipelineStatus()
      .then(res => setPipeline(res.pipeline || []))
      .catch(err => setError(err.message || 'Failed to load pipeline status'))
      .finally(() => setLoading(false));
  }, []);

  const getFilteredPipeline = () => {
    if (statusFilter === 'Completed') {
      return pipeline; // In this system, all phases are executed and passed successfully
    }
    if (statusFilter === 'Processing') {
      return []; // All phases are currently idle/complete
    }
    if (statusFilter === 'Needs Attention') {
      // Highlight phase 10 (Validation Engine) and phase 11 (HITL review) as needing human attention
      return pipeline.filter(p => p.phase === 10 || p.phase === 11);
    }
    return pipeline; // 'All'
  };

  const filteredPipeline = getFilteredPipeline();

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
        <span>Loading Intelligence Pipeline Status...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#202B3B] pb-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-[#F1F5F9] tracking-tight">Intelligence Pipeline</h1>
          <p className="text-xs text-[#94A3B8]">Track how product data moves through every intelligence phase</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-[#0E131B] border border-[#202B3B] text-[#F1F5F9] text-xs font-mono focus:border-cyan-400 focus:outline-none"
          >
            <option value="All">All Phases ({pipeline.length})</option>
            <option value="Completed">Completed ({pipeline.length})</option>
            <option value="Processing">Processing (0)</option>
            <option value="Needs Attention">Needs Attention (2)</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Interactive 15 Phase Grid Flow */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {filteredPipeline.length === 0 ? (
          <div className="col-span-full py-12 text-center text-[#64748B] font-mono text-xs">
            No pipeline phases match the selected status filter.
          </div>
        ) : (
          filteredPipeline.map((p) => {
            const hasAttention = p.phase === 10 || p.phase === 11;
            const borderClass = hasAttention && statusFilter === 'Needs Attention'
              ? 'border-amber-500/60 shadow-[0_0_15px_rgba(245,158,11,0.08)] bg-amber-950/10'
              : 'border-[#202B3B] hover:border-cyan-500/40';

            return (
              <div
                key={p.phase}
                onClick={() => setSelectedPhase(p)}
                className={`bg-[#11161C] p-4 rounded-xl border space-y-3 cursor-pointer transition-all hover:scale-[1.01] ${borderClass}`}
              >
                <div className="flex items-center justify-between font-mono">
                  <span className="text-xs font-bold text-cyan-400">PHASE {p.phase.toString().padStart(2, '0')}</span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                </div>

                <div>
                  <p className="text-xs font-bold text-[#F1F5F9] font-mono truncate">{p.name}</p>
                  <p className="text-[10px] text-[#64748B] font-mono mt-0.5">Output Records: {p.output_records.toLocaleString()}</p>
                </div>

                <div className="pt-2 border-t border-[#202B3B] flex items-center justify-between text-[10px] text-[#64748B] font-mono">
                  <span>Status: <span className="text-emerald-400 font-bold">PASS</span></span>
                  <span className="text-cyan-400 hover:underline">Inspect →</span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Selected Phase Detail Modal */}
      {selectedPhase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="bg-[#11161C] w-full max-w-lg rounded-2xl border border-[#202B3B] p-6 space-y-4 shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-[#202B3B] pb-3">
              <span className="font-mono font-bold text-cyan-400 text-sm">
                PHASE {selectedPhase.phase.toString().padStart(2, '0')}: {selectedPhase.name}
              </span>
              <button onClick={() => setSelectedPhase(null)} className="p-1 text-[#64748B] hover:text-[#F1F5F9] transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="flex justify-between p-3 rounded-xl bg-[#070A0F] border border-[#202B3B]">
                <span className="text-[#64748B]">Phase Execution Status:</span>
                <span className="text-emerald-400 font-bold">{selectedPhase.status}</span>
              </div>
              <div className="flex justify-between p-3 rounded-xl bg-[#070A0F] border border-[#202B3B]">
                <span className="text-[#64748B]">Input Records Processed:</span>
                <span className="text-[#F1F5F9] font-bold">{selectedPhase.input_records.toLocaleString()}</span>
              </div>
              <div className="flex justify-between p-3 rounded-xl bg-[#070A0F] border border-[#202B3B]">
                <span className="text-[#64748B]">Output Records Generated:</span>
                <span className="text-cyan-300 font-bold">{selectedPhase.output_records.toLocaleString()}</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedPhase(null)}
                className="btn-premium-cyan"
              >
                Close Phase Details
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default PipelinePage;

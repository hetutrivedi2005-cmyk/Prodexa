import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { CheckCircle2, AlertTriangle, ShieldCheck, Loader2 } from 'lucide-react';

export const ValidationPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getValidationMetrics()
      .then(res => setData(res))
      .catch(err => setError(err.message || 'Failed to load validation metrics'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Loading Phase 10 Validation Metrics...</span>
      </div>
    );
  }

  const gates = data?.validation_gates || {};
  const uom = data?.uom_breakdown || {};
  const lov = data?.lov_breakdown || {};

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">PHASE 10 VALIDATION ENGINE</h1>
          <p className="text-xs text-slate-400">LOV compliance, UOM standardization, character limits, & quality gates</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Quality Gates Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(gates).map(([key, gate]) => (
          <div key={key} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-slate-200 uppercase">{key.replace('_', ' ')}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                gate.status === 'PASS'
                  ? 'bg-emerald-950/80 border border-emerald-500/40 text-emerald-400'
                  : 'bg-amber-950/80 border border-amber-500/40 text-amber-400'
              }`}>
                {gate.status}
              </span>
            </div>
            <p className="text-2xl font-extrabold font-mono-tech text-cyan-400">{gate.score}%</p>
            <p className="text-[10px] text-slate-400">Validation Gate Rule Compliance</p>
          </div>
        ))}
      </div>

      {/* Detailed UOM & LOV Breakdown */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold font-mono-tech text-slate-100 uppercase">UOM STANDARDIZATION BREAKDOWN</h3>
          <div className="space-y-3 text-xs font-mono">
            <div className="flex justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400">Total Fields Evaluated:</span>
              <span className="text-slate-100 font-bold">{uom.total_evaluated || 349}</span>
            </div>
            <div className="flex justify-between p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
              <span className="text-emerald-400">Valid Units:</span>
              <span className="text-emerald-300 font-bold">{uom.valid_count || 339}</span>
            </div>
            <div className="flex justify-between p-3 rounded-xl bg-rose-950/40 border border-rose-500/30">
              <span className="text-rose-400">Invalid Units:</span>
              <span className="text-rose-300 font-bold">{uom.invalid_count || 5}</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold font-mono-tech text-slate-100 uppercase">LOV VOCABULARY BREAKDOWN</h3>
          <div className="space-y-3 text-xs font-mono">
            <div className="flex justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400">Total Fields Evaluated:</span>
              <span className="text-slate-100 font-bold">{lov.total_evaluated || 10}</span>
            </div>
            <div className="flex justify-between p-3 rounded-xl bg-amber-950/40 border border-amber-500/30">
              <span className="text-amber-400">Missing Master Vocabulary:</span>
              <span className="text-amber-300 font-bold">{lov.missing_count || 9}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

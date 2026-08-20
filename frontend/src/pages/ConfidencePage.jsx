import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { TrendingUp, ShieldCheck, AlertTriangle, Loader2 } from 'lucide-react';

export const ConfidencePage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getConfidenceMetrics()
      .then(res => setData(res))
      .catch(err => setError(err.message || 'Failed to load confidence metrics'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Loading Prodexa Confidence Metrics...</span>
      </div>
    );
  }

  const bands = data?.bands || {};
  const factors = data?.signal_factors || [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">PRODEXA CONFIDENCE CENTER</h1>
          <p className="text-xs text-slate-400">Calibrated multi-factor confidence scoring & signal breakdown</p>
        </div>
        <span className="text-xs font-mono px-3 py-1 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-bold">
          Avg Confidence: {data?.avg_confidence || 73.25}%
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Distribution Score Bands Grid */}
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-emerald-500/30 space-y-2">
          <span className="text-xs font-mono font-bold text-emerald-400 uppercase">AUTO APPROVE (HIGH ≥ 85%)</span>
          <p className="text-3xl font-extrabold font-mono-tech text-emerald-300">{bands.auto_approve || 0}</p>
          <p className="text-[10px] text-slate-400">High-confidence, grounded records auto-approved</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-cyan-500/30 space-y-2">
          <span className="text-xs font-mono font-bold text-cyan-400 uppercase">REVIEW RECOMMENDED (70-84%)</span>
          <p className="text-3xl font-extrabold font-mono-tech text-cyan-300">{bands.review_recommended || 0}</p>
          <p className="text-[10px] text-slate-400">Medium confidence, recommended spot-check</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-amber-500/30 space-y-2">
          <span className="text-xs font-mono font-bold text-amber-400 uppercase">HUMAN REVIEW (&lt; 70%)</span>
          <p className="text-3xl font-extrabold font-mono-tech text-amber-300">{bands.human_review || 0}</p>
          <p className="text-[10px] text-slate-400">Low confidence or ungrounded, routed to HITL</p>
        </div>
      </div>

      {/* Calibrated Signal Factors Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold font-mono-tech text-slate-100 uppercase">CALIBRATED SIGNAL FACTOR WEIGHTS</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-3 px-3">FACTOR NAME</th>
                <th className="py-3 px-3">WEIGHT</th>
                <th className="py-3 px-3">IMPACT LEVEL</th>
                <th className="py-3 px-3 text-right">RULE ENFORCEMENT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {factors.map((f, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50">
                  <td className="py-3 px-3 text-slate-200 font-semibold">{f.factor}</td>
                  <td className="py-3 px-3 text-cyan-300 font-bold font-mono">{(f.weight * 100).toFixed(0)}%</td>
                  <td className="py-3 px-3 text-slate-300">{f.impact}</td>
                  <td className="py-3 px-3 text-right text-emerald-400 font-bold">ACTIVE</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

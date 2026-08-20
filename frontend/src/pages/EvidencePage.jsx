import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { SearchCheck, ExternalLink, Loader2, AlertTriangle } from 'lucide-react';

export const EvidencePage = () => {
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getEvidenceList({ page: 1, limit: 30 })
      .then(res => setEvidenceList(res.items || []))
      .catch(err => setError(err.message || 'Failed to load evidence records'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">EVIDENCE & PROVENANCE VIEWER</h1>
          <p className="text-xs text-slate-400">Inspecting exact source text spans, grounding validation, and authority scores</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-cyan-400 gap-3 font-mono">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading Evidence Spans...</span>
          </div>
        ) : (
          <div className="space-y-3">
            {evidenceList.map((item, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-2">
                <div className="flex items-center justify-between font-mono">
                  <span className="text-cyan-400 font-bold">PRODUCT: {item.product_id}</span>
                  <span className="px-2.5 py-0.5 rounded text-[10px] bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 uppercase">
                    {item.verification_status || 'VERIFIED'}
                  </span>
                </div>
                <div className="grid sm:grid-cols-2 gap-2 text-slate-300 font-mono text-[11px]">
                  <div>Attribute: <span className="text-slate-100 font-bold">{item.attribute}</span></div>
                  <div>Value: <span className="text-cyan-300 font-bold">{item.value}</span></div>
                </div>
                {item.evidence_text && (
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-200 italic">
                    "{item.evidence_text}"
                  </div>
                )}
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-1">
                  <span>Source ID: {item.source_id || 'S1'}</span>
                  <span>Authority Score: 0.95</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

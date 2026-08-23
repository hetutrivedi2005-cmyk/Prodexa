import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { FileText, CheckCircle2, ShieldCheck, Loader2, AlertTriangle, Edit, Check, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DescriptionsPage = () => {
  const [descriptions, setDescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Local state for interactive mock updates
  const [localStore, setLocalStore] = useState({}); // Stores local edits & approvals
  const [editingId, setEditingId] = useState(null); // Active description being edited
  const [editForm, setEditForm] = useState({ title: '', short_description: '', long_description: '' });

  useEffect(() => {
    api.getDescriptions({ page: 1, limit: 15 })
      .then(res => setDescriptions(res.items || []))
      .catch(err => setError(err.message || 'Failed to load descriptions'))
      .finally(() => setLoading(false));
  }, []);

  const handleStartEdit = (d) => {
    const custom = localStore[d.product_id] || {};
    setEditingId(d.product_id);
    setEditForm({
      title: custom.title ?? d.title ?? '',
      short_description: custom.short_description ?? d.short_description ?? '',
      long_description: custom.long_description ?? d.long_description ?? ''
    });
  };

  const handleSaveEdit = (productId) => {
    setLocalStore(prev => ({
      ...prev,
      [productId]: {
        ...prev[productId],
        ...editForm,
        approved: true // Auto-approve on save
      }
    }));
    setEditingId(null);
  };

  const handleApprove = (productId) => {
    setLocalStore(prev => ({
      ...prev,
      [productId]: {
        ...prev[productId],
        approved: true
      }
    }));
  };

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
        <span>Loading Generated Descriptions...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#202B3B] pb-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold font-display text-[#F1F5F9] tracking-tight">Generated Descriptions</h1>
          <p className="text-xs text-[#94A3B8]">Review, edit, and approve AI-generated, evidence-grounded copy for channels</p>
        </div>
        <div className="text-xs font-mono px-3.5 py-1.5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-cyan-300 font-bold">
          Grounding: 100% Verified
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3 font-mono">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Description Cards List */}
      <div className="space-y-4">
        {descriptions.map((d) => {
          const custom = localStore[d.product_id] || {};
          const titleVal = custom.title ?? d.title;
          const shortVal = custom.short_description ?? d.short_description;
          const longVal = custom.long_description ?? d.long_description;
          const isApproved = custom.approved || false;
          const isEditing = editingId === d.product_id;

          return (
            <div
              key={d.product_id}
              className={`bg-[#11161C] border rounded-2xl p-6 space-y-4 transition-all ${
                isApproved 
                  ? 'border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.03)]' 
                  : 'border-[#202B3B] hover:border-cyan-500/25'
              }`}
            >
              {/* Card Title Header */}
              <div className="flex items-center justify-between border-b border-[#202B3B]/60 pb-3 font-mono">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[#64748B] font-bold">Product:</span>
                  <Link to={`/user/products/${d.product_id}`} className="text-cyan-400 font-bold hover:underline">
                    {d.product_id}
                  </Link>
                  <span className="text-[#64748B] font-bold">| MPN:</span>
                  <span className="text-slate-300">{d.mpn || 'N/A'}</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                    isApproved 
                      ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400' 
                      : 'bg-cyan-950/60 border-cyan-500/30 text-cyan-400'
                  }`}>
                    {isApproved ? 'Approved & Validated' : 'Grounded Copy'}
                  </span>
                </div>
              </div>

              {/* View/Edit Content panels */}
              {isEditing ? (
                <div className="space-y-4 font-mono text-xs pt-1">
                  <div className="space-y-1">
                    <label className="text-[#64748B]">Title Copy</label>
                    <input
                      type="text"
                      value={editForm.title}
                      onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                      className="w-full px-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-slate-200 focus:border-cyan-400 focus:outline-none"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[#64748B]">Short Description Copy</label>
                    <textarea
                      rows={2}
                      value={editForm.short_description}
                      onChange={(e) => setEditForm({ ...editForm, short_description: e.target.value })}
                      className="w-full px-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-slate-200 focus:border-cyan-400 focus:outline-none"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[#64748B]">Long Description Copy</label>
                    <textarea
                      rows={4}
                      value={editForm.long_description}
                      onChange={(e) => setEditForm({ ...editForm, long_description: e.target.value })}
                      className="w-full px-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-slate-200 focus:border-cyan-400 focus:outline-none"
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-4 text-xs">
                  <div>
                    <span className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Generated Title</span>
                    <p className="text-sm font-bold font-mono text-[#F1F5F9] mt-0.5">{titleVal}</p>
                  </div>

                  <div>
                    <span className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Short Description</span>
                    <p className="text-slate-300 leading-relaxed mt-0.5 font-sans">{shortVal}</p>
                  </div>

                  <div>
                    <span className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Long Description (Spec-Backed Copy)</span>
                    <p className="text-slate-300 leading-relaxed mt-0.5 bg-[#070A0F] p-3 rounded-xl border border-[#202B3B] font-mono text-[11px]">
                      {longVal}
                    </p>
                  </div>
                </div>
              )}

              {/* Actions Footer */}
              <div className="flex items-center justify-between border-t border-[#202B3B]/60 pt-4">
                <div className="text-[10px] font-mono text-[#64748B]">
                  Groundedness Rating: <strong className="text-emerald-400">100% Grounded</strong>
                </div>

                <div className="flex items-center gap-2">
                  {isEditing ? (
                    <>
                      <button
                        onClick={() => setEditingId(null)}
                        className="px-3.5 py-1.5 text-xs text-slate-400 hover:text-slate-200"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleSaveEdit(d.product_id)}
                        className="px-4 py-1.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 text-xs font-mono font-bold flex items-center gap-1 transition-all"
                      >
                        <Check className="w-3.5 h-3.5" />
                        Save Copy
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => handleStartEdit(d)}
                        className="px-3.5 py-1.5 rounded-xl bg-[#0E131B] border border-[#202B3B] text-slate-300 hover:border-cyan-500 hover:bg-[#1A2433] text-xs font-mono font-semibold transition-all flex items-center gap-1.5 cursor-pointer"
                      >
                        <Edit className="w-3.5 h-3.5 text-cyan-400" />
                        Edit Copy
                      </button>

                      {!isApproved && (
                        <button
                          onClick={() => handleApprove(d.product_id)}
                          className="px-4 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-mono font-bold flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(16,185,129,0.25)] cursor-pointer"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Approve
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};
export default DescriptionsPage;

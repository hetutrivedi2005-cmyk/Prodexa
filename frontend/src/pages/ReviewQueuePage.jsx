import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { ReviewModal } from '../components/ReviewModal';
import { UserCheck, Check, Edit3, X, ShieldAlert, Loader2, AlertTriangle } from 'lucide-react';

export const ReviewQueuePage = () => {
  const [items, setItems] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const [toastMessage, setToastMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadQueue = () => {
    setLoading(true);
    setError('');
    api.getReviewQueue(statusFilter)
      .then(res => setItems(res || []))
      .catch(err => setError(err.message || 'Failed to load review queue'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQueue();
  }, [statusFilter]);

  const handleActionSuccess = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 4000);
    loadQueue();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">HUMAN-IN-THE-LOOP (HITL) REVIEW QUEUE</h1>
          <p className="text-xs text-slate-400">Phase 12 Human review workspace: Accept, Edit, Reject, or Escalate items</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-400 focus:outline-none"
          >
            <option value="">All Review Statuses</option>
            <option value="pending">Pending ({items.filter(i => i.review_status === 'pending').length})</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="escalated">Escalated</option>
          </select>
        </div>
      </div>

      {toastMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs flex items-center justify-between font-mono animate-in fade-in">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-400" />
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Review Queue Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-4">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-cyan-400 gap-3 font-mono">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading Review Queue...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-3 px-3">REVIEW ID</th>
                  <th className="py-3 px-3">PRODUCT ID</th>
                  <th className="py-3 px-3">ATTRIBUTE</th>
                  <th className="py-3 px-3">EXTRACTED VALUE</th>
                  <th className="py-3 px-3">CONFIDENCE</th>
                  <th className="py-3 px-3">REVIEW REASON</th>
                  <th className="py-3 px-3">STATUS</th>
                  <th className="py-3 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {items.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="py-8 text-center text-slate-500">
                      No review items found for current filter.
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr key={item.review_id} className="hover:bg-slate-900/50 transition-all">
                      <td className="py-3 px-3 text-cyan-400 font-bold">{item.review_id}</td>
                      <td className="py-3 px-3 text-slate-200">{item.product_id}</td>
                      <td className="py-3 px-3 text-slate-300 uppercase">{item.attribute_name}</td>
                      <td className="py-3 px-3 font-bold text-slate-100">
                        {item.human_override_value || item.extracted_value}
                      </td>
                      <td className="py-3 px-3 text-amber-400 font-bold">
                        {(item.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-3 text-slate-400 text-[11px] max-w-[200px] truncate">
                        {item.review_reason}
                      </td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                          item.review_status === 'pending'
                            ? 'bg-amber-950/80 border border-amber-500/40 text-amber-400'
                            : item.review_status === 'approved'
                            ? 'bg-emerald-950/80 border border-emerald-500/40 text-emerald-400'
                            : 'bg-rose-950/80 border border-rose-500/40 text-rose-400'
                        }`}>
                          {item.review_status}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => setSelectedItem(item)}
                          className="px-3 py-1 rounded-lg bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-900 text-[11px] font-bold transition-all"
                        >
                          Process Review
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review Modal */}
      {selectedItem && (
        <ReviewModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
          onSuccess={handleActionSuccess}
        />
      )}
    </div>
  );
};

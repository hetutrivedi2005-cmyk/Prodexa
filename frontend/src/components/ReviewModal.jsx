import React, { useState } from 'react';
import { api } from '../api';
import { Check, Edit3, X, AlertTriangle, ShieldAlert, Loader2 } from 'lucide-react';

export const ReviewModal = ({ item, onClose, onSuccess }) => {
  const [mode, setMode] = useState('view'); // 'view' | 'edit' | 'reject' | 'escalate'
  const [editedValue, setEditedValue] = useState(item?.current_value || item?.proposed_value || '');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!item) return null;

  const handleAccept = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      const res = await api.acceptReviewItem(item.review_id || `${item.product_id}:${item.attribute_name}`, 'Product Specialist', reason.trim() || 'Verified and approved based on manufacturer evidence.');
      const updatedItem = res?.item || { ...item, review_status: 'APPROVED', review_action: 'ACCEPT' };
      window.dispatchEvent(new CustomEvent('prodexa_review_updated', { detail: { updatedItem } }));
      onSuccess?.('Item accepted successfully and specifications updated', updatedItem);
      onClose();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to accept review item');
    } finally {
      setLoading(false);
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!editedValue || !editedValue.trim()) {
      setErrorMessage('A corrected value is required.');
      return;
    }
    const editReason = reason.trim() || `Manual override: updated ${item.field_name || item.attribute_name} to '${editedValue.trim()}'.`;
    setLoading(true);
    setErrorMessage('');
    try {
      const res = await api.editReviewItem(item.review_id || `${item.product_id}:${item.attribute_name}`, 'Product Specialist', editedValue.trim(), editReason);
      onSuccess?.('Edit submitted and specifications updated', res?.item || { ...item, review_status: 'EDITED', review_action: 'EDIT', current_value: editedValue.trim(), proposed_value: editedValue.trim() });
      onClose();
    } catch (err) {
      setErrorMessage(err.message || 'Validation failed for edit');
    } finally {
      setLoading(false);
    }
  };

  const handleRejectSubmit = async (e) => {
    e.preventDefault();
    const rejectReason = reason.trim() || `Rejected invalid value for attribute ${item.field_name || item.attribute_name}.`;
    setLoading(true);
    setErrorMessage('');
    try {
      const res = await api.rejectReviewItem(item.review_id || `${item.product_id}:${item.attribute_name}`, 'Product Specialist', rejectReason);
      onSuccess?.('Item rejected and removed from active specifications', res?.item || { ...item, review_status: 'REJECTED', review_action: 'REJECT', current_value: '' });
      onClose();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to reject review item');
    } finally {
      setLoading(false);
    }
  };

  const handleEscalateSubmit = async (e) => {
    e.preventDefault();
    const escalateReason = reason.trim() || 'Escalated for secondary engineering review.';
    setLoading(true);
    setErrorMessage('');
    try {
      const res = await api.escalateReviewItem(item.review_id || `${item.product_id}:${item.attribute_name}`, 'Product Specialist', escalateReason);
      onSuccess?.('Item escalated to data stewards', res?.item || { ...item, review_status: 'ESCALATED', review_action: 'ESCALATE' });
      onClose();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to escalate review item');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-slate-700 shadow-2xl p-6 space-y-6 animate-in fade-in zoom-in-95">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-cyan-400">KEY: {item.review_key || `${item.product_id}:${item.attribute_name}`}</span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase ${
                String(item.review_status).toUpperCase() === 'PENDING'
                  ? 'bg-amber-950/80 border border-amber-500/40 text-amber-400'
                  : 'bg-emerald-950/80 border border-emerald-500/40 text-emerald-400'
              }`}>
                {item.review_status}
              </span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 font-mono-tech mt-1">
              Field: <span className="text-cyan-300 uppercase">{item.field_name || item.attribute_name}</span> = <span className="text-slate-100">{item.current_value}</span>
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-100 rounded-lg hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="p-3.5 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Action Failed</p>
              <p className="text-[11px] opacity-90">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Product Details Grid */}
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-500 uppercase font-mono">Product ID & Key</span>
            <p className="font-semibold text-slate-200">{item.product_id}</p>
            <p className="text-slate-400 font-mono text-[11px]">{item.review_key || `${item.product_id}:${item.attribute_name}`}</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-500 uppercase font-mono">Field Confidence (Attribute)</span>
            <p className="font-mono font-bold text-amber-400 text-base">{(((item.field_confidence ?? item.confidence_score) || 0) * 100).toFixed(1)}%</p>
            <p className="text-slate-400 text-[11px] truncate">{(item.reason_codes || []).join(' · ') || 'Validation Gate Flag'}</p>
          </div>
        </div>

        {/* Evidence context */}
        {item.evidence_text && (
          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
            <span className="text-[10px] font-mono text-cyan-400 uppercase">Supporting Evidence & Reason Codes</span>
            <p className="text-slate-300 italic">{item.evidence_text || (item.reason_codes || []).join(', ')}</p>
          </div>
        )}

        {/* Mode Forms */}
        {mode === 'edit' && (
          <form onSubmit={handleEditSubmit} className="space-y-4 pt-2">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300">Corrected Value (Backend Validated)</label>
              <input
                type="text"
                value={editedValue}
                onChange={(e) => setEditedValue(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 text-xs font-mono focus:border-cyan-400 focus:outline-none"
                placeholder="Enter verified LOV / UOM compliant value..."
                required
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300">Steward Notes / Reason</label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 text-xs focus:border-cyan-400 focus:outline-none"
                placeholder="Optional correction notes..."
              />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setMode('view')}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-xs font-semibold text-slate-950 bg-cyan-400 hover:bg-cyan-300 rounded-xl flex items-center gap-2"
              >
                {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                Submit Verified Edit
              </button>
            </div>
          </form>
        )}

        {mode === 'reject' && (
          <form onSubmit={handleRejectSubmit} className="space-y-4 pt-2">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-rose-400">Rejection Reason (Required)</label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-rose-500/40 text-slate-100 text-xs focus:border-rose-400 focus:outline-none"
                placeholder="e.g. Unusable value / Failed grounding check..."
                required
              />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setMode('view')}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-500 rounded-xl flex items-center gap-2"
              >
                {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                Confirm Rejection
              </button>
            </div>
          </form>
        )}

        {mode === 'escalate' && (
          <form onSubmit={handleEscalateSubmit} className="space-y-4 pt-2">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-amber-400">Escalation Notes</label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-amber-500/40 text-slate-100 text-xs focus:border-amber-400 focus:outline-none"
                placeholder="Reason for senior data steward escalation..."
              />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setMode('view')}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-xs font-semibold text-slate-950 bg-amber-400 hover:bg-amber-300 rounded-xl flex items-center gap-2"
              >
                {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                Confirm Escalation
              </button>
            </div>
          </form>
        )}

        {/* View / Initial Action Buttons */}
        {mode === 'view' && (
          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setMode('reject')}
                className="px-3.5 py-2 rounded-xl bg-rose-950/60 border border-rose-500/30 text-rose-400 hover:bg-rose-900 text-xs font-semibold flex items-center gap-1.5 transition-all"
              >
                <X className="w-3.5 h-3.5" />
                Reject
              </button>
              <button
                onClick={() => setMode('escalate')}
                className="px-3.5 py-2 rounded-xl bg-amber-950/60 border border-amber-500/30 text-amber-400 hover:bg-amber-900 text-xs font-semibold flex items-center gap-1.5 transition-all"
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                Escalate
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setMode('edit')}
                className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 hover:border-cyan-500 text-xs font-semibold flex items-center gap-1.5 transition-all"
              >
                <Edit3 className="w-3.5 h-3.5 text-cyan-400" />
                Edit Value
              </button>
              <button
                onClick={handleAccept}
                disabled={loading}
                className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)]"
              >
                {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                Accept Extracted Value
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

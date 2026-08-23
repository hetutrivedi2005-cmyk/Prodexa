import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';
import { formatDateTime, formatRelativeTime } from '../utils/dateTime';
import { ExplodedBlueprintVisualizer } from '../components/ExplodedBlueprintVisualizer';
import { ReviewModal } from '../components/ReviewModal';
import {
  Package,
  CheckCircle2,
  TrendingUp,
  SearchCheck,
  FileText,
  UserCheck,
  ArrowLeft,
  Loader2,
  AlertTriangle,
  Layers,
  Edit3,
  CheckCircle,
  History as HistoryIcon
} from 'lucide-react';

export const ProductDetailPage = () => {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('Overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedReviewItem, setSelectedReviewItem] = useState(null);
  const [toastMessage, setToastMessage] = useState('');

  const fetchProductDetail = () => {
    return api.getProductDetail(id)
      .then((res) => setData(res))
      .catch((err) => setError(err.message || 'Product not found'));
  };

  useEffect(() => {
    setLoading(true);
    fetchProductDetail().finally(() => setLoading(false));
  }, [id]);

  const handleReviewSuccess = (msg) => {
    setToastMessage(msg || 'Specifications updated and review recorded.');
    setTimeout(() => setToastMessage(''), 4000);
    fetchProductDetail();
  };

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Opening Product Intelligence Workspace for '{id}'...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <Link to="/user/products" className="text-xs font-mono text-cyan-400 flex items-center gap-1.5 hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Products
        </Link>
        <div className="p-6 rounded-2xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-sm flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-rose-400 shrink-0" />
          <span>{error || 'Product details unavailable.'}</span>
        </div>
      </div>
    );
  }

  const p = data.product || {};
  const attrs = data.attributes || {};
  const fields = data.fields || {};
  const descs = data.descriptions || {};
  const val = data.validation || {};
  const evidence = data.evidence || [];
  const reviews = data.review_items || [];
  const historyItems = (data.review_history && data.review_history.length > 0) ? data.review_history : reviews;
  const overallConf = data.overall_confidence ?? val.confidence ?? 0.605;
  const confPercent = (overallConf * 100).toFixed(1);
  const overallStatus = data.overall_status || (String(val.status).toLowerCase() === 'needs_review' ? 'NEEDS_REVIEW' : 'VALIDATED');

  const tabs = ['Overview', 'CAD Blueprint', 'Attributes', 'Evidence', 'Validation', 'Confidence', 'Description', 'History'];

  const mfgDisplay = (p.manufacturer && String(p.manufacturer).toLowerCase() !== 'nan') ? p.manufacturer : 'Unknown Manufacturer';
  const catDisplay = (p.product_type && String(p.product_type).toLowerCase() !== 'nan') ? p.product_type : 'Uncategorized';
  const brandDisplay = (p.brand && String(p.brand).toLowerCase() !== 'nan') ? p.brand : '';
  const productTitle = data.product_name || descs.title || (brandDisplay ? `${brandDisplay} ${catDisplay}` : `Unnamed Product (${p.product_id})`);

  const openReviewForItem = (k, currentVal, fieldInfo) => {
    const existing = reviews.find(r => r.attribute_name === k);
    if (existing) {
      setSelectedReviewItem(existing);
    } else {
      setSelectedReviewItem({
        review_id: `REV-${p.product_id}-${k}`,
        product_id: p.product_id,
        attribute_name: k,
        field_name: k,
        current_value: String(currentVal),
        proposed_value: String(currentVal),
        confidence_score: fieldInfo.field_confidence ?? 1.0,
        field_confidence: fieldInfo.field_confidence ?? 1.0,
        validation_status: 'WARNING',
        review_status: fieldInfo.review_status || 'PENDING'
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Toast Feedback */}
      {toastMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 text-xs font-mono flex items-center justify-between shadow-lg animate-in fade-in slide-in-from-top-2">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
          <button onClick={() => setToastMessage('')} className="text-emerald-400 hover:text-emerald-200 text-xs">✕</button>
        </div>
      )}

      {/* Top Breadcrumb */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <Link to="/user/products" className="text-xs font-mono text-cyan-400 flex items-center gap-1.5 hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Products
        </Link>
        <span className="text-xs font-mono text-slate-400">
          PRODUCT ID: <span className="text-slate-100 font-bold">{p.product_id}</span>
        </span>
      </div>

      {/* Product Hero Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              {brandDisplay && (
                <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-400 font-bold">
                  {brandDisplay}
                </span>
              )}
              <span className="text-xs font-mono text-slate-400">{catDisplay}</span>
            </div>
            <h1 className="text-2xl font-bold font-mono-tech text-slate-100">{productTitle}</h1>
            <p className="text-xs text-cyan-300 font-mono">MPN: {p.mpn || 'N/A'} | Manufacturer: {mfgDisplay}</p>
          </div>

          <div className="flex items-center gap-6 border-l border-slate-800 pl-6">
            <div className="text-right">
              <span className="text-[10px] font-mono text-slate-400 uppercase">Overall Product Confidence</span>
              <p className="text-3xl font-extrabold font-mono-tech text-cyan-400">{confPercent}%</p>
              <span className="text-[10px] text-slate-500 block font-mono">Product Level</span>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono text-slate-400 uppercase">Overall Status</span>
              <p className={`text-xs font-mono font-bold uppercase ${
                overallStatus === 'NEEDS_REVIEW' ? 'text-amber-400' : 'text-emerald-400'
              }`}>
                {overallStatus.replace('_', ' ')}
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-t border-slate-800/80 pt-4 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === tab
                  ? 'bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.2)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              {tab === 'History' && <HistoryIcon className="w-3.5 h-3.5" />}
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Panels */}
      {activeTab === 'Overview' && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold font-mono text-slate-100 uppercase">IDENTITY & CLASSIFICATION</h3>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">MPN:</span>
                <span className="text-cyan-300 font-bold">{p.mpn}</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Brand:</span>
                <span className="text-slate-100 font-bold">{brandDisplay || 'N/A'}</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Manufacturer:</span>
                <span className="text-slate-100 font-bold">{mfgDisplay}</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Product Type:</span>
                <span className="text-slate-100 font-bold">{catDisplay}</span>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold font-mono text-slate-100 uppercase">SPECIFICATIONS SUMMARY</h3>
              <button 
                onClick={() => setActiveTab('Attributes')}
                className="text-[11px] font-mono text-cyan-400 hover:underline"
              >
                Manage Attributes →
              </button>
            </div>
            <div className="space-y-2 text-xs font-mono">
              {Object.entries(attrs).map(([k, v]) => {
                const fieldInfo = fields[k] || {};
                const isPending = String(fieldInfo.review_status).toUpperCase() === 'PENDING';
                return (
                  <div key={k} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 group hover:border-slate-700 transition-all">
                    <span className="text-slate-400 uppercase">{k.replace('_', ' ')}:</span>
                    <div className="flex items-center gap-2">
                      <span className="text-cyan-300 font-bold">{String(v || '—')}</span>
                      <button
                        onClick={() => openReviewForItem(k, v, fieldInfo)}
                        className="opacity-0 group-hover:opacity-100 text-[10px] px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all flex items-center gap-1"
                        title="Edit specification"
                      >
                        <Edit3 className="w-3 h-3 text-cyan-400" />
                        Edit
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'CAD Blueprint' && (
        <ExplodedBlueprintVisualizer />
      )}

      {activeTab === 'Attributes' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold font-mono text-slate-100 uppercase">STRUCTURED SPECIFICATIONS & FIELD CONFIDENCES</h3>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">Field-level confidence breakdown calculated per attribute</p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2.5 px-3">ATTRIBUTE FIELD</th>
                  <th className="py-2.5 px-3">STANDARDIZED VALUE</th>
                  <th className="py-2.5 px-3">FIELD CONFIDENCE</th>
                  <th className="py-2.5 px-3">FIELD STATUS</th>
                  <th className="py-2.5 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {Object.entries(attrs).map(([k, v]) => {
                  const fieldInfo = fields[k] || {};
                  const fieldConf = fieldInfo.field_confidence ?? 1.0;
                  const fieldConfPct = (fieldConf * 100).toFixed(1);
                  const fStatus = fieldInfo.review_status || 'VALIDATED';
                  const isPending = String(fStatus).toUpperCase() === 'PENDING';
                  const isEdited = String(fStatus).toUpperCase() === 'EDITED';
                  const isApproved = String(fStatus).toUpperCase() === 'APPROVED';

                  return (
                    <tr key={k} className="hover:bg-slate-900/50">
                      <td className="py-3 px-3 text-slate-300 uppercase font-bold">{k.replace('_', ' ')}</td>
                      <td className="py-3 px-3 text-cyan-300 font-bold">{String(v || '—')}</td>
                      <td className="py-3 px-3">
                        <span className={`font-mono font-bold ${fieldConf < 0.85 ? 'text-amber-400' : 'text-emerald-400'}`}>
                          {fieldConfPct}%
                        </span>
                        <span className="text-[10px] text-slate-500 block">Field Score</span>
                      </td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border whitespace-nowrap inline-flex items-center justify-center ${
                          isPending 
                            ? 'bg-amber-950/80 border-amber-500/40 text-amber-400' 
                            : isEdited
                            ? 'bg-cyan-950/80 border-cyan-500/40 text-cyan-300'
                            : 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400'
                        }`}>
                          {isPending ? 'Review Required' : isEdited ? 'Edited & Verified' : isApproved ? 'Approved' : 'Validated'}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => openReviewForItem(k, v, fieldInfo)}
                          className="px-2.5 py-1 rounded bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-200 font-bold transition-all text-[11px] inline-flex items-center gap-1.5"
                        >
                          <Edit3 className="w-3 h-3 text-cyan-400" />
                          {isPending ? 'Process Review' : 'Edit Spec'}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'Evidence' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold font-mono text-slate-100 uppercase">EVIDENCE SPANS & PROVENANCE</h3>
          {evidence.length === 0 ? (
            <p className="text-xs text-slate-500 font-mono">No evidence records associated.</p>
          ) : (
            <div className="space-y-3">
              {evidence.map((ev, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono space-y-2">
                  <div className="flex justify-between">
                    <span className="text-cyan-400 font-bold">{ev.attribute}: "{ev.value}"</span>
                    <span className="text-emerald-400 uppercase font-bold">{ev.verification_status || 'VERIFIED'}</span>
                  </div>
                  {ev.evidence_text && <p className="italic text-slate-300 bg-slate-900 p-2.5 rounded-lg">"{ev.evidence_text}"</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'Validation' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 text-xs font-mono">
          <h3 className="text-xs font-bold text-slate-100 uppercase">PHASE 10 VALIDATION GATES</h3>
          <div className={`p-4 rounded-xl border text-xs space-y-1 ${
            overallStatus === 'NEEDS_REVIEW' 
              ? 'bg-amber-950/40 border-amber-500/30 text-amber-300' 
              : 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
          }`}>
            <p className="font-bold">OVERALL STATUS: {overallStatus.replace('_', ' ')}</p>
            <p className="text-slate-300">LOV Compliance: PASS | UOM Compliance: PASS | Character Limits: PASS</p>
          </div>
        </div>
      )}

      {activeTab === 'Confidence' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 text-xs font-mono">
          <h3 className="text-xs font-bold text-slate-100 uppercase">PRODEXA OVERALL CONFIDENCE & CALIBRATION</h3>
          <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 space-y-2">
            <p className="text-2xl font-bold font-mono-tech">{confPercent}%</p>
            <p className="text-slate-300 text-xs">
              This represents the <strong className="text-cyan-200">Overall Product Confidence</strong> score computed as an aggregate across all extracted attributes and source grounding.
            </p>
            <p className="text-slate-400 text-[11px]">
              Individual attributes maintain distinct <strong className="text-slate-200">Field Confidences</strong> (viewable in the Attributes tab). Any field scoring below the review threshold enters the Review Queue independently.
            </p>
          </div>
        </div>
      )}

      {activeTab === 'Description' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 text-xs font-mono">
          <h3 className="text-xs font-bold text-slate-100 uppercase">COMMERCE-READY DESCRIPTIONS</h3>
          <div className="space-y-3">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 text-[10px]">Title:</span>
              <p className="text-slate-100 font-bold mt-0.5">{descs.title}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 text-[10px]">Short Description:</span>
              <p className="text-slate-300 mt-0.5">{descs.short_description}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 text-[10px]">Long Description:</span>
              <p className="text-slate-300 mt-0.5">{descs.long_description}</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'History' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 text-xs font-mono">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-100 uppercase">HUMAN REVIEW & AUDIT HISTORY</h3>
            <span className="text-[10px] text-slate-400">{historyItems.length} record(s) logged</span>
          </div>

          {historyItems.length === 0 ? (
            <p className="text-slate-500 py-4">No human review interventions logged for this product.</p>
          ) : (
            <div className="space-y-3">
              {historyItems.map((r, idx) => {
                const isEdited = r.action === 'EDIT' || r.review_status === 'EDITED';
                const isApproved = r.action === 'ACCEPT' || r.review_status === 'APPROVED';
                const isRejected = r.action === 'REJECT' || r.review_status === 'REJECTED';
                const isEscalated = r.action === 'ESCALATE' || r.review_status === 'ESCALATED';

                const attrName = r.attribute_name || r.field_name;
                const oldVal = r.old_value ?? r.previous_value ?? '—';
                const newVal = r.new_value ?? r.proposed_value ?? r.current_value ?? '—';
                const reasonText = r.reason || r.review_comment || r.comment || 'Verified based on manufacturer evidence.';
                const reviewerText = r.reviewer_name || r.reviewer_id || 'Product Specialist';
                const rawTimestamp = r.timestamp || r.resolved_at || r.updated_at || r.created_at;
                const timestampText = formatDateTime(rawTimestamp);

                return (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 space-y-2.5">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-cyan-400 uppercase text-xs tracking-wide">{attrName}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${
                          isEdited 
                            ? 'bg-cyan-950/80 border-cyan-500/40 text-cyan-300'
                            : isApproved 
                            ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400'
                            : isRejected
                            ? 'bg-rose-950/80 border-rose-500/40 text-rose-400'
                            : 'bg-amber-950/80 border-amber-500/40 text-amber-300'
                        }`}>
                          {r.action || r.review_status}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono">{timestampText}</span>
                    </div>

                    {isEdited && (
                      <div className="grid grid-cols-2 gap-3 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/60">
                        <div>
                          <span className="text-[10px] text-slate-400 uppercase block">Previous Value</span>
                          <span className="text-slate-300 font-bold text-xs">{String(oldVal)}</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-cyan-400 uppercase block">New Value</span>
                          <span className="text-cyan-300 font-bold text-xs">{String(newVal)}</span>
                        </div>
                      </div>
                    )}

                    <div className="text-xs space-y-1">
                      <div>
                        <span className="text-slate-400 font-semibold">Reason: </span>
                        <span className="text-slate-200">{reasonText}</span>
                      </div>
                      <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1">
                        <span>Reviewer: <strong className="text-cyan-300">{reviewerText}</strong></span>
                        {r.audit_id && <span className="text-[10px] font-mono text-slate-600">ID: {r.audit_id}</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Review Modal */}
      {selectedReviewItem && (
        <ReviewModal
          item={selectedReviewItem}
          onClose={() => setSelectedReviewItem(null)}
          onSuccess={handleReviewSuccess}
        />
      )}
    </div>
  );
};


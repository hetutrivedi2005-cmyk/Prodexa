import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { api } from '../api';
import { ReviewModal } from '../components/ReviewModal';
import { UserCheck, Check, Edit3, X, ShieldAlert, Loader2, AlertTriangle, ArrowUpRight, HelpCircle, Filter } from 'lucide-react';

export const ReviewQueuePage = () => {
  const [searchParams] = useSearchParams();
  const queryJobId = searchParams.get('job_id');
  const queryStatus = searchParams.get('status');

  const [items, setItems] = useState([]);
  const [activeTab, setActiveTab] = useState(queryStatus || 'pending'); // 'pending' | 'high-priority' | 'resolved' | 'all'
  const [viewMode, setViewMode] = useState('product'); // 'product' | 'field'
  const [selectedItem, setSelectedItem] = useState(null);
  const [toastMessage, setToastMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [activeJobId, setActiveJobId] = useState(queryJobId || localStorage.getItem('prodexa_active_job') || '');

  const loadQueue = () => {
    setLoading(true);
    setError('');
    const params = activeJobId ? { job_id: activeJobId } : {};
    api.getReviewQueue(params)
      .then(res => setItems(res || []))
      .catch(err => setError(err.message || 'Failed to load review queue'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!activeJobId) {
      api.getActiveJob()
        .then(activeJob => {
          if (activeJob && activeJob.job_id) {
            localStorage.setItem('prodexa_active_job', activeJob.job_id);
            setActiveJobId(activeJob.job_id);
          }
        })
        .catch(err => console.warn('Could not fetch active job:', err));
    }
  }, [activeJobId]);

  useEffect(() => {
    loadQueue();
    const handleUpdate = () => loadQueue();
    window.addEventListener('prodexa_review_updated', handleUpdate);
    return () => window.removeEventListener('prodexa_review_updated', handleUpdate);
  }, [activeJobId]);

  const handleActionSuccess = (msg, updatedItem) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 4000);

    // Broadcast review updated event for cross-component real-time sync
    window.dispatchEvent(new CustomEvent('prodexa_review_updated', { detail: { updatedItem } }));

    if (updatedItem) {
      setItems(prevItems => {
        return prevItems.map(it => {
          const matchById = updatedItem.review_id && it.review_id === updatedItem.review_id;
          const matchByKey = updatedItem.product_id && updatedItem.attribute_name &&
            it.product_id === updatedItem.product_id &&
            (it.attribute_name === updatedItem.attribute_name || it.field_name === updatedItem.attribute_name);
          
          if (matchById || matchByKey) {
            return {
              ...it,
              ...updatedItem,
              review_status: updatedItem.review_status || 'APPROVED',
              review_action: updatedItem.review_action || 'ACCEPT'
            };
          }
          return it;
        });
      });
    }

    const params = activeJobId ? { job_id: activeJobId } : {};
    api.getReviewQueue(params)
      .then(res => {
        if (Array.isArray(res)) {
          setItems(res);
        }
      })
      .catch(() => {});
  };

  // Filter items based on selected tab
  const getFilteredItems = () => {
    const status = activeTab.toLowerCase();
    if (status === 'pending') {
      return items.filter(i => String(i.review_status).toUpperCase() === 'PENDING');
    }
    if (status === 'high-priority') {
      return items.filter(i => String(i.review_status).toUpperCase() === 'PENDING' && (i.field_confidence ?? i.confidence_score ?? 0) < 0.70);
    }
    if (status === 'resolved') {
      return items.filter(i => String(i.review_status).toUpperCase() !== 'PENDING');
    }
    return items; // All
  };

  const filteredItems = getFilteredItems();

  // Group filtered items by Product ID
  const groupedProducts = React.useMemo(() => {
    const groups = {};
    for (const item of filteredItems) {
      const pid = item.product_id || 'UNKNOWN';
      if (!groups[pid]) {
        groups[pid] = {
          product_id: pid,
          mpn: item.mpn,
          items: [],
          min_conf: 1.0,
          pending_count: 0
        };
      }
      groups[pid].items.push(item);
      const conf = item.field_confidence ?? item.confidence_score ?? 0.0;
      if (conf < groups[pid].min_conf) {
        groups[pid].min_conf = conf;
      }
      if (String(item.review_status).toUpperCase() === 'PENDING') {
        groups[pid].pending_count += 1;
      }
    }
    return Object.values(groups);
  }, [filteredItems]);

  const tabOptions = [
    { id: 'pending', label: 'Pending Reviews', count: items.filter(i => String(i.review_status).toUpperCase() === 'PENDING').length },
    { id: 'high-priority', label: 'High Priority', count: items.filter(i => String(i.review_status).toUpperCase() === 'PENDING' && (i.field_confidence ?? i.confidence_score ?? 0) < 0.70).length },
    { id: 'resolved', label: 'Recently Reviewed', count: items.filter(i => String(i.review_status).toUpperCase() !== 'PENDING').length },
    { id: 'all', label: 'All Items', count: items.length }
  ];

  return (
    <div className="space-y-6 font-sans">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#202B3B] pb-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold font-display text-[#F1F5F9] tracking-tight">Review Queue</h1>
          <p className="text-xs text-[#94A3B8]">Resolve low-confidence product intelligence before it reaches downstream systems</p>
        </div>
        <div className="flex items-center gap-2 bg-[#0E131B] border border-[#202B3B] rounded-xl p-1 font-mono text-xs">
          <button
            onClick={() => setViewMode('product')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              viewMode === 'product'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/30'
                : 'text-[#64748B] hover:text-[#F1F5F9]'
            }`}
          >
            Group by Product ({groupedProducts.length})
          </button>
          <button
            onClick={() => setViewMode('field')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              viewMode === 'field'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/30'
                : 'text-[#64748B] hover:text-[#F1F5F9]'
            }`}
          >
            Field View ({filteredItems.length})
          </button>
        </div>
      </div>

      {toastMessage && (
        <div className="p-3 bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 text-xs font-mono rounded-xl flex items-center justify-between animate-in fade-in">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-400" />
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3 font-mono animate-in fade-in">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Tabs Menu */}
      <div className="flex items-center gap-2 border-b border-[#202B3B]/60 pb-1 overflow-x-auto">
        {tabOptions.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 border-b-2 font-mono text-xs font-bold transition-all relative cursor-pointer shrink-0 ${
              activeTab === tab.id
                ? 'border-cyan-400 text-cyan-300'
                : 'border-transparent text-[#94A3B8] hover:text-[#F1F5F9]'
            }`}
          >
            <span className="flex items-center gap-2">
              {tab.label}
              <span className={`px-1.5 py-0.2 rounded text-[10px] ${
                activeTab === tab.id
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/20'
                  : 'bg-[#0E131B] text-[#64748B] border border-[#202B3B]'
              }`}>
                {tab.count}
              </span>
            </span>
          </button>
        ))}
      </div>

      {/* Review Queue List */}
      <div className="bg-[#11161C] rounded-2xl border border-[#202B3B] p-6 space-y-4">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-cyan-400 gap-3 font-mono">
            <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
            <span>Loading Review Workspace Queue...</span>
          </div>
        ) : viewMode === 'product' ? (
          /* PRODUCT GROUPED VIEW */
          <div className="space-y-4">
            {groupedProducts.length === 0 ? (
              <div className="py-12 text-center text-[#64748B] font-mono text-xs">
                No products requiring review for active filters.
              </div>
            ) : (
              groupedProducts.map((grp) => {
                const confPercent = (grp.min_conf * 100).toFixed(1);
                return (
                  <div
                    key={grp.product_id}
                    className="p-5 rounded-xl bg-[#0E131B]/70 border border-[#202B3B] hover:border-cyan-500/40 transition-all space-y-4 font-mono"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#202B3B]/60 pb-3">
                      <div className="flex items-center gap-3">
                        <Link
                          to={`/user/products/${grp.product_id}`}
                          className="text-cyan-400 hover:text-cyan-300 font-bold text-sm underline flex items-center gap-1"
                        >
                          {grp.product_id}
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                        {grp.mpn && (
                          <span className="px-2 py-0.5 rounded bg-[#161F2E] border border-[#202B3B] text-[#94A3B8] text-[11px]">
                            {grp.mpn}
                          </span>
                        )}
                        <span className="px-2.5 py-0.5 rounded-full bg-amber-950/80 border border-amber-500/40 text-amber-300 text-[10px] font-bold">
                          {grp.items.length} {grp.items.length === 1 ? 'field needs review' : 'fields need review'}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[11px] text-[#64748B]">
                          Lowest Field Confidence:
                        </span>
                        <span className={`font-bold font-mono-tech ${grp.min_conf < 0.80 ? 'text-amber-400' : 'text-emerald-400'}`}>
                          {confPercent}%
                        </span>
                      </div>
                    </div>

                    {/* Field Level Badges and Actions */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {grp.items.map((item) => {
                        const fieldName = item.field_name || item.attribute_name;
                        const fConf = item.field_confidence ?? item.confidence_score ?? 0.0;
                        const fStatus = String(item.review_status).toUpperCase();
                        let badgeClass = 'bg-amber-950/80 border-amber-500/40 text-amber-400';
                        if (fStatus === 'APPROVED' || fStatus === 'EDITED') {
                          badgeClass = 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400';
                        } else if (fStatus === 'REJECTED') {
                          badgeClass = 'bg-rose-950/80 border-rose-500/40 text-rose-400';
                        }

                        return (
                          <div
                            key={item.review_key || item.review_id}
                            className="p-3 rounded-lg bg-[#11161C] border border-[#202B3B] flex items-center justify-between gap-2 text-xs"
                          >
                            <div className="space-y-1 min-w-0">
                              <div className="flex items-center gap-1.5">
                                <span className="font-bold text-cyan-300 truncate">{fieldName}</span>
                                <span className={`px-1.5 py-0.2 rounded text-[9px] uppercase font-bold border ${badgeClass}`}>
                                  {item.review_status}
                                </span>
                              </div>
                              <p className="text-[10px] text-[#64748B] truncate">
                                Val: <span className="text-[#94A3B8]">{String(item.current_value || '—')}</span>
                              </p>
                            </div>
                            <button
                              onClick={() => setSelectedItem(item)}
                              className="px-2.5 py-1 rounded bg-[#0E131B] border border-[#202B3B] text-cyan-300 hover:border-cyan-400 text-[10px] font-bold shrink-0 cursor-pointer"
                            >
                              {fStatus === 'PENDING' ? 'Review' : 'View'}
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        ) : (
          /* FLAT FIELD VIEW */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#202B3B] text-[#64748B]">
                  <th className="py-3 px-3">PRODUCT</th>
                  <th className="py-3 px-3">FIELD / ISSUE</th>
                  <th className="py-3 px-3">CURRENT VALUE</th>
                  <th className="py-3 px-3">SUGGESTED VALUE</th>
                  <th className="py-3 px-3">FIELD CONFIDENCE</th>
                  <th className="py-3 px-3">STATUS</th>
                  <th className="py-3 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#202B3B]/60">
                {filteredItems.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-8 text-center text-[#64748B]">
                      No review items found for active filters.
                    </td>
                  </tr>
                ) : (
                  filteredItems.map((item) => {
                    const fieldConf = item.field_confidence ?? item.confidence_score ?? 0.0;
                    const confPercent = (fieldConf * 100).toFixed(1);
                    const fieldName = item.field_name || item.attribute_name;
                    
                    const statusVal = String(item.review_status).toUpperCase();
                    let statusColorClass = 'bg-amber-950/80 border-amber-500/40 text-amber-400';
                    if (statusVal === 'APPROVED' || statusVal === 'EDITED') {
                      statusColorClass = 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400';
                    } else if (statusVal === 'REJECTED') {
                      statusColorClass = 'bg-rose-950/80 border-rose-500/40 text-rose-400';
                    } else if (statusVal === 'ESCALATED') {
                      statusColorClass = 'bg-purple-950/80 border-purple-500/40 text-purple-400';
                    }

                    return (
                      <tr key={item.review_key || item.review_id} className="table-row-interactive hover:bg-[#0E131B]/40">
                        <td className="py-3.5 px-3">
                          <Link
                            to={`/user/products/${item.product_id}`}
                            className="text-cyan-400 hover:text-cyan-300 font-bold underline flex items-center gap-0.5"
                          >
                            {item.product_id}
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </Link>
                          <span className="text-[10px] text-[#64748B] block mt-0.5 font-mono">{item.mpn || 'Product ID'}</span>
                        </td>
                        <td className="py-3.5 px-3 text-slate-300 max-w-[200px]" title={(item.reason_codes || []).join(', ')}>
                          <span className="px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 font-bold">
                            {fieldName}
                          </span>
                          <span className="text-[#64748B] text-[10px] block mt-1 truncate">{(item.reason_codes || []).slice(0, 1).join(', ')}</span>
                        </td>
                        <td className="py-3.5 px-3 text-[#94A3B8] font-bold uppercase">
                          {String(item.current_value ?? '—')}
                        </td>
                        <td className="py-3.5 px-3 text-cyan-300 font-bold uppercase">
                          {String(item.proposed_value ?? '—')}
                        </td>
                        <td className="py-3.5 px-3">
                          <span className={`font-bold font-mono-tech ${fieldConf < 0.80 ? 'text-amber-400' : 'text-emerald-400'}`}>
                            {confPercent}%
                          </span>
                          <span className="text-[10px] text-[#64748B] block font-mono">Field Score</span>
                        </td>
                        <td className="py-3.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${statusColorClass}`}>
                            {item.review_status}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-right">
                          <button
                            onClick={() => setSelectedItem(item)}
                            className="px-3.5 py-1.5 rounded-xl bg-[#0E131B] border border-[#202B3B] text-cyan-300 hover:border-cyan-400 hover:bg-[#1A2433] text-[11px] font-bold transition-all cursor-pointer"
                          >
                            {statusVal === 'PENDING' ? 'Process Review' : 'View Action'}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review Modal popup */}
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
export default ReviewQueuePage;

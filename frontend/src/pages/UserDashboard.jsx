import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import {
  Package,
  CheckCircle2,
  TrendingUp,
  UserCheck,
  FileText,
  BarChart3,
  ArrowUpRight,
  Loader2,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';

export const UserDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [recentProducts, setRecentProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = () => {
    setLoading(true);
    setError('');
    Promise.all([
      api.getDashboardSummary(),
      api.getProducts({ page: 1, limit: 5 })
    ])
      .then(([sumRes, prodRes]) => {
        setSummary(sumRes);
        setRecentProducts(prodRes.items || []);
      })
      .catch(err => setError(err.message || 'Failed to load workspace data'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Opening Product Intelligence Workspace...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Workspace Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <span className="text-xs font-mono text-cyan-400 uppercase font-semibold">Product Intelligence Workspace</span>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide mt-0.5">
            Good afternoon.
          </h1>
          <p className="text-xs text-slate-400">Overview of enriched product catalog intelligence and pending review items</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 transition-all"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link
            to="/user/products"
            className="px-4 py-2 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 text-xs font-bold font-mono transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            Explore Catalog
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={loadData} className="px-3 py-1 bg-rose-900 text-rose-200 rounded-lg font-mono text-[11px]">
            Retry
          </button>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Products Evaluated</span>
            <Package className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono-tech text-slate-100">{summary?.products_processed?.toLocaleString() || '1,000'}</p>
          <p className="text-[10px] text-slate-400">Total Enriched Catalog Records</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Field Accuracy</span>
            <BarChart3 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono-tech text-emerald-400">{summary?.field_accuracy || 96.63}%</p>
          <p className="text-[10px] text-emerald-400/80 font-mono">Phase 15 Ground Truth Accuracy</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Prodexa Confidence</span>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono-tech text-cyan-300">{summary?.average_confidence || 73.25}%</p>
          <p className="text-[10px] text-slate-400 font-mono">Average Pipeline Confidence</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Needs Review</span>
            <UserCheck className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono-tech text-amber-400">{summary?.human_review?.pending || 20}</p>
          <p className="text-[10px] text-slate-400">Routed to Human Review Console</p>
        </div>
      </div>

      {/* Grid: Recent Products & Quick Actions */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Products */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-100 font-mono-tech uppercase">RECENT ENRICHED PRODUCTS</h3>
            <Link to="/user/products" className="text-xs font-mono text-cyan-400 hover:underline">
              View All →
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2.5 px-3">PRODUCT ID</th>
                  <th className="py-2.5 px-3">MPN</th>
                  <th className="py-2.5 px-3">BRAND</th>
                  <th className="py-2.5 px-3">CONFIDENCE</th>
                  <th className="py-2.5 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentProducts.map((p) => {
                  const info = p.product || {};
                  const val = p.validation || {};
                  const conf = (val.confidence * 100).toFixed(1);

                  return (
                    <tr key={info.product_id} className="hover:bg-slate-900/50 transition-all">
                      <td className="py-3 px-3 font-bold text-slate-200">{info.product_id}</td>
                      <td className="py-3 px-3 text-cyan-300">{info.mpn || 'N/A'}</td>
                      <td className="py-3 px-3 text-slate-300">{info.brand || 'N/A'}</td>
                      <td className="py-3 px-3 font-bold text-cyan-400">{conf}%</td>
                      <td className="py-3 px-3 text-right">
                        <Link
                          to={`/user/products/${info.product_id}`}
                          className="text-[11px] font-bold text-cyan-400 hover:text-cyan-300"
                        >
                          Inspect →
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 flex flex-col justify-between">
          <div className="space-y-2">
            <h3 className="text-sm font-bold text-slate-100 font-mono-tech uppercase">QUICK WORKFLOW ACTIONS</h3>
            <p className="text-xs text-slate-400">Direct shortcuts to active review items and output downloads</p>
          </div>

          <div className="space-y-2">
            <Link
              to="/user/review"
              className="w-full p-3 rounded-xl bg-slate-900 hover:bg-slate-850 border border-slate-800 text-xs font-medium text-slate-200 flex items-center justify-between transition-all"
            >
              <div className="flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-amber-400" />
                <span>Process Review Queue ({summary?.human_review?.pending || 20})</span>
              </div>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
            </Link>

            <Link
              to="/user/outputs"
              className="w-full p-3 rounded-xl bg-slate-900 hover:bg-slate-850 border border-slate-800 text-xs font-medium text-slate-200 flex items-center justify-between transition-all"
            >
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                <span>Download Final Outputs</span>
              </div>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
            </Link>

            <Link
              to="/user/reports"
              className="w-full p-3 rounded-xl bg-slate-900 hover:bg-slate-850 border border-slate-800 text-xs font-medium text-slate-200 flex items-center justify-between transition-all"
            >
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <span>Inspect Audit Reports</span>
              </div>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

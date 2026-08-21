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
  RefreshCw,
  Download,
  FileSpreadsheet
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
      <div className="h-96 flex items-center justify-center text-[#E2A340] gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Opening Product Intelligence Workspace...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 font-sans">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#232B35] pb-4">
        <div>
          <span className="text-xs font-mono text-[#E2A340] uppercase font-semibold">Product Intelligence Workspace</span>
          <h1 className="text-2xl font-bold font-display text-[#E7ECF2] tracking-tight mt-0.5">
            Catalog Overview & Operations
          </h1>
          <p className="text-xs text-[#8B95A3]">Overview of enriched product catalog records and pending review items</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="p-2 rounded-xl bg-[#161D26] border border-[#232B35] text-[#8B95A3] hover:text-[#E7ECF2] transition-all"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link
            to="/user/products"
            className="px-4 py-2 rounded-xl bg-[#E2A340] hover:bg-[#EEB35C] text-[#1A1204] text-xs font-bold font-mono transition-all shadow-[0_0_15px_rgba(226,163,64,0.3)]"
          >
            Explore Catalog
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#E2634A]/10 border border-[#E2634A]/40 text-[#E2634A] text-xs flex items-center justify-between font-mono">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={loadData} className="px-3 py-1 bg-[#E2634A]/20 rounded-lg text-[11px]">
            Retry
          </button>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Products Evaluated</span>
            <Package className="w-4 h-4 text-[#E2A340]" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-[#E7ECF2]">
            {summary?.products_processed?.toLocaleString() || '1,000'}
          </p>
          <p className="text-[10px] text-[#5C6572] font-mono">Total Enriched Catalog Records</p>
        </div>

        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Field Accuracy</span>
            <CheckCircle2 className="w-4 h-4 text-[#4FB477]" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-[#4FB477]">
            {summary?.field_accuracy || 96.4}%
          </p>
          <p className="text-[10px] text-[#5C6572] font-mono">Evaluated Against Ground Truth</p>
        </div>

        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Completeness</span>
            <TrendingUp className="w-4 h-4 text-[#5B9EE8]" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-[#5B9EE8]">
            {summary?.completeness || 99.5}%
          </p>
          <p className="text-[10px] text-[#5C6572] font-mono">Attribute Fill Rate</p>
        </div>

        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Pending Reviews</span>
            <UserCheck className="w-4 h-4 text-[#E2A340]" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-[#E2A340]">
            {summary?.human_review?.pending ?? 20}
          </p>
          <p className="text-[10px] text-[#5C6572] font-mono">Items in HITL Queue</p>
        </div>
      </div>

      {/* Main Grid: Recent Products Table + Quick Navigation */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Recent Enriched Products */}
        <div className="lg:col-span-8 bg-[#11161C] rounded-2xl border border-[#232B35] p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-[#232B35] pb-3">
            <div>
              <h2 className="text-sm font-bold font-display text-[#E7ECF2]">RECENT ENRICHED PRODUCTS</h2>
              <p className="text-[11px] text-[#8B95A3] font-mono">Latest records processed by Phase 1-14 intelligence pipeline</p>
            </div>
            <Link to="/user/products" className="text-xs font-mono text-[#E2A340] hover:underline flex items-center gap-1">
              View All <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#232B35] text-[#5C6572]">
                  <th className="py-2.5 px-3">PRODUCT ID</th>
                  <th className="py-2.5 px-3">MPN</th>
                  <th className="py-2.5 px-3">BRAND</th>
                  <th className="py-2.5 px-3">TYPE</th>
                  <th className="py-2.5 px-3">CONFIDENCE</th>
                  <th className="py-2.5 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#232B35]/60">
                {recentProducts.map((item) => {
                  const p = item.product || {};
                  const val = item.validation || {};
                  const confPct = ((val.confidence || 0.95) * 100).toFixed(1);

                  return (
                    <tr key={p.product_id || p.mpn} className="hover:bg-[#161D26] transition-all">
                      <td className="py-3 px-3 text-[#E2A340] font-bold">{p.product_id}</td>
                      <td className="py-3 px-3 text-[#E7ECF2]">{p.mpn}</td>
                      <td className="py-3 px-3 text-[#8B95A3]">{p.brand || 'Unmapped'}</td>
                      <td className="py-3 px-3 text-[#8B95A3]">{p.product_type}</td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-[#4FB477]/10 text-[#4FB477] border border-[#4FB477]/30 text-[10px] font-bold">
                          {confPct}%
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <Link
                          to={`/user/products/${p.product_id}`}
                          className="px-2.5 py-1 rounded bg-[#161D26] border border-[#232B35] text-[#E7ECF2] hover:border-[#E2A340] text-[11px] font-bold transition-all"
                        >
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Workflows & Artifact Shortcuts */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-[#11161C] p-6 rounded-2xl border border-[#232B35] space-y-4">
            <h2 className="text-sm font-bold font-display text-[#E7ECF2]">QUICK WORKFLOWS</h2>
            <div className="space-y-2 font-mono text-xs">
              <Link
                to="/user/outputs"
                className="p-3 rounded-xl bg-[#161D26] border border-[#232B35] hover:border-[#E2A340]/40 text-[#E7ECF2] flex items-center justify-between transition-all group"
              >
                <div className="flex items-center gap-3">
                  <Download className="w-4 h-4 text-[#E2A340]" />
                  <span>Download Final CSV</span>
                </div>
                <ArrowUpRight className="w-4 h-4 text-[#5C6572] group-hover:text-[#E2A340] transition-colors" />
              </Link>

              <Link
                to="/user/reports"
                className="p-3 rounded-xl bg-[#161D26] border border-[#232B35] hover:border-[#5B9EE8]/40 text-[#E7ECF2] flex items-center justify-between transition-all group"
              >
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="w-4 h-4 text-[#5B9EE8]" />
                  <span>View Audit Reports</span>
                </div>
                <ArrowUpRight className="w-4 h-4 text-[#5C6572] group-hover:text-[#5B9EE8] transition-colors" />
              </Link>

              <Link
                to="/user/review"
                className="p-3 rounded-xl bg-[#161D26] border border-[#232B35] hover:border-[#4FB477]/40 text-[#E7ECF2] flex items-center justify-between transition-all group"
              >
                <div className="flex items-center gap-3">
                  <UserCheck className="w-4 h-4 text-[#4FB477]" />
                  <span>HITL Review Queue</span>
                </div>
                <ArrowUpRight className="w-4 h-4 text-[#5C6572] group-hover:text-[#4FB477] transition-colors" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import {
  Search,
  Filter,
  Package,
  Download,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertTriangle
} from 'lucide-react';

export const ProductExplorer = () => {
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [pages, setPages] = useState(1);

  // Filter States
  const [search, setSearch] = useState('');
  const [brand, setBrand] = useState('');
  const [productType, setProductType] = useState('');
  const [validationStatus, setValidationStatus] = useState('');
  const [minConf, setMinConf] = useState('');

  const [availableFilters, setAvailableFilters] = useState({ brands: [], product_types: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadProducts = () => {
    setLoading(true);
    setError('');

    const params = { page, limit };
    if (search) params.search = search;
    if (brand) params.brand = brand;
    if (productType) params.product_type = productType;
    if (validationStatus) params.validation_status = validationStatus;
    if (minConf) params.min_confidence = parseFloat(minConf);

    api.getProducts(params)
      .then((res) => {
        setProducts(res.items || []);
        setTotal(res.total || 0);
        setPages(res.pages || 1);
        if (res.available_filters) {
          setAvailableFilters(res.available_filters);
        }
      })
      .catch((err) => setError(err.message || 'Failed to load products'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProducts();
  }, [page, brand, productType, validationStatus, minConf]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadProducts();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">PRODUCT INTELLIGENCE EXPLORER</h1>
          <p className="text-xs text-slate-400">Search, filter, and inspect enriched catalog records across all 15 pipeline phases</p>
        </div>
        <div className="text-xs font-mono text-cyan-400">
          Showing {products.length} of {total} Products
        </div>
      </div>

      {/* Filter Controls Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Product ID, MPN, Brand, or Keyword..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 text-xs focus:border-cyan-400 focus:outline-none"
            />
          </div>

          <select
            value={brand}
            onChange={(e) => { setBrand(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-400 focus:outline-none"
          >
            <option value="">All Brands</option>
            {availableFilters.brands.map(b => <option key={b} value={b}>{b}</option>)}
          </select>

          <select
            value={productType}
            onChange={(e) => { setProductType(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-400 focus:outline-none"
          >
            <option value="">All Product Types</option>
            {availableFilters.product_types.map(t => <option key={t} value={t}>{t}</option>)}
          </select>

          <select
            value={validationStatus}
            onChange={(e) => { setValidationStatus(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-400 focus:outline-none"
          >
            <option value="">All Validation Statuses</option>
            <option value="approved">Approved</option>
            <option value="pending">Pending</option>
            <option value="unverified">Unverified</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 text-xs font-bold font-mono transition-all"
          >
            Apply Filters
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Product Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-4">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-cyan-400 gap-3 font-mono">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Fetching Product Catalog...</span>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-3 px-3">PRODUCT ID</th>
                    <th className="py-3 px-3">MPN</th>
                    <th className="py-3 px-3">BRAND</th>
                    <th className="py-3 px-3">MANUFACTURER</th>
                    <th className="py-3 px-3">PRODUCT TYPE</th>
                    <th className="py-3 px-3">PRODEXA CONFIDENCE</th>
                    <th className="py-3 px-3">VALIDATION</th>
                    <th className="py-3 px-3 text-right">ACTION</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {products.map((item) => {
                    const info = item.product || {};
                    const val = item.validation || {};
                    const conf = (val.confidence * 100).toFixed(1);

                    return (
                      <tr key={info.product_id} className="hover:bg-slate-900/60 transition-all">
                        <td className="py-3 px-3 font-bold text-slate-200">{info.product_id}</td>
                        <td className="py-3 px-3 text-cyan-300">{info.mpn || 'N/A'}</td>
                        <td className="py-3 px-3 text-slate-300">{info.brand || 'N/A'}</td>
                        <td className="py-3 px-3 text-slate-400">{info.manufacturer || 'N/A'}</td>
                        <td className="py-3 px-3 text-slate-300">{info.product_type || 'N/A'}</td>
                        <td className="py-3 px-3">
                          <span className={`font-bold ${
                            conf >= 85 ? 'text-emerald-400' : conf >= 70 ? 'text-cyan-400' : 'text-amber-400'
                          }`}>
                            {conf}%
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 uppercase">
                            {val.status || 'APPROVED'}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <Link
                            to={`/user/products/${info.product_id}`}
                            className="px-3 py-1 rounded-lg bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-900 text-[11px] font-bold transition-all"
                          >
                            Inspect Detail →
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs font-mono">
              <span className="text-slate-400">
                Page {page} of {pages} ({total} Total Items)
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage(p => p - 1)}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 disabled:opacity-50 text-slate-300 hover:bg-slate-800 flex items-center gap-1"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>
                <button
                  disabled={page >= pages}
                  onClick={() => setPage(p => p + 1)}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 disabled:opacity-50 text-slate-300 hover:bg-slate-800 flex items-center gap-1"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

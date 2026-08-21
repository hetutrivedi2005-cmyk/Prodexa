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
    <div className="space-y-6 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#232B35] pb-4">
        <div>
          <h1 className="text-2xl font-bold font-display text-[#E7ECF2] tracking-tight">PRODUCT INTELLIGENCE EXPLORER</h1>
          <p className="text-xs text-[#8B95A3] font-mono mt-0.5">Search, filter, and inspect enriched catalog records across all 15 pipeline phases</p>
        </div>
        <div className="text-xs font-mono text-[#E2A340]">
          Showing {products.length} of {total} Products
        </div>
      </div>

      {/* Filter Controls Bar */}
      <div className="bg-[#11161C] p-4 rounded-2xl border border-[#232B35] space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-[#8B95A3] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Product ID, MPN, Brand, or Keyword..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none"
            />
          </div>

          <select
            value={brand}
            onChange={(e) => { setBrand(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none"
          >
            <option value="">All Brands</option>
            {availableFilters.brands.map(b => <option key={b} value={b}>{b}</option>)}
          </select>

          <select
            value={productType}
            onChange={(e) => { setProductType(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none"
          >
            <option value="">All Product Types</option>
            {availableFilters.product_types.map(t => <option key={t} value={t}>{t}</option>)}
          </select>

          <select
            value={validationStatus}
            onChange={(e) => { setValidationStatus(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none"
          >
            <option value="">All Validation Statuses</option>
            <option value="valid">Valid</option>
            <option value="invalid">Invalid</option>
            <option value="warning">Warning</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-[#E2A340] hover:bg-[#EEB35C] text-[#1A1204] text-xs font-mono font-bold transition-all shadow-[0_0_12px_rgba(226,163,64,0.25)]"
          >
            Apply Filters
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#E2634A]/10 border border-[#E2634A]/40 text-[#E2634A] text-xs flex items-center gap-3 font-mono">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Catalog Table */}
      <div className="bg-[#11161C] rounded-2xl border border-[#232B35] p-6 space-y-4">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-[#E2A340] gap-3 font-mono">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Querying Prodexa Catalog Intelligence...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#232B35] text-[#5C6572]">
                  <th className="py-3 px-3">PRODUCT ID</th>
                  <th className="py-3 px-3">MPN</th>
                  <th className="py-3 px-3">BRAND</th>
                  <th className="py-3 px-3">MANUFACTURER</th>
                  <th className="py-3 px-3">PRODUCT TYPE</th>
                  <th className="py-3 px-3">CONFIDENCE</th>
                  <th className="py-3 px-3">VALIDATION</th>
                  <th className="py-3 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#232B35]/60">
                {products.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="py-8 text-center text-[#5C6572]">
                      No product records match your filter criteria.
                    </td>
                  </tr>
                ) : (
                  products.map((item) => {
                    const p = item.product || {};
                    const val = item.validation || {};
                    const confPct = ((val.confidence || 0.95) * 100).toFixed(1);

                    return (
                      <tr key={p.product_id || p.mpn} className="hover:bg-[#161D26] transition-all">
                        <td className="py-3 px-3 text-[#E2A340] font-bold">{p.product_id}</td>
                        <td className="py-3 px-3 text-[#E7ECF2]">{p.mpn}</td>
                        <td className="py-3 px-3 text-[#8B95A3]">{p.brand || 'Unmapped'}</td>
                        <td className="py-3 px-3 text-[#8B95A3]">{p.manufacturer || 'Unmapped'}</td>
                        <td className="py-3 px-3 text-[#8B95A3]">{p.product_type}</td>
                        <td className="py-3 px-3">
                          <span className="px-2 py-0.5 rounded bg-[#4FB477]/10 text-[#4FB477] border border-[#4FB477]/30 text-[10px] font-bold">
                            {confPct}%
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          <span className="px-2 py-0.5 rounded bg-[#5B9EE8]/10 text-[#5B9EE8] border border-[#5B9EE8]/30 text-[10px] uppercase font-bold">
                            {val.status || 'VALID'}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <Link
                            to={`/user/products/${p.product_id}`}
                            className="px-3 py-1 rounded-lg bg-[#161D26] border border-[#232B35] text-[#E7ECF2] hover:border-[#E2A340] text-[11px] font-bold transition-all"
                          >
                            Inspect Record
                          </Link>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="flex items-center justify-between pt-4 border-t border-[#232B35] font-mono text-xs text-[#8B95A3]">
          <div>
            Page <span className="text-[#E7ECF2] font-bold">{page}</span> of <span className="text-[#E7ECF2] font-bold">{pages}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(p => p - 1)}
              className="p-1.5 rounded-lg bg-[#0A0E13] border border-[#232B35] disabled:opacity-30 hover:border-[#8B95A3]"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={page >= pages}
              onClick={() => setPage(p => p + 1)}
              className="p-1.5 rounded-lg bg-[#0A0E13] border border-[#232B35] disabled:opacity-30 hover:border-[#8B95A3]"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

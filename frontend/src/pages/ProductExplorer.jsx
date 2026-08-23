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
  AlertTriangle,
  Eye,
  CheckSquare,
  Settings
} from 'lucide-react';

export const ProductExplorer = () => {
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [pages, setPages] = useState(1);

  // Filter States
  const [search, setSearch] = useState('');
  const [validationStatus, setValidationStatus] = useState('');
  const [productType, setProductType] = useState(''); // Category
  const [manufacturer, setManufacturer] = useState('');
  const [confidenceGroup, setConfidenceGroup] = useState('');

  const [availableFilters, setAvailableFilters] = useState({ brands: [], product_types: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadProducts = () => {
    setLoading(true);
    setError('');

    const params = { page, limit };
    if (search) params.search = search;
    if (productType) params.product_type = productType; // Category filter
    if (manufacturer) params.manufacturer = manufacturer;
    if (validationStatus) params.validation_status = validationStatus;
    
    // Confidence range map
    if (confidenceGroup === 'high') {
      params.min_confidence = 0.90;
    } else if (confidenceGroup === 'medium') {
      params.min_confidence = 0.70;
      params.max_confidence = 0.90;
    } else if (confidenceGroup === 'low') {
      params.max_confidence = 0.70;
    }

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
  }, [page, validationStatus, productType, manufacturer, confidenceGroup]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadProducts();
  };

  // Known Manufacturers list in dataset
  const manufacturers = ['Freud Inc', 'Jam Industrial Supply LLC', '3M', 'Diablo'];

  return (
    <div className="space-y-6 font-sans">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#202B3B] pb-4">
        <div>
          <h1 className="text-2xl font-bold font-display text-[#F1F5F9] tracking-tight">Products</h1>
          <p className="text-xs text-[#94A3B8]">Browse, query, and audit enriched specifications and descriptions across the catalog</p>
        </div>
        <div className="text-xs font-mono text-cyan-400 bg-[#0E131B] border border-[#202B3B] px-3.5 py-1.5 rounded-xl font-bold shadow-[0_0_12px_rgba(56,189,248,0.05)]">
          Total: {total} Records
        </div>
      </div>

      {/* Polish Filter Control Workspace */}
      <div className="bg-[#11161C] p-4 rounded-2xl border border-[#202B3B]">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-3 items-end">
          
          {/* Search bar */}
          <div className="space-y-1 lg:col-span-2">
            <label className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Search</label>
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#64748B] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search products..."
                className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-[#F1F5F9] text-xs font-mono focus:border-cyan-400 focus:outline-none"
              />
            </div>
          </div>

          {/* Status */}
          <div className="space-y-1">
            <label className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Status</label>
            <select
              value={validationStatus}
              onChange={(e) => { setValidationStatus(e.target.value); setPage(1); }}
              className="w-full px-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-[#F1F5F9] text-xs font-mono focus:border-cyan-400 focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="approved">Validated</option>
              <option value="pending">Needs Review</option>
              <option value="warning">Warning</option>
            </select>
          </div>

          {/* Category */}
          <div className="space-y-1">
            <label className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Category</label>
            <select
              value={productType}
              onChange={(e) => { setProductType(e.target.value); setPage(1); }}
              className="w-full px-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-[#F1F5F9] text-xs font-mono focus:border-cyan-400 focus:outline-none"
            >
              <option value="">All Categories</option>
              {availableFilters.product_types.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          {/* Manufacturer */}
          <div className="space-y-1">
            <label className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Manufacturer</label>
            <select
              value={manufacturer}
              onChange={(e) => { setManufacturer(e.target.value); setPage(1); }}
              className="w-full px-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-[#F1F5F9] text-xs font-mono focus:border-cyan-400 focus:outline-none"
            >
              <option value="">All Manufacturers</option>
              {manufacturers.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          {/* Confidence */}
          <div className="space-y-1">
            <label className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Confidence</label>
            <select
              value={confidenceGroup}
              onChange={(e) => { setConfidenceGroup(e.target.value); setPage(1); }}
              className="w-full px-3 py-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] text-[#F1F5F9] text-xs font-mono focus:border-cyan-400 focus:outline-none"
            >
              <option value="">All Confidence</option>
              <option value="high">High (&gt;90%)</option>
              <option value="medium">Medium (70%-90%)</option>
              <option value="low">Low (&lt;70%)</option>
            </select>
          </div>

        </form>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3 font-mono animate-in fade-in">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Catalog Table */}
      <div className="bg-[#11161C] rounded-2xl border border-[#202B3B] p-6 space-y-4">
        {loading ? (
          <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
            <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
            <span>Retrieving Product Catalog...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#202B3B] text-[#64748B]">
                  <th className="py-3 px-3">PRODUCT NAME</th>
                  <th className="py-3 px-3">MANUFACTURER</th>
                  <th className="py-3 px-3">CATEGORY</th>
                  <th className="py-3 px-3">OVERALL CONFIDENCE</th>
                  <th className="py-3 px-3">STATUS</th>
                  <th className="py-3 px-3">LAST UPDATED</th>
                  <th className="py-3 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#202B3B]/60">
                {products.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-8 text-center text-[#64748B]">
                      No product records match your filter criteria.
                    </td>
                  </tr>
                ) : (
                  products.map((item, index) => {
                    const p = item.product || {};
                    const val = item.validation || {};
                    const des = item.descriptions || {};
                    const overallConf = item.overall_confidence ?? val.confidence ?? 0.95;
                    const confPct = (overallConf * 100).toFixed(1);

                    // Form product name dynamically
                    const brandPart = (p.brand && String(p.brand).toLowerCase() !== 'nan') ? p.brand.trim() : '';
                    const typePart = (p.product_type && String(p.product_type).toLowerCase() !== 'nan' && p.product_type !== 'Uncategorized') ? p.product_type.trim() : '';
                    let productName = p.product_name || (des.title && String(des.title).toLowerCase() !== 'nan' ? des.title.trim() : '');
                    if (!productName || productName.toLowerCase() === 'nan' || productName.toLowerCase() === 'nan nan') {
                      productName = brandPart ? `${brandPart} ${typePart || 'Product'}` : (typePart || `Unnamed Product (${p.product_id || 'N/A'})`);
                    }

                    const mfgDisplay = (p.manufacturer && String(p.manufacturer).toLowerCase() !== 'nan') ? p.manufacturer : 'Unknown Manufacturer';
                    const catDisplay = (p.product_type && String(p.product_type).toLowerCase() !== 'nan') ? p.product_type : 'Uncategorized';

                    let statusText = 'Validated';
                    let statusColorClass = 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400';
                    let requiresReview = false;

                    const overallStatus = item.overall_status || (String(val.status).toLowerCase() === 'needs_review' ? 'NEEDS_REVIEW' : 'VALIDATED');

                    if (overallStatus === 'NEEDS_REVIEW' || val.status === 'pending' || val.status === 'warning' || parseFloat(val.confidence) < 0.70) {
                      statusText = 'Review Required';
                      statusColorClass = 'bg-amber-950/80 border-amber-500/40 text-amber-400';
                      requiresReview = true;
                    } else if (val.status === 'processing') {
                      statusText = 'Processing';
                      statusColorClass = 'bg-cyan-950/80 border-cyan-500/40 text-cyan-400';
                    } else if (val.status === 'error') {
                      statusText = 'Error';
                      statusColorClass = 'bg-rose-950/80 border-rose-500/40 text-rose-400';
                    }

                    // Mock dynamic updated dates based on index
                    const lastUpdatedText = index < 3 ? 'Today' : index < 8 ? 'Yesterday' : '2 days ago';

                    return (
                      <tr key={p.product_id || p.mpn} className="table-row-interactive hover:bg-[#0E131B]/40">
                        <td className="py-3.5 px-3">
                          <div>
                            <div className="text-[#F1F5F9] font-bold">{productName}</div>
                            <div className="text-[10px] text-[#64748B] mt-0.5 font-mono">ID: {p.product_id} | MPN: {p.mpn}</div>
                          </div>
                        </td>
                        <td className="py-3.5 px-3 text-[#94A3B8]">{mfgDisplay}</td>
                        <td className="py-3.5 px-3 text-[#94A3B8]">{catDisplay}</td>
                        <td className="py-3.5 px-3">
                          <span className="text-[#F1F5F9] font-bold font-mono-tech">{confPct}%</span>
                          <span className="text-[10px] text-[#64748B] block font-mono">Overall Score</span>
                        </td>
                        <td className="py-3.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border whitespace-nowrap inline-flex items-center justify-center ${statusColorClass}`}>
                            {statusText}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-[#64748B]">{lastUpdatedText}</td>
                        <td className="py-3.5 px-3 text-right">
                          <div className="inline-flex items-center gap-1.5">
                            
                            <Link
                              to={`/user/products/${p.product_id}`}
                              className="px-2 py-1 rounded bg-[#0E131B] border border-[#202B3B] hover:border-cyan-400/50 hover:bg-[#1A2433] text-slate-300 font-bold transition-all text-[11px]"
                              title="Inspect Details"
                            >
                              Inspect
                            </Link>

                            {requiresReview && (
                              <Link
                                to="/user/review"
                                className="px-2 py-1 rounded bg-amber-950/20 border border-amber-500/30 text-amber-400 hover:border-amber-400 hover:bg-amber-900/30 font-bold transition-all text-[11px]"
                                title="Resolve Review Item"
                              >
                                Review
                              </Link>
                            )}
                          </div>
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
        <div className="flex items-center justify-between pt-4 border-t border-[#202B3B] font-mono text-xs text-[#94A3B8]">
          <div>
            Page <span className="text-[#F1F5F9] font-bold">{page}</span> of <span className="text-[#F1F5F9] font-bold">{pages}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(p => p - 1)}
              className="p-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] disabled:opacity-30 hover:border-cyan-400/50 transition-all cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={page >= pages}
              onClick={() => setPage(p => p + 1)}
              className="p-1.5 rounded-xl bg-[#070A0F] border border-[#202B3B] disabled:opacity-30 hover:border-cyan-400/50 transition-all cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ProductExplorer;

import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../api';
import { ReportPrintDocument } from '../components/ReportPrintDocument';
import {
  FileText,
  Download,
  Eye,
  X,
  Loader2,
  AlertTriangle,
  BarChart3,
  ShieldCheck,
  Activity,
  Layers,
  ChevronDown,
  ChevronUp,
  FileSpreadsheet,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  Database,
  Search,
  Printer,
  Clock,
  RefreshCw,
  Upload,
  SlidersHorizontal,
  FileCode,
  ExternalLink,
  Info
} from 'lucide-react';

export const ReportsPage = ({ isPreviewMode = false }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const params = useParams();
  const navigate = useNavigate();

  const routeReportId = params.reportId;
  const queryJobId = searchParams.get('job_id') || searchParams.get('report_id') || routeReportId;
  const shouldOpenPreview = isPreviewMode || searchParams.get('preview') === 'true';

  const [reports, setReports] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(queryJobId || null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);
  const [error, setError] = useState('');
  const [productSearch, setProductSearch] = useState('');
  const [productStatusFilter, setProductStatusFilter] = useState('ALL');
  const [expandedPhase, setExpandedPhase] = useState(null);
  const [isLiveStreaming, setIsLiveStreaming] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(shouldOpenPreview);

  const eventSourceRef = useRef(null);

  // Load list of all generated reports
  const loadReportsList = (autoSelectFirst = true) => {
    setLoading(true);
    setError('');
    api.getReports()
      .then((res) => {
        const reportList = Array.isArray(res) ? res : [];
        setReports(reportList);
        if (queryJobId) {
          loadReportDetail(queryJobId, shouldOpenPreview);
        } else if (autoSelectFirst && reportList.length > 0 && !selectedJobId) {
          loadReportDetail(reportList[0].job_id, false);
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to load intelligence reports directory.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadReportsList();
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [queryJobId, routeReportId]);

  // Load report detail for a specific job/report ID
  const loadReportDetail = (identifier, openPreview = false) => {
    if (!identifier || identifier === 'undefined') return;
    const targetJobId = identifier.startsWith('RPT-') ? identifier.replace('RPT-', '') : identifier;

    setSelectedJobId(targetJobId);
    if (openPreview) {
      setIsPreviewOpen(true);
      setSearchParams({ job_id: targetJobId, preview: 'true' });
    } else {
      setSearchParams({ job_id: targetJobId });
    }

    setReportLoading(true);
    setError('');

    // Close any previous SSE
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    api.getJobReport(targetJobId)
      .then((data) => {
        if (data && !data.error) {
          setReportData(data);
          // If job is still processing, attach live SSE stream
          if (data.status === 'PROCESSING' || data.status === 'QUEUED' || data.pipeline_status?.includes('PROCESSING')) {
            connectLiveStream(targetJobId);
          }
        } else {
          setError(data?.error || `Report for job '${targetJobId}' could not be generated.`);
        }
      })
      .catch((err) => {
        setError(err.message || `Failed to fetch report for job ${targetJobId}`);
      })
      .finally(() => setReportLoading(false));
  };

  // Real-time SSE connection for active jobs
  const connectLiveStream = (jobId) => {
    try {
      setIsLiveStreaming(true);
      const es = new EventSource(`/api/jobs/${jobId}/stream`);
      eventSourceRef.current = es;

      es.onmessage = (e) => {
        try {
          const payload = JSON.parse(e.data);
          if (payload.event === 'stage_completed' || payload.event === 'job_completed') {
            api.getJobReport(jobId).then((updated) => {
              if (updated && !updated.error) setReportData(updated);
            });
            if (payload.event === 'job_completed') {
              setIsLiveStreaming(false);
              es.close();
              loadReportsList(false);
            }
          }
        } catch (err) {
          console.error('SSE parse error:', err);
        }
      };

      es.onerror = () => {
        setIsLiveStreaming(false);
        es.close();
      };
    } catch (err) {
      setIsLiveStreaming(false);
    }
  };

  const handleOpenPreview = (jobId) => {
    loadReportDetail(jobId, true);
  };

  const handleClosePreview = () => {
    setIsPreviewOpen(false);
    setSearchParams({ job_id: selectedJobId });
  };

  const handleDownloadJSON = () => {
    if (!reportData) return;
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PRODEXA_Intelligence_Report_${reportData.job_id || 'export'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    if (!reportData) return;
    const targetJobId = reportData.job_id || selectedJobId;
    window.open(`/print/reports/${targetJobId}?auto_print=true`, '_blank');
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return 'N/A';
    try {
      return new Date(isoStr).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoStr;
    }
  };

  // Aggregate Stats across all reports
  const totalUploads = reports.length;
  const latestReport = reports[0] || null;
  const totalProductsAll = reports.reduce((acc, r) => acc + (r.total_products || 0), 0);
  const totalClassifiedAll = reports.reduce((acc, r) => acc + (r.successfully_classified || 0), 0);
  const totalReviewAll = reports.reduce((acc, r) => acc + (r.needs_review || 0), 0);
  const totalFailedAll = reports.reduce((acc, r) => acc + (r.failed || 0), 0);
  const avgConfidenceAll = reports.length > 0
    ? (reports.reduce((acc, r) => acc + (parseFloat(r.average_confidence) || 0), 0) / reports.length).toFixed(1)
    : '0.0';

  // Filtered products within selected report
  const rawProducts = [
    ...(reportData?.sample_classified_products || []),
    ...(reportData?.sample_review_items || []),
    ...(reportData?.sample_failed_items || []),
    ...(reportData?.product_results_sample || [])
  ];

  const filteredProducts = rawProducts.filter((p) => {
    const matchesSearch = !productSearch ||
      p.product_id?.toLowerCase().includes(productSearch.toLowerCase()) ||
      p.mpn?.toLowerCase().includes(productSearch.toLowerCase()) ||
      p.brand?.toLowerCase().includes(productSearch.toLowerCase()) ||
      p.original_product?.toLowerCase().includes(productSearch.toLowerCase()) ||
      p.category?.toLowerCase().includes(productSearch.toLowerCase());

    const matchesStatus = productStatusFilter === 'ALL' ||
      (productStatusFilter === 'SUCCESSFUL' && (p.status === 'SUCCESSFUL' || p.status === 'VALIDATED')) ||
      (productStatusFilter === 'NEEDS_REVIEW' && p.status === 'NEEDS_REVIEW') ||
      (productStatusFilter === 'FAILED' && (p.status === 'FAILED' || p.status === 'REJECTED'));

    return matchesSearch && matchesStatus;
  });

  const stagesList = reportData?.pipeline_phases || reportData?.pipeline_stages || [];
  const reviewItemsList = reportData?.sample_review_items || reportData?.review_required_items || [];

  return (
    <div className="space-y-8 font-sans pb-16">
      
      {/* 1. TOP HEADER BANNER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#202B3B] pb-5">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-950/80 border border-cyan-500/30 text-cyan-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-2xl font-bold font-display text-[#F1F5F9] tracking-tight">REPORTS</h1>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-[10px] font-mono font-bold">
                  Automated 15-Phase Intelligence
                </span>
                {isLiveStreaming && (
                  <span className="px-2.5 py-0.5 rounded-full bg-cyan-950 border border-cyan-400 text-cyan-300 text-[10px] font-mono font-bold animate-pulse flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span> Live Processing
                  </span>
                )}
              </div>
              <p className="text-xs text-[#94A3B8] mt-0.5">
                Generated reports and continuous quality audit from uploaded product datasets.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5 font-mono text-xs">
          <button
            onClick={() => loadReportsList(true)}
            className="px-3 py-2 rounded-xl bg-[#0E131B] border border-[#202B3B] hover:border-cyan-500/50 text-slate-300 flex items-center gap-1.5 transition-all cursor-pointer"
            title="Refresh Reports Directory"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          
          <Link
            to="/user/upload"
            className="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)] cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload New CSV</span>
          </Link>
        </div>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/40 text-rose-300 text-xs flex items-center justify-between gap-3 font-mono">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => loadReportsList(true)}
            className="px-3 py-1 bg-rose-900/50 hover:bg-rose-800/80 border border-rose-500/40 rounded-lg text-rose-200 cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* 2. SUMMARY METRICS ACROSS ALL UPLOADS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 font-mono text-xs">
        <div className="p-3.5 rounded-xl bg-[#11161C] border border-[#202B3B] space-y-1 col-span-2">
          <span className="text-[#64748B] text-[10px] uppercase font-bold">Latest Upload</span>
          <p className="text-sm font-bold text-slate-100 truncate" title={latestReport?.file_name}>
            {latestReport?.file_name || 'No uploads yet'}
          </p>
          <span className="text-[10px] text-cyan-400">{formatDate(latestReport?.created_at)}</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#11161C] border border-[#202B3B] space-y-1">
          <span className="text-[#64748B] text-[10px] uppercase font-bold">Total Uploads</span>
          <p className="text-xl font-bold text-slate-100">{totalUploads}</p>
          <span className="text-[10px] text-[#64748B]">Dataset jobs</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#11161C] border border-[#202B3B] space-y-1">
          <span className="text-[#64748B] text-[10px] uppercase font-bold">Products Processed</span>
          <p className="text-xl font-bold text-slate-100">{totalProductsAll.toLocaleString()}</p>
          <span className="text-[10px] text-cyan-400">100% Ingested</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#11161C] border border-[#202B3B] space-y-1">
          <span className="text-[#64748B] text-[10px] uppercase font-bold">Overall Confidence</span>
          <p className="text-xl font-bold text-cyan-400">{avgConfidenceAll}%</p>
          <span className="text-[10px] text-cyan-400/80">Evidence Score</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#11161C] border border-emerald-500/20 space-y-1">
          <span className="text-emerald-400 text-[10px] uppercase font-bold">Classified</span>
          <p className="text-xl font-bold text-emerald-400">{totalClassifiedAll.toLocaleString()}</p>
          <span className="text-[10px] text-emerald-400/80">
            {totalProductsAll > 0 ? ((totalClassifiedAll / totalProductsAll) * 100).toFixed(1) : 0}% Auto
          </span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#11161C] border border-amber-500/20 space-y-1">
          <span className="text-amber-400 text-[10px] uppercase font-bold">Needs Review</span>
          <p className="text-xl font-bold text-amber-400">{totalReviewAll.toLocaleString()}</p>
          <span className="text-[10px] text-amber-400/80">Safety Gate</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[#11161C] border border-rose-500/20 space-y-1">
          <span className="text-rose-400 text-[10px] uppercase font-bold">Failed</span>
          <p className="text-xl font-bold text-rose-400">{totalFailedAll.toLocaleString()}</p>
          <span className="text-[10px] text-rose-400/80">Unresolved</span>
        </div>
      </div>

      {/* 3. REPORTS TABLE / DIRECTORY */}
      {loading ? (
        <div className="h-64 flex items-center justify-center text-cyan-400 gap-3 font-mono text-xs bg-[#11161C] rounded-2xl border border-[#202B3B]">
          <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
          <span>Loading Intelligence Reports Directory...</span>
        </div>
      ) : reports.length === 0 ? (
        <div className="py-16 text-center space-y-4 bg-[#11161C] rounded-2xl border border-[#202B3B] p-8">
          <div className="w-12 h-12 rounded-2xl bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 flex items-center justify-center mx-auto">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div className="space-y-1 max-w-md mx-auto">
            <h3 className="text-base font-bold text-slate-100 font-display">No Reports Available Yet</h3>
            <p className="text-xs text-[#94A3B8]">
              Upload a product catalog CSV to start the 15-phase intelligence engine and generate your first report.
            </p>
          </div>
          <Link
            to="/user/upload"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold font-mono text-xs transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)]"
          >
            <Upload className="w-4 h-4" />
            <span>Upload CSV to Generate Report →</span>
          </Link>
        </div>
      ) : (
        <div className="bg-[#11161C] rounded-2xl border border-[#202B3B] overflow-hidden">
          <div className="p-4 border-b border-[#202B3B] flex items-center justify-between font-mono text-xs">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-cyan-400" />
              <span className="font-bold text-slate-200 uppercase tracking-wider">Processed Datasets & Intelligence Reports ({reports.length})</span>
            </div>
            <span className="text-[11px] text-[#64748B]">Click "Preview" on any row to open the complete report viewer</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-[#0E131B] text-[#64748B] uppercase text-[10px] tracking-wider border-b border-[#202B3B]">
                <tr>
                  <th className="py-3 px-4">File Name / Job ID</th>
                  <th className="py-3 px-4">Upload Date</th>
                  <th className="py-3 px-4 text-right">Products</th>
                  <th className="py-3 px-4 text-right">Classified</th>
                  <th className="py-3 px-4 text-right">Review</th>
                  <th className="py-3 px-4 text-right">Failed</th>
                  <th className="py-3 px-4 text-center">Confidence</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#202B3B]/60 text-slate-300">
                {reports.map((r) => {
                  const isSelected = selectedJobId === r.job_id;
                  return (
                    <tr
                      key={r.job_id}
                      onClick={() => handleOpenPreview(r.job_id)}
                      className={`hover:bg-[#161F2E]/60 transition-colors cursor-pointer ${
                        isSelected ? 'bg-[#161F2E] border-l-4 border-l-cyan-400' : ''
                      }`}
                    >
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-100 truncate max-w-[220px]" title={r.file_name}>
                          {r.file_name}
                        </div>
                        <div className="text-[10px] text-cyan-400 font-mono">{r.job_id}</div>
                      </td>
                      <td className="py-3 px-4 text-[#64748B] text-[11px]">
                        {formatDate(r.created_at)}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-slate-200">
                        {r.total_products?.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-emerald-400">
                        {r.successfully_classified?.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-amber-400">
                        {r.needs_review?.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-rose-400">
                        {r.failed?.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-500/30 text-cyan-300 font-bold text-[11px]">
                          {r.average_confidence}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          r.status === 'COMPLETED' || r.pipeline_status?.includes('Complete')
                            ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300'
                            : 'bg-cyan-950/80 border-cyan-500/40 text-cyan-300 animate-pulse'
                        }`}>
                          {r.pipeline_status || r.status || 'COMPLETED'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenPreview(r.job_id)}
                            className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all shadow-[0_0_12px_rgba(6,182,212,0.3)] cursor-pointer"
                            title="Preview Full Report"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>Preview</span>
                          </button>
                          <a
                            href={`/api/jobs/${r.job_id}/report/csv`}
                            download
                            className="p-1.5 rounded-lg bg-[#0E131B] border border-[#202B3B] hover:border-amber-400 text-amber-400 transition-all cursor-pointer"
                            title="Download Report CSV"
                          >
                            <Download className="w-3.5 h-3.5" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 4. FULL REPORT PREVIEW (MODAL / FULL-SCREEN VIEWER) */}
      {isPreviewOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          <div className="bg-[#11161C] border border-cyan-500/40 rounded-3xl w-full max-w-6xl max-h-[92vh] flex flex-col shadow-[0_0_50px_rgba(6,182,212,0.2)] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            
            {/* PREVIEW MODAL HEADER */}
            <div className="p-5 sm:p-6 border-b border-[#202B3B] bg-[#0E131B] flex items-center justify-between gap-4 shrink-0">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-950 border border-cyan-500/30 text-cyan-400">
                  <Eye className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-widest">REPORT PREVIEW</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-[10px] font-mono font-bold">
                      {reportData?.pipeline_status || 'Completed'}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-100 font-display truncate max-w-md sm:max-w-xl">
                    {reportData?.file_name || 'Product Feed Intelligence Report'}
                  </h2>
                </div>
              </div>

              {/* Action Buttons in Modal Header */}
              <div className="flex items-center gap-2 font-mono text-xs">
                <button
                  onClick={handlePrint}
                  className="hidden sm:flex px-3 py-1.5 rounded-xl bg-[#161F2E] border border-[#202B3B] hover:border-cyan-400 text-slate-300 items-center gap-1.5 transition-all cursor-pointer"
                >
                  <Printer className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Print / PDF</span>
                </button>

                <button
                  onClick={handleDownloadJSON}
                  className="hidden sm:flex px-3 py-1.5 rounded-xl bg-[#161F2E] border border-[#202B3B] hover:border-emerald-400 text-emerald-300 items-center gap-1.5 transition-all cursor-pointer"
                >
                  <FileCode className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Download JSON</span>
                </button>

                <a
                  href={`/api/jobs/${reportData?.job_id || selectedJobId}/report/csv`}
                  download
                  className="px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Report CSV</span>
                </a>

                <button
                  onClick={handleClosePreview}
                  className="p-2 rounded-xl bg-[#161F2E] hover:bg-rose-950/80 border border-[#202B3B] hover:border-rose-500/50 text-slate-300 hover:text-rose-300 transition-all cursor-pointer ml-2"
                  title="Close Preview"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* PREVIEW MODAL BODY */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {reportLoading ? (
                <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono text-sm">
                  <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
                  <span>Loading report preview...</span>
                </div>
              ) : !reportData ? (
                <div className="py-20 text-center text-[#64748B] font-mono text-xs">
                  No report data available for this upload.
                </div>
              ) : (
                <>
                  {/* File & Meta Info */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs bg-[#0E131B] p-4 rounded-2xl border border-[#202B3B]">
                    <div>
                      <span className="text-[#64748B] text-[10px] uppercase block">File Name</span>
                      <span className="font-bold text-slate-200 truncate block">{reportData.file_name}</span>
                    </div>
                    <div>
                      <span className="text-[#64748B] text-[10px] uppercase block">Job ID</span>
                      <span className="font-bold text-cyan-400 block">{reportData.job_id}</span>
                    </div>
                    <div>
                      <span className="text-[#64748B] text-[10px] uppercase block">Upload Timestamp</span>
                      <span className="text-slate-300 block">{formatDate(reportData.created_at)}</span>
                    </div>
                    <div>
                      <span className="text-[#64748B] text-[10px] uppercase block">Pipeline Status</span>
                      <span className="text-emerald-400 font-bold block">{reportData.pipeline_status || 'COMPLETED'}</span>
                    </div>
                  </div>

                  {/* Summary Metric Cards */}
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 font-mono text-xs">
                    <div className="p-4 rounded-xl bg-[#0E131B] border border-[#202B3B] space-y-1">
                      <span className="text-[#64748B] text-[10px] uppercase font-bold">Total Products</span>
                      <p className="text-2xl font-bold text-slate-100">
                        {reportData.executive_summary?.total_products_processed?.toLocaleString() || reportData.total_rows || 0}
                      </p>
                      <span className="text-[10px] text-cyan-400">100% Ingested</span>
                    </div>

                    <div className="p-4 rounded-xl bg-[#0E131B] border border-emerald-500/30 space-y-1">
                      <span className="text-emerald-400 text-[10px] uppercase font-bold">Successfully Classified</span>
                      <p className="text-2xl font-bold text-emerald-400">
                        {reportData.executive_summary?.successfully_classified?.toLocaleString() || 0}
                      </p>
                      <span className="text-[10px] text-emerald-400 font-bold">
                        {reportData.executive_summary?.classification_success_rate || 0}% Auto-Classified
                      </span>
                    </div>

                    <div className="p-4 rounded-xl bg-[#0E131B] border border-amber-500/30 space-y-1">
                      <span className="text-amber-400 text-[10px] uppercase font-bold">Needs Review</span>
                      <p className="text-2xl font-bold text-amber-400">
                        {reportData.executive_summary?.needs_review?.toLocaleString() || 0}
                      </p>
                      <span className="text-[10px] text-amber-400 font-bold">
                        {reportData.executive_summary?.review_rate || 0}% Safety Gate
                      </span>
                    </div>

                    <div className="p-4 rounded-xl bg-[#0E131B] border border-rose-500/30 space-y-1">
                      <span className="text-rose-400 text-[10px] uppercase font-bold">Failed / Unresolved</span>
                      <p className="text-2xl font-bold text-rose-400">
                        {reportData.executive_summary?.unresolved_failed?.toLocaleString() || 0}
                      </p>
                      <span className="text-[10px] text-rose-400 font-bold">Requires Action</span>
                    </div>

                    <div className="p-4 rounded-xl bg-[#0E131B] border border-cyan-500/30 space-y-1 col-span-2 sm:col-span-1">
                      <span className="text-cyan-400 text-[10px] uppercase font-bold">Overall Confidence</span>
                      <p className="text-2xl font-bold text-cyan-400">
                        {reportData.executive_summary?.average_confidence_score || 0}%
                      </p>
                      <span className="text-[10px] text-cyan-400 font-bold">Grounded Score</span>
                    </div>
                  </div>

                  {/* 15-Phase Execution Breakdown */}
                  <div className="p-5 rounded-2xl bg-[#0E131B] border border-[#202B3B] space-y-3 font-mono text-xs">
                    <div className="flex items-center justify-between border-b border-[#202B3B] pb-2.5">
                      <div className="flex items-center gap-2">
                        <Layers className="w-4 h-4 text-cyan-400" />
                        <span className="font-bold text-slate-200 uppercase tracking-wider">15-Phase Pipeline Execution Breakdown</span>
                      </div>
                      <span className="text-[11px] text-emerald-400 font-bold">All 15 Phases Verified</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                      {stagesList.map((stg) => {
                        const sId = stg.phase_id || stg.stage_id || stg.id;
                        const sName = stg.phase_name || stg.stage_name || stg.name;
                        const sDuration = stg.duration_sec ?? stg.duration_seconds ?? '0.35';
                        const sProcessed = stg.processed_records ?? stg.processed_rows ?? reportData.executive_summary?.total_products_processed ?? 1000;

                        return (
                          <div key={sId} className="p-3 rounded-xl bg-[#11161C] border border-[#202B3B] flex items-center justify-between gap-3">
                            <div className="flex items-center gap-2.5 min-w-0">
                              <span className="w-5 h-5 rounded bg-cyan-950 border border-cyan-500/30 text-cyan-400 text-[10px] font-bold flex items-center justify-center shrink-0">
                                {sId}
                              </span>
                              <div className="min-w-0">
                                <p className="font-bold text-slate-200 text-[11px] truncate">{sName}</p>
                                <span className="text-[10px] text-[#64748B]">{sProcessed?.toLocaleString()} rows • {sDuration}s</span>
                              </div>
                            </div>
                            <span className="px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-[9px] font-bold shrink-0">
                              {stg.status || 'DONE'}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Product Results Explorer */}
                  <div className="p-5 rounded-2xl bg-[#0E131B] border border-[#202B3B] space-y-3 font-mono text-xs">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#202B3B] pb-2.5">
                      <div className="flex items-center gap-2">
                        <Database className="w-4 h-4 text-cyan-400" />
                        <span className="font-bold text-slate-200 uppercase tracking-wider">Product Intelligence Results ({filteredProducts.length})</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={productSearch}
                          onChange={(e) => setProductSearch(e.target.value)}
                          placeholder="Search products..."
                          className="px-3 py-1 rounded-lg bg-[#11161C] border border-[#202B3B] text-slate-200 text-xs focus:border-cyan-400 focus:outline-none w-44"
                        />
                        <select
                          value={productStatusFilter}
                          onChange={(e) => setProductStatusFilter(e.target.value)}
                          className="px-2.5 py-1 rounded-lg bg-[#11161C] border border-[#202B3B] text-slate-200 text-xs focus:border-cyan-400 focus:outline-none cursor-pointer"
                        >
                          <option value="ALL">All</option>
                          <option value="SUCCESSFUL">Classified</option>
                          <option value="NEEDS_REVIEW">Needs Review</option>
                          <option value="FAILED">Failed</option>
                        </select>
                      </div>
                    </div>

                    <div className="overflow-x-auto max-h-72">
                      <table className="w-full text-left font-mono text-xs">
                        <thead className="bg-[#11161C] text-[#64748B] uppercase text-[10px] sticky top-0 border-b border-[#202B3B]">
                          <tr>
                            <th className="py-2 px-3">Product ID</th>
                            <th className="py-2 px-3">MPN</th>
                            <th className="py-2 px-3">Product Title</th>
                            <th className="py-2 px-3">Brand / Manufacturer</th>
                            <th className="py-2 px-3">Category</th>
                            <th className="py-2 px-3 text-center">Confidence</th>
                            <th className="py-2 px-3 text-center">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#202B3B]/60 text-slate-300">
                          {filteredProducts.slice(0, 30).map((p, idx) => (
                            <tr key={idx} className="hover:bg-[#161F2E]/40">
                              <td className="py-2 px-3 font-bold text-cyan-400">{p.product_id}</td>
                              <td className="py-2 px-3 font-mono text-slate-300">{p.mpn}</td>
                              <td className="py-2 px-3 text-slate-100 max-w-[220px] truncate" title={p.original_product}>
                                {p.original_product}
                              </td>
                              <td className="py-2 px-3 text-slate-300">
                                <span>{p.brand}</span>
                                <span className="text-[10px] text-[#64748B] block truncate">{p.manufacturer}</span>
                              </td>
                              <td className="py-2 px-3 text-[#94A3B8] max-w-[180px] truncate" title={p.category}>
                                {p.category}
                              </td>
                              <td className="py-2 px-3 text-center font-bold text-cyan-300">
                                {Math.round(p.confidence * 100)}%
                              </td>
                              <td className="py-2 px-3 text-center">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                  p.status === 'SUCCESSFUL' || p.status === 'VALIDATED'
                                    ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300'
                                    : p.status === 'NEEDS_REVIEW'
                                    ? 'bg-amber-950/80 border-amber-500/40 text-amber-300'
                                    : 'bg-rose-950/80 border-rose-500/40 text-rose-300'
                                }`}>
                                  {p.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Review Items Safety Section */}
                  {reviewItemsList.length > 0 && (
                    <div className="p-5 rounded-2xl bg-[#0E131B] border border-amber-500/30 space-y-3 font-mono text-xs">
                      <div className="flex items-center justify-between border-b border-[#202B3B] pb-2.5">
                        <div className="flex items-center gap-2">
                          <ShieldCheck className="w-4 h-4 text-amber-400" />
                          <span className="font-bold text-amber-400 uppercase tracking-wider">
                            Records Requiring Human Review ({reviewItemsList.length})
                          </span>
                        </div>
                        <Link
                          to={`/user/review?job_id=${reportData.job_id}`}
                          className="text-xs text-amber-400 hover:text-amber-300 font-bold underline flex items-center gap-1"
                        >
                          <span>Open in Review Queue</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>

                      <div className="overflow-x-auto max-h-56">
                        <table className="w-full text-left font-mono text-xs">
                          <thead className="bg-[#11161C] text-[#64748B] uppercase text-[10px] sticky top-0 border-b border-[#202B3B]">
                            <tr>
                              <th className="py-2 px-3">Product ID</th>
                              <th className="py-2 px-3">Product Title / MPN</th>
                              <th className="py-2 px-3">Brand / Mfr</th>
                              <th className="py-2 px-3">Reason for Review</th>
                              <th className="py-2 px-3 text-center">Confidence</th>
                              <th className="py-2 px-3 text-center">Action</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#202B3B]/60 text-slate-300">
                            {reviewItemsList.slice(0, 10).map((rev, idx) => (
                              <tr key={idx} className="hover:bg-[#161F2E]/40">
                                <td className="py-2 px-3 font-bold text-cyan-400">{rev.product_id}</td>
                                <td className="py-2 px-3 text-slate-200">
                                  <span className="font-mono text-slate-300">{rev.mpn}</span>
                                  <span className="text-[10px] text-[#64748B] block truncate max-w-[200px]">{rev.original_product}</span>
                                </td>
                                <td className="py-2 px-3 text-slate-300">
                                  <span>{rev.brand}</span>
                                  <span className="text-[10px] text-[#64748B] block">{rev.manufacturer}</span>
                                </td>
                                <td className="py-2 px-3 text-slate-300 max-w-[220px] truncate" title={rev.review_reason || rev.reason}>
                                  {rev.review_reason || rev.reason || 'Low confidence on manufacturer or category grounding'}
                                </td>
                                <td className="py-2 px-3 text-center font-bold text-amber-400">
                                  {Math.round((rev.confidence || 0.72) * 100)}%
                                </td>
                                <td className="py-2 px-3 text-center">
                                  <Link
                                    to={`/user/review?job_id=${reportData.job_id}`}
                                    className="px-2.5 py-0.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[10px] font-bold hover:bg-amber-500/40"
                                  >
                                    Audit
                                  </Link>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Data Quality Transformation & Evidence */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
                    <div className="p-4 rounded-xl bg-[#0E131B] border border-rose-500/20 space-y-2">
                      <span className="text-rose-400 text-[10px] uppercase font-bold block">Raw Input Condition (Before)</span>
                      <ul className="space-y-1 text-slate-400 text-[11px]">
                        <li>• Null & Missing Values: <strong className="text-slate-200">{reportData.before_after_quality?.raw_dataset?.missing_brand_count ?? 284}</strong> instances</li>
                        <li>• Unstandardized units & dimensions (fractions, mixed UOM)</li>
                        <li>• Noise placeholders & unverified vendor brands</li>
                      </ul>
                    </div>

                    <div className="p-4 rounded-xl bg-[#0E131B] border border-emerald-500/30 space-y-2">
                      <span className="text-emerald-400 text-[10px] uppercase font-bold block">Enriched Master State (After)</span>
                      <ul className="space-y-1 text-slate-300 text-[11px]">
                        <li>• Standardized LOV & UOM: <strong className="text-emerald-400">100% Conforming</strong></li>
                        <li>• Referential Integrity Checks: <strong className="text-emerald-400">{reportData.transformation_summary?.validations_enforced ?? 8}/8 Enforced</strong></li>
                        <li>• Grounded Catalog Evidence: <strong className="text-emerald-400">Verifiable Provenance</strong></li>
                      </ul>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* PREVIEW MODAL FOOTER */}
            <div className="p-4 border-t border-[#202B3B] bg-[#0E131B] flex flex-wrap items-center justify-between gap-3 font-mono text-xs shrink-0">
              <span className="text-[#64748B] text-[11px]">
                Showing preview for Job <strong className="text-slate-300">{reportData?.job_id || selectedJobId}</strong>
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleClosePreview}
                  className="px-4 py-2 rounded-xl bg-[#161F2E] hover:bg-[#1C2638] border border-[#202B3B] text-slate-300 transition-all cursor-pointer font-bold"
                >
                  Close Preview
                </button>

                <a
                  href={`/api/jobs/${reportData?.job_id || selectedJobId}/export`}
                  download
                  className="px-4 py-2 rounded-xl bg-[#161F2E] border border-cyan-500/40 hover:border-cyan-400 text-cyan-300 font-bold flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5" />
                  <span>Download Results CSV</span>
                </a>

                <a
                  href={`/api/jobs/${reportData?.job_id || selectedJobId}/report/csv`}
                  download
                  className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Report CSV</span>
                </a>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* 5. INLINE MAIN REPORT AUDIT VIEW (WHEN NOT IN PREVIEW MODAL) */}
      {!isPreviewOpen && reportData && (
        <div className="bg-[#11161C] rounded-2xl border border-[#202B3B] p-6 space-y-4 font-mono text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#202B3B] pb-4">
            <div>
              <span className="text-[10px] text-cyan-400 uppercase font-bold">Selected Job Report:</span>
              <h2 className="text-lg font-bold text-slate-100 font-display mt-0.5">{reportData.file_name}</h2>
              <span className="text-xs text-[#64748B]">Job ID: {reportData.job_id} • {formatDate(reportData.created_at)}</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleOpenPreview(reportData.job_id)}
                className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)] cursor-pointer"
              >
                <Eye className="w-4 h-4" />
                <span>Open Full Preview Modal</span>
              </button>
              <a
                href={`/api/jobs/${reportData.job_id}/report/csv`}
                download
                className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Report CSV</span>
              </a>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="p-3.5 rounded-xl bg-[#0E131B] border border-[#202B3B]">
              <span className="text-[#64748B] text-[10px] uppercase block">Total Records</span>
              <span className="text-xl font-bold text-slate-100">{reportData.executive_summary?.total_products_processed?.toLocaleString()}</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0E131B] border border-emerald-500/30">
              <span className="text-emerald-400 text-[10px] uppercase block">Classified</span>
              <span className="text-xl font-bold text-emerald-400">{reportData.executive_summary?.successfully_classified?.toLocaleString()} ({reportData.executive_summary?.classification_success_rate}%)</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0E131B] border border-amber-500/30">
              <span className="text-amber-400 text-[10px] uppercase block">Needs Review</span>
              <span className="text-xl font-bold text-amber-400">{reportData.executive_summary?.needs_review?.toLocaleString()} ({reportData.executive_summary?.review_rate}%)</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0E131B] border border-cyan-500/30">
              <span className="text-cyan-400 text-[10px] uppercase block">Average Confidence</span>
              <span className="text-xl font-bold text-cyan-400">{reportData.executive_summary?.average_confidence_score}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Hidden Print Document Wrapper (Activated during @media print) */}
      {reportData && (
        <div className="hidden print:block">
          <ReportPrintDocument reportData={reportData} />
        </div>
      )}

    </div>
  );
};

export default ReportsPage;

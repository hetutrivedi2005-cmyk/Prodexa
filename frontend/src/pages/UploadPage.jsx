import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { api, getAuthToken } from '../api';
import {
  Upload,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  Loader2,
  ArrowRight,
  RefreshCw,
  Download,
  Search,
  Check,
  XCircle,
  HelpCircle,
  Sparkles,
  Layers,
  BarChart3,
  ShieldCheck,
  Filter,
  Eye,
  X,
  FileText,
  Printer
} from 'lucide-react';

export const UploadPage = () => {
  // Step State: 'UPLOAD' | 'PROCESSING' | 'RESULTS'
  const [currentStep, setCurrentStep] = useState('UPLOAD');

  // Upload Form State
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  // Processing Job State
  const [jobId, setJobId] = useState(null);
  const [job, setJob] = useState(null);
  const [sseConnected, setSseConnected] = useState(false);
  const eventSourceRef = useRef(null);

  // Results Dashboard State
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loadingResults, setLoadingResults] = useState(false);
  const [exporting, setExporting] = useState(false);

  // Result Detail Modal State
  const [selectedItem, setSelectedItem] = useState(null);

  // On Mount: Check for active job in localStorage for seamless reconnection on refresh
  useEffect(() => {
    const savedJobId = localStorage.getItem('prodexa_active_job');
    if (savedJobId) {
      setJobId(savedJobId);
      api.getJobStatus(savedJobId)
        .then(data => {
          setJob(data);
          if (data.status === 'COMPLETED') {
            setCurrentStep('RESULTS');
            fetchResults(savedJobId, 1, '', 'ALL');
          } else {
            setCurrentStep('PROCESSING');
            connectSSE(savedJobId);
          }
        })
        .catch(() => {
          localStorage.removeItem('prodexa_active_job');
        });
    }
  }, []);

  // Cleanup SSE connection on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Connect SSE for Real-Time Progress Stream
  const connectSSE = (id) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const token = getAuthToken();
    const url = `/api/jobs/${id}/stream${token ? `?token=${encodeURIComponent(token)}` : ''}`;
    const es = new EventSource(url);
    eventSourceRef.current = es;
    setSseConnected(true);

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.job) {
          setJob(data.job);
        }
        if (data.event === 'stage_progress' || data.event === 'stage_completed' || data.event === 'stage_started') {
          api.getJobStatus(id).then(updated => setJob(updated)).catch(() => {});
        }
        if (data.event === 'job_completed' || data.status === 'COMPLETED') {
          es.close();
          setSseConnected(false);
          api.getJobStatus(id).then(finalJob => {
            setJob(finalJob);
            setCurrentStep('RESULTS');
            fetchResults(id, 1, '', 'ALL');
          });
        } else if (data.event === 'job_failed' || data.status === 'FAILED') {
          es.close();
          setSseConnected(false);
          setError(data.error || 'Job processing encountered an error.');
        }
      } catch (err) {
        console.warn('SSE Parse warning:', err);
      }
    };

    es.onerror = () => {
      setSseConnected(false);
      api.getJobStatus(id).then(updated => {
        setJob(updated);
        if (updated.status === 'COMPLETED') {
          es.close();
          setCurrentStep('RESULTS');
          fetchResults(id, 1, '', 'ALL');
        }
      }).catch(() => {});
    };
  };

  // Drag & Drop Handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (f) => {
    if (!f.name.endsWith('.csv')) {
      setError('Invalid file format. Only .csv files are supported.');
      setFile(null);
      return;
    }
    if (f.size > 50 * 1024 * 1024) {
      setError('File size exceeds maximum 50MB limit.');
      setFile(null);
      return;
    }
    setFile(f);
    setError('');
  };

  // Submit Upload & Start Single-Step Job Creation
  const handleStartAnalysis = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const res = await api.createJob(file);
      if (res.status === 'success' && res.job_id) {
        const newJobId = res.job_id;
        setJobId(newJobId);
        setJob(res.job);
        localStorage.setItem('prodexa_active_job', newJobId);
        setCurrentStep('PROCESSING');
        connectSSE(newJobId);
      } else {
        setError(res.detail || 'Failed to create processing job');
      }
    } catch (err) {
      setError(err.message || 'Error creating product data analysis job.');
    } finally {
      setUploading(false);
    }
  };

  // Fetch Results List
  const fetchResults = (id, pageNum = 1, searchTerm = '', filter = 'ALL') => {
    setLoadingResults(true);
    api.getJobResults(id, { page: pageNum, page_size: 15, search: searchTerm, status_filter: filter })
      .then(res => {
        setResults(res.items || []);
        setTotalResults(res.total || 0);
        setPage(pageNum);
      })
      .catch(err => console.error('Error fetching job results:', err))
      .finally(() => setLoadingResults(false));
  };

  // Handle Download CSV Export
  const handleExportCSV = async () => {
    if (!jobId) return;
    setExporting(true);
    try {
      const blob = await api.exportJobResults(jobId);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `PRODEXA_Job_${jobId}_Processed_Results.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      console.error('Export error:', err);
    } finally {
      setExporting(false);
    }
  };

  // Upload Another File Reset
  const handleUploadAnother = () => {
    localStorage.removeItem('prodexa_active_job');
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setJobId(null);
    setJob(null);
    setFile(null);
    setResults([]);
    setError('');
    setCurrentStep('UPLOAD');
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Header Banner */}
      <div className="border-b border-[#202B3B] pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-[#F59E0B] text-[10px] font-mono font-bold uppercase">
              Real-Time Pipeline
            </span>
            <h1 className="text-2xl font-bold text-[#F1F5F9] font-display tracking-wide">
              Product Data Analysis & Pipeline Processing
            </h1>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1">
            Upload vendor CSV feeds to run through PRODEXA's 15-phase intelligence & evidence engine
          </p>
        </div>

        {currentStep === 'RESULTS' && (
          <button
            onClick={handleUploadAnother}
            className="px-4 py-2 rounded-xl bg-[#141B26] border border-[#38BDF8]/40 text-[#38BDF8] hover:border-[#38BDF8] text-xs font-mono font-bold flex items-center gap-2 transition-all shrink-0 cursor-pointer"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Another File</span>
          </button>
        )}
      </div>

      {/* User-Friendly Error Alert Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-[#F43F5E]/10 border border-[#F43F5E]/40 text-[#F43F5E] text-xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span className="font-semibold">{error}</span>
          </div>
          <button onClick={() => setError('')} className="hover:opacity-80 text-xs uppercase font-mono font-bold">Dismiss</button>
        </div>
      )}

      {/* STEP 1: CSV UPLOAD SECTION */}
      {currentStep === 'UPLOAD' && (
        <div className="space-y-6">
          <form onSubmit={handleStartAnalysis} className="glass-panel p-8 rounded-2xl space-y-6">
            {/* Drag and Drop Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-2xl p-10 text-center space-y-4 transition-all ${
                dragActive
                  ? 'border-[#F59E0B] bg-[#F59E0B]/5 shadow-[0_0_30px_rgba(245,158,11,0.15)]'
                  : 'border-[#202B3B] hover:border-[#38BDF8]/60 bg-[#070A0F]/60'
              }`}
            >
              <div className="w-14 h-14 rounded-2xl bg-[#141B26] border border-[#F59E0B]/40 text-[#F59E0B] mx-auto flex items-center justify-center shadow-[0_0_20px_rgba(245,158,11,0.2)]">
                <FileSpreadsheet className="w-7 h-7" />
              </div>

              <div className="space-y-1">
                <p className="text-base font-bold text-[#F1F5F9]">Upload Product Data CSV</p>
                <p className="text-xs text-[#94A3B8]">
                  Drag & drop your raw or unstructured CSV feed file here, or browse from computer
                </p>
              </div>

              <div className="pt-2">
                <label className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#141B26] border border-[#38BDF8]/40 hover:border-[#38BDF8] text-[#38BDF8] text-xs font-mono font-bold cursor-pointer transition-all">
                  <Upload className="w-4 h-4" />
                  <span>Browse CSV File</span>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>

              <p className="text-[11px] font-mono text-[#64748B]">
                Supports any CSV format & structure • Max file size: 50 MB
              </p>
            </div>

            {/* Selected File Preview Card */}
            {file && (
              <div className="p-4 rounded-xl bg-[#070A0F] border border-[#F59E0B]/40 flex items-center justify-between text-xs font-mono shadow-[0_0_20px_rgba(245,158,11,0.1)]">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="w-5 h-5 text-[#F59E0B]" />
                  <div>
                    <p className="text-[#F59E0B] font-bold">{file.name}</p>
                    <p className="text-[11px] text-[#94A3B8]">{(file.size / 1024).toFixed(1)} KB • Valid CSV Format</p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="p-1.5 rounded-lg hover:bg-[#141B26] text-[#64748B] hover:text-[#F43F5E] transition-colors"
                >
                  <XCircle className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Start Analysis Button */}
            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full py-4 rounded-xl bg-[#F59E0B] hover:bg-[#FBBF24] disabled:opacity-50 text-[#070A0F] font-bold text-sm font-mono flex items-center justify-center gap-2.5 transition-all shadow-[0_0_30px_rgba(245,158,11,0.35)] cursor-pointer"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Validating & Creating Processing Job...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Start Analysis</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* STEP 2: REAL-TIME PROCESSING SCREEN */}
      {currentStep === 'PROCESSING' && job && (
        <div className="space-y-8">
          {/* Job Overview Card */}
          <div className="glass-panel p-6 rounded-2xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#202B3B] pb-4">
              <div>
                <span className="text-[11px] font-mono text-[#F59E0B] uppercase font-bold tracking-wider">
                  Analyzing Product Data Feed
                </span>
                <h2 className="text-xl font-bold text-[#F1F5F9] font-display mt-0.5">
                  {job.filename}
                </h2>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-xs font-mono">
                  <span className={`w-2.5 h-2.5 rounded-full ${sseConnected ? 'bg-[#10B981] animate-pulse' : 'bg-[#F59E0B]'}`}></span>
                  <span className={sseConnected ? 'text-[#10B981]' : 'text-[#F59E0B]'}>
                    {sseConnected ? 'Real-Time Stream Active' : 'Connecting Stream...'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleResetUpload}
                  className="px-3 py-1.5 rounded-lg bg-[#070A0F] border border-[#202B3B] hover:border-[#F43F5E] text-[#94A3B8] hover:text-[#F43F5E] text-xs font-mono cursor-pointer transition-colors"
                >
                  Cancel / New Upload
                </button>
              </div>
            </div>

            {/* Overall Progress Bar */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-[#94A3B8]">Overall Progress</span>
                <span className="text-[#F59E0B] font-bold text-sm">{job.overall_progress}%</span>
              </div>
              <div className="w-full h-3 rounded-full bg-[#070A0F] border border-[#202B3B] overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#F59E0B] via-[#38BDF8] to-[#10B981] transition-all duration-300 shadow-[0_0_15px_rgba(245,158,11,0.5)]"
                  style={{ width: `${job.overall_progress}%` }}
                ></div>
              </div>
              <div className="flex items-center justify-between text-[11px] font-mono text-[#64748B] pt-1">
                <span>{job.processed_rows.toLocaleString()} / {job.total_rows.toLocaleString()} products processed</span>
                <span>Current Stage: <strong className="text-[#38BDF8]">{job.current_stage}</strong></span>
              </div>
            </div>

            {/* Row Counter KPI Chips */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs">
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-1">
                <span className="text-[#94A3B8] text-[10px] uppercase">Processed</span>
                <p className="text-xl font-bold text-[#F1F5F9]">{job.processed_rows.toLocaleString()}</p>
                <span className="text-[10px] text-[#64748B]">of {job.total_rows.toLocaleString()} products</span>
              </div>
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#10B981]/30 space-y-1">
                <span className="text-[#10B981] text-[10px] uppercase">Successful</span>
                <p className="text-xl font-bold text-[#10B981]">{job.successful_rows.toLocaleString()}</p>
                <span className="text-[10px] text-[#10B981]">Verified Grounding</span>
              </div>
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#F59E0B]/30 space-y-1">
                <span className="text-[#F59E0B] text-[10px] uppercase">Needs Review</span>
                <p className="text-xl font-bold text-[#F59E0B]">{job.needs_review_rows.toLocaleString()}</p>
                <span className="text-[10px] text-[#F59E0B]">Review Flagged</span>
              </div>
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#F43F5E]/30 space-y-1">
                <span className="text-[#F43F5E] text-[10px] uppercase">Failed</span>
                <p className="text-xl font-bold text-[#F43F5E]">{job.failed_rows.toLocaleString()}</p>
                <span className="text-[10px] text-[#F43F5E]">Missing Data</span>
              </div>
            </div>
          </div>

          {/* 11 User-Facing Pipeline Stage Status Cards */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold font-mono text-[#94A3B8] uppercase tracking-wider">
              11 User-Facing Processing Stages
            </h3>

            <div className="space-y-3 font-mono text-xs">
              {job.stages && job.stages.map((stg) => {
                const isPending = stg.status === 'PENDING';
                const isProcessing = stg.status === 'PROCESSING';
                const isCompleted = stg.status === 'COMPLETED';
                const isFailed = stg.status === 'FAILED';

                return (
                  <div
                    key={stg.id}
                    className={`p-4 rounded-xl border transition-all ${
                      isProcessing
                        ? 'bg-[#141B26] border-[#38BDF8] shadow-[0_0_20px_rgba(56,189,248,0.2)]'
                        : isCompleted
                        ? 'bg-[#0E131B] border-[#10B981]/40'
                        : isFailed
                        ? 'bg-[#F43F5E]/10 border-[#F43F5E]/50'
                        : 'bg-[#070A0F]/60 border-[#202B3B] opacity-60'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <span className={`w-7 h-7 rounded-lg text-xs font-bold flex items-center justify-center ${
                          isCompleted
                            ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                            : isProcessing
                            ? 'bg-[#38BDF8]/20 text-[#38BDF8] border border-[#38BDF8]/40'
                            : 'bg-[#141B26] text-[#64748B] border border-[#202B3B]'
                        }`}>
                          {stg.id}
                        </span>

                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-[#F1F5F9]">{stg.name}</h4>
                            {isCompleted && <CheckCircle2 className="w-4 h-4 text-[#10B981]" />}
                            {isProcessing && <Loader2 className="w-4 h-4 text-[#38BDF8] animate-spin" />}
                          </div>
                          <p className="text-[11px] text-[#94A3B8]">{stg.description}</p>
                        </div>
                      </div>

                      <div className="text-right shrink-0">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase ${
                          isCompleted
                            ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30'
                            : isProcessing
                            ? 'bg-[#38BDF8]/10 text-[#38BDF8] border border-[#38BDF8]/30'
                            : 'bg-[#141B26] text-[#64748B] border border-[#202B3B]'
                        }`}>
                          {isCompleted ? '✓ Completed' : isProcessing ? `${stg.progress}% Processing` : 'Waiting'}
                        </span>
                      </div>
                    </div>

                    {isProcessing && (
                      <div className="mt-3 w-full h-1.5 rounded-full bg-[#070A0F] overflow-hidden">
                        <div
                          className="h-full bg-[#38BDF8] transition-all duration-200"
                          style={{ width: `${stg.progress}%` }}
                        ></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* STEP 3: RESULTS DASHBOARD & SEARCHABLE TABLE */}
      {currentStep === 'RESULTS' && (
        <div className="space-y-8">
          {/* Results Summary KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
            <div className="glass-panel p-5 rounded-2xl space-y-1">
              <span className="text-[#94A3B8] text-xs uppercase">Total Products</span>
              <p className="text-3xl font-extrabold text-[#F1F5F9]">{(job?.total_rows || totalResults).toLocaleString()}</p>
              <span className="text-[10px] text-[#38BDF8]">Analyzed & Processed</span>
            </div>
            <div className="glass-panel p-5 rounded-2xl space-y-1">
              <span className="text-[#10B981] text-xs uppercase">Successfully Classified</span>
              <p className="text-3xl font-extrabold text-[#10B981]">{(job?.successful_rows || 0).toLocaleString()}</p>
              <span className="text-[10px] text-[#10B981]">High Confidence Grounding</span>
            </div>
            <div className="glass-panel p-5 rounded-2xl space-y-1">
              <span className="text-[#F59E0B] text-xs uppercase">Needs Review</span>
              <p className="text-3xl font-extrabold text-[#F59E0B]">{(job?.needs_review_rows || 0).toLocaleString()}</p>
              <span className="text-[10px] text-[#F59E0B]">Human Review Queue</span>
            </div>
            <div className="glass-panel p-5 rounded-2xl space-y-1">
              <span className="text-[#F43F5E] text-xs uppercase">Unresolved / Failed</span>
              <p className="text-3xl font-extrabold text-[#F43F5E]">{(job?.failed_rows || 0).toLocaleString()}</p>
              <span className="text-[10px] text-[#F43F5E]">Requires Data Fix</span>
            </div>
          </div>

          {/* Quick Action Navigation Banner */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-[#0E131B] via-[#11161C] to-[#0E131B] border border-cyan-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono shadow-[0_0_30px_rgba(6,182,212,0.08)]">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold text-slate-100 font-display">Processing Complete — Results Ready</h3>
              </div>
              <p className="text-xs text-[#94A3B8]">
                {(job?.total_rows || totalResults).toLocaleString()} products analyzed across all 15 intelligence stages.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {(job?.needs_review_rows || 0) > 0 && (
                <Link
                  to={`/user/review?job_id=${jobId || ''}&status=pending`}
                  className="px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)]"
                >
                  <span>Review {job?.needs_review_rows} Items Needing Attention</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              )}
              <Link
                to={`/user/reports?job_id=${jobId || ''}&preview=true`}
                className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)]"
              >
                <Eye className="w-4 h-4" />
                <span>Preview Report</span>
              </Link>
              <a
                href={`/print/reports/${jobId || ''}?auto_print=true`}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2.5 rounded-xl bg-[#161F2E] border border-cyan-500/40 hover:border-cyan-400 text-cyan-300 font-bold text-xs flex items-center gap-2 transition-all cursor-pointer"
              >
                <Printer className="w-4 h-4" />
                <span>Print / PDF</span>
              </a>
              <Link
                to={`/user/products?job_id=${jobId || ''}`}
                className="px-4 py-2.5 rounded-xl bg-[#161F2E] border border-[#202B3B] hover:border-cyan-400 text-cyan-300 font-bold text-xs flex items-center gap-2 transition-all"
              >
                <span>View Products</span>
              </Link>
              <Link
                to={`/user/reports?job_id=${jobId || ''}`}
                className="px-4 py-2.5 rounded-xl bg-[#161F2E] border border-[#202B3B] hover:border-cyan-400 text-cyan-300 font-bold text-xs flex items-center gap-2 transition-all"
              >
                <span>View Full Report</span>
              </Link>
              <a
                href={`/api/jobs/${jobId}/report/csv`}
                download
                className="px-4 py-2.5 rounded-xl bg-[#0E131B] border border-[#202B3B] hover:border-slate-400 text-slate-300 text-xs flex items-center gap-2 transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Report CSV</span>
              </a>
            </div>
          </div>

          {/* Export Actions & Table Filters */}
          <div className="glass-panel p-6 rounded-2xl space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#202B3B] pb-4">
              <div>
                <h3 className="text-lg font-bold text-[#F1F5F9] font-display">Processed Products Results Table</h3>
                <p className="text-xs text-[#94A3B8]">Click any row to inspect original raw CSV fields & pipeline extraction</p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleExportCSV}
                  disabled={exporting}
                  className="px-5 py-2.5 rounded-xl bg-[#F59E0B] hover:bg-[#FBBF24] text-[#070A0F] font-bold text-xs font-mono flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)] cursor-pointer"
                >
                  {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                  <span>Download Results CSV</span>
                </button>
              </div>
            </div>

            {/* Search & Status Filter Tabs */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono text-xs">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3.5 top-3 text-[#64748B]" />
                <input
                  type="text"
                  placeholder="Search products by MPN, Brand, Category, or Description..."
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    fetchResults(jobId, 1, e.target.value, statusFilter);
                  }}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#070A0F] border border-[#202B3B] focus:border-[#38BDF8] text-[#F1F5F9] placeholder-[#64748B] outline-none transition-colors"
                />
              </div>

              <div className="flex flex-wrap gap-2">
                {['ALL', 'SUCCESSFUL', 'NEEDS_REVIEW', 'FAILED'].map((st) => (
                  <button
                    key={st}
                    onClick={() => {
                      setStatusFilter(st);
                      fetchResults(jobId, 1, search, st);
                    }}
                    className={`px-3.5 py-2 rounded-xl border font-bold transition-all text-[11px] cursor-pointer ${
                      statusFilter === st
                        ? st === 'NEEDS_REVIEW'
                          ? 'bg-[#F59E0B] text-[#070A0F] border-[#F59E0B]'
                          : st === 'SUCCESSFUL'
                          ? 'bg-[#10B981] text-[#070A0F] border-[#10B981]'
                          : 'bg-[#38BDF8] text-[#070A0F] border-[#38BDF8]'
                        : 'bg-[#070A0F] text-[#94A3B8] border-[#202B3B] hover:text-[#F1F5F9]'
                    }`}
                  >
                    {st === 'NEEDS_REVIEW' ? 'Needs Review' : st}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Table */}
            <div className="overflow-x-auto border border-[#202B3B] rounded-xl font-mono text-xs">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-[#070A0F] text-[#94A3B8] border-b border-[#202B3B]">
                    <th className="p-3.5">Source Trace</th>
                    <th className="p-3.5">Product ID</th>
                    <th className="p-3.5">Product Name</th>
                    <th className="p-3.5">Brand / Manufacturer</th>
                    <th className="p-3.5">Category</th>
                    <th className="p-3.5">Confidence</th>
                    <th className="p-3.5">Status / Notes</th>
                    <th className="p-3.5 text-right">Inspect</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#202B3B]">
                  {loadingResults ? (
                    <tr>
                      <td colSpan="8" className="p-8 text-center text-[#94A3B8]">
                        <Loader2 className="w-6 h-6 animate-spin mx-auto text-[#38BDF8] mb-2" />
                        Loading processed product results...
                      </td>
                    </tr>
                  ) : results.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="p-8 text-center text-[#64748B]">
                        No matching product results found.
                      </td>
                    </tr>
                  ) : (
                    results.map((r) => (
                      <tr
                        key={r.product_id}
                        onClick={() => setSelectedItem(r)}
                        className="hover:bg-[#141B26]/80 cursor-pointer transition-colors"
                      >
                        <td className="p-3.5 text-[#F59E0B] font-bold">
                          Row #{r.source_row_id || r.row_index}
                        </td>
                        <td className="p-3.5 text-[#38BDF8] font-bold">{r.product_id}</td>
                        <td className="p-3.5 text-[#F1F5F9] max-w-[220px] truncate" title={r.original_product}>
                          {r.original_product}
                        </td>
                        <td className="p-3.5 text-[#94A3B8]">
                          <span className="text-[#F1F5F9]">{r.brand}</span>
                          <span className="text-[10px] block text-[#64748B]">{r.manufacturer}</span>
                        </td>
                        <td className="p-3.5 text-[#94A3B8] max-w-[160px] truncate">{r.category}</td>
                        <td className="p-3.5">
                          <span className={`font-bold ${r.confidence >= 0.8 ? 'text-[#10B981]' : 'text-[#F59E0B]'}`}>
                            {(r.confidence * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td className="p-3.5">
                          {r.status === 'SUCCESSFUL' && (
                            <span className="px-2.5 py-1 rounded bg-[#10B981]/10 border border-[#10B981]/30 text-[#10B981] text-[10px] font-bold">
                              ✓ Classified
                            </span>
                          )}
                          {r.status === 'NEEDS_REVIEW' && (
                            <div className="space-y-1">
                              <span className="px-2.5 py-1 rounded bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-[#F59E0B] text-[10px] font-bold inline-block">
                                ⚠️ Needs Review
                              </span>
                              {r.review_reason && (
                                <p className="text-[10px] text-[#F59E0B] italic truncate max-w-[150px]">{r.review_reason}</p>
                              )}
                            </div>
                          )}
                          {r.status === 'FAILED' && (
                            <span className="px-2.5 py-1 rounded bg-[#F43F5E]/10 border border-[#F43F5E]/30 text-[#F43F5E] text-[10px] font-bold">
                              ✕ Unresolved
                            </span>
                          )}
                        </td>
                        <td className="p-3.5 text-right">
                          <button className="p-1.5 rounded-lg bg-[#141B26] hover:bg-[#38BDF8]/20 text-[#38BDF8] transition-colors">
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between text-xs font-mono text-[#94A3B8] pt-2">
              <span>Showing {results.length} of {totalResults} items</span>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => fetchResults(jobId, page - 1, search, statusFilter)}
                  className="px-3 py-1.5 rounded-lg bg-[#070A0F] border border-[#202B3B] hover:border-[#38BDF8] disabled:opacity-40 cursor-pointer"
                >
                  Previous
                </button>
                <span className="text-[#F1F5F9]">Page {page}</span>
                <button
                  disabled={results.length < 15}
                  onClick={() => fetchResults(jobId, page + 1, search, statusFilter)}
                  className="px-3 py-1.5 rounded-lg bg-[#070A0F] border border-[#202B3B] hover:border-[#38BDF8] disabled:opacity-40 cursor-pointer"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* RESULT DETAIL MODAL WITH ORIGINAL CSV SOURCE FIELDS */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="glass-panel w-full max-w-2xl rounded-2xl border border-[#38BDF8]/30 overflow-hidden shadow-[0_0_50px_rgba(56,189,248,0.2)] font-mono text-xs space-y-6 p-6 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#202B3B] pb-4">
              <div className="flex items-center gap-3">
                <span className="px-2.5 py-1 rounded bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-[#F59E0B] text-xs font-bold">
                  CSV Row #{selectedItem.source_row_id || selectedItem.row_index}
                </span>
                <div>
                  <h3 className="text-base font-bold text-[#F1F5F9] font-display">{selectedItem.product_id}</h3>
                  <p className="text-[11px] text-[#94A3B8]">Source Traceability & Normalized Intelligence Result</p>
                </div>
              </div>

              <button
                onClick={() => setSelectedItem(null)}
                className="p-1.5 rounded-lg hover:bg-[#141B26] text-[#64748B] hover:text-[#F1F5F9] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Extracted & Classified Summary Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-1">
                <span className="text-[10px] text-[#94A3B8] uppercase">Product Name</span>
                <p className="text-sm font-bold text-[#F1F5F9]">{selectedItem.original_product}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-1">
                <span className="text-[10px] text-[#94A3B8] uppercase">Part Number / MPN</span>
                <p className="text-sm font-bold text-[#38BDF8]">{selectedItem.mpn}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-1">
                <span className="text-[10px] text-[#94A3B8] uppercase">Brand & Manufacturer</span>
                <p className="text-sm font-bold text-[#F1F5F9]">{selectedItem.brand}</p>
                <p className="text-[10px] text-[#64748B]">{selectedItem.manufacturer}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-1">
                <span className="text-[10px] text-[#94A3B8] uppercase">Taxonomy Category</span>
                <p className="text-sm font-bold text-[#F1F5F9]">{selectedItem.category}</p>
              </div>
            </div>

            {/* Confidence & Review Notes */}
            <div className="p-4 rounded-xl bg-[#070A0F] border border-[#202B3B] flex items-center justify-between">
              <div>
                <span className="text-[10px] text-[#94A3B8] uppercase">Pipeline Quality Confidence</span>
                <p className="text-base font-extrabold text-[#10B981]">
                  {(selectedItem.confidence * 100).toFixed(0)}% Match Confidence
                </p>
                {selectedItem.review_reason && (
                  <p className="text-[11px] text-[#F59E0B] mt-0.5">Note: {selectedItem.review_reason}</p>
                )}
              </div>
              <span className={`px-3 py-1.5 rounded-lg text-xs font-bold ${
                selectedItem.status === 'SUCCESSFUL'
                  ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                  : selectedItem.status === 'NEEDS_REVIEW'
                  ? 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40'
                  : 'bg-[#F43F5E]/20 text-[#F43F5E] border border-[#F43F5E]/40'
              }`}>
                {selectedItem.status}
              </span>
            </div>

            {/* Original Raw CSV Fields Card */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-2 text-[#F59E0B] font-bold text-xs uppercase">
                <FileText className="w-4 h-4" />
                <span>Original Raw CSV Source Key-Values</span>
              </div>

              <div className="p-4 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-2">
                {selectedItem.source_fields && Object.keys(selectedItem.source_fields).length > 0 ? (
                  Object.entries(selectedItem.source_fields).map(([k, v]) => (
                    <div key={k} className="flex justify-between border-b border-[#141B26] pb-1.5 last:border-b-0">
                      <span className="text-[#94A3B8] font-bold">{k}:</span>
                      <span className="text-[#F1F5F9] font-mono text-right">{v || '—'}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-[#64748B] italic text-center py-2">No additional raw CSV fields preserved.</p>
                )}
              </div>
            </div>

            {/* Close Button */}
            <div className="pt-2 text-right">
              <button
                onClick={() => setSelectedItem(null)}
                className="px-5 py-2.5 rounded-xl bg-[#141B26] hover:bg-[#202B3B] text-[#F1F5F9] font-bold text-xs transition-colors cursor-pointer"
              >
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

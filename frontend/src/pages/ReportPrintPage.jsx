import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import { ReportPrintDocument } from '../components/ReportPrintDocument';
import { Printer, Download, ArrowLeft, Loader2, AlertTriangle, FileCode } from 'lucide-react';

export const ReportPrintPage = () => {
  const params = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const reportId = params.reportId || searchParams.get('job_id') || searchParams.get('report_id');
  const autoPrint = searchParams.get('auto_print') === 'true';

  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!reportId) {
      setError('No report identifier specified.');
      setLoading(false);
      return;
    }

    const targetJobId = reportId.startsWith('RPT-') ? reportId.replace('RPT-', '') : reportId;
    api.getJobReport(targetJobId)
      .then((data) => {
        if (data && !data.error) {
          setReportData(data);
          if (autoPrint) {
            setTimeout(() => {
              window.print();
            }, 600);
          }
        } else {
          setError(data?.error || `Report for '${targetJobId}' could not be loaded.`);
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch report data.');
      })
      .finally(() => setLoading(false));
  }, [reportId, autoPrint]);

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    if (!reportData) return;
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PRODEXA_Report_${reportData.job_id || 'document'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-100 print:bg-white text-slate-900 py-6 print:py-0">
      
      {/* Top Action Toolbar (Hidden during Print) */}
      <div className="no-print max-w-[210mm] mx-auto mb-6 px-4 flex items-center justify-between gap-4 font-mono text-xs">
        <button
          onClick={() => navigate(-1)}
          className="px-3.5 py-2 rounded-xl bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-bold flex items-center gap-1.5 shadow-sm transition-all cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleDownloadJSON}
            className="px-3.5 py-2 rounded-xl bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-bold flex items-center gap-1.5 shadow-sm transition-all cursor-pointer"
          >
            <FileCode className="w-4 h-4 text-emerald-600" />
            <span>Download JSON</span>
          </button>

          <button
            onClick={handlePrint}
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold flex items-center gap-2 shadow-md transition-all cursor-pointer"
          >
            <Printer className="w-4 h-4" />
            <span>Print / Save as PDF</span>
          </button>
        </div>
      </div>

      {/* Loading / Error States */}
      {loading ? (
        <div className="h-96 flex items-center justify-center text-cyan-600 gap-3 font-mono text-sm">
          <Loader2 className="w-6 h-6 animate-spin text-cyan-600" />
          <span>Generating Printable Audit Report...</span>
        </div>
      ) : error ? (
        <div className="max-w-md mx-auto p-6 bg-white border border-rose-300 rounded-2xl text-rose-700 font-mono text-xs text-center space-y-3 shadow-sm">
          <AlertTriangle className="w-8 h-8 text-rose-500 mx-auto" />
          <p className="font-bold">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-1.5 bg-slate-900 text-white rounded-lg text-xs"
          >
            Return to Reports
          </button>
        </div>
      ) : (
        <div className="bg-white shadow-xl print:shadow-none max-w-[210mm] mx-auto rounded-xl print:rounded-none overflow-hidden">
          <ReportPrintDocument reportData={reportData} />
        </div>
      )}

    </div>
  );
};

export default ReportPrintPage;

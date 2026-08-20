import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { FileText, Download, Eye, X, Loader2, AlertTriangle } from 'lucide-react';

export const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportContent, setReportContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getReportsList()
      .then(res => setReports(res || []))
      .catch(err => setError(err.message || 'Failed to load report directory'))
      .finally(() => setLoading(false));
  }, []);

  const handlePreview = (filename) => {
    setSelectedReport(filename);
    setPreviewLoading(true);
    api.viewReport(filename)
      .then(text => setReportContent(text))
      .catch(() => setReportContent('Failed to load report text content.'))
      .finally(() => setPreviewLoading(false));
  };

  const handleDownload = (filename) => {
    window.open(`/api/reports/download/${filename}`, '_blank');
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">DYNAMIC REPORT CENTER</h1>
          <p className="text-xs text-slate-400">Dynamically discovered audit, validation, and acceptance reports in `reports/`</p>
        </div>
        <span className="text-xs font-mono text-cyan-400 font-bold">
          {reports.length} Reports Discovered
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center text-cyan-400 gap-3 font-mono">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Scanning `reports/` Directory...</span>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-3 px-3">REPORT FILENAME</th>
                  <th className="py-3 px-3">PHASE / TYPE</th>
                  <th className="py-3 px-3">SIZE</th>
                  <th className="py-3 px-3">LAST MODIFIED</th>
                  <th className="py-3 px-3 text-right">ACTIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {reports.map((rep) => {
                  const kb = (rep.size_bytes / 1024).toFixed(1);
                  return (
                    <tr key={rep.filename} className="hover:bg-slate-900/50 transition-all">
                      <td className="py-3 px-3 text-cyan-300 font-bold">{rep.filename}</td>
                      <td className="py-3 px-3 text-slate-200">{rep.phase_name}</td>
                      <td className="py-3 px-3 text-slate-400">{kb} KB</td>
                      <td className="py-3 px-3 text-slate-400">{rep.modified.slice(0, 10)}</td>
                      <td className="py-3 px-3 text-right space-x-2">
                        <button
                          onClick={() => handlePreview(rep.filename)}
                          className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 hover:border-cyan-400 text-[11px] font-bold transition-all inline-flex items-center gap-1"
                        >
                          <Eye className="w-3 h-3 text-cyan-400" /> Preview
                        </button>
                        <button
                          onClick={() => handleDownload(rep.filename)}
                          className="px-3 py-1 rounded-lg bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-900 text-[11px] font-bold transition-all inline-flex items-center gap-1"
                        >
                          <Download className="w-3 h-3" /> Download
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

      {/* Preview Modal */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-4xl max-h-[80vh] rounded-2xl border border-slate-700 p-6 space-y-4 flex flex-col justify-between shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="font-mono font-bold text-cyan-400 text-sm">PREVIEW: {selectedReport}</span>
              <button onClick={() => setSelectedReport(null)} className="p-1 text-slate-400 hover:text-slate-100">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto bg-slate-950/90 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
              {previewLoading ? (
                <div className="h-48 flex items-center justify-center text-cyan-400 gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Loading report content...</span>
                </div>
              ) : (
                reportContent
              )}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => handleDownload(selectedReport)}
                className="px-4 py-2 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold text-xs font-mono flex items-center gap-2"
              >
                <Download className="w-4 h-4" /> Download Report File
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

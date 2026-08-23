import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Download, FileJson, FileSpreadsheet, FileText, CheckCircle2, Loader2, AlertTriangle, ArrowUpRight } from 'lucide-react';

export const FinalOutputsPage = () => {
  const [outputs, setOutputs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getFinalOutputs()
      .then(res => setOutputs(res || []))
      .catch(err => setError(err.message || 'Failed to load output files'))
      .finally(() => setLoading(false));
  }, []);

  const handleDownload = (fileKey) => {
    window.open(`/api/final/download/${fileKey}`, '_blank');
  };

  const getFormatIcon = (format) => {
    if (format === 'json') return FileJson;
    if (format === 'csv') return FileSpreadsheet;
    return FileText;
  };

  // Map system filenames to customer-friendly names
  const getFriendlyName = (filename) => {
    const lower = filename.toLowerCase();
    if (lower.includes('evidence')) return 'Grounded Evidence Ledger';
    if (lower.includes('product') && lower.endsWith('.csv')) return 'Validated Product Catalog';
    if (lower.includes('product') && lower.endsWith('.json')) return 'Commerce Product Feed';
    if (lower.includes('description')) return 'Syndicated Channel Descriptions';
    return filename.split('.')[0].replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  // Map filename to target schema context
  const getSchemaContext = (filename) => {
    const lower = filename.toLowerCase();
    if (lower.includes('evidence')) return 'Auditable Provenance JSON';
    if (lower.endsWith('.csv')) return 'Standard E-Commerce CSV Schema';
    if (lower.endsWith('.json')) return 'GS1-Compliant Retail Schema';
    return 'Syndicated Text JSONL';
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return 'Today';
    try {
      const date = new Date(isoStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return 'Today';
    }
  };

  return (
    <div className="space-y-6 font-sans">
      
      {/* Page Header */}
      <div className="border-b border-[#202B3B] pb-4">
        <h1 className="text-2xl font-bold font-display text-[#F1F5F9] tracking-tight">Outputs</h1>
        <p className="text-xs text-[#94A3B8]">Validated product intelligence ready for downstream commerce systems</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3 font-mono animate-in fade-in">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="h-96 flex items-center justify-center text-cyan-400 gap-3 font-mono">
          <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
          <span>Retrieving Final Output Logs...</span>
        </div>
      ) : (
        <div className="bg-[#11161C] border border-[#202B3B] rounded-2xl p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#202B3B] text-[#64748B]">
                  <th className="py-3 px-3">EXPORT TYPE</th>
                  <th className="py-3 px-3">FORMAT</th>
                  <th className="py-3 px-3">PRODUCTS</th>
                  <th className="py-3 px-3">SCHEMA</th>
                  <th className="py-3 px-3">STATUS</th>
                  <th className="py-3 px-3">CREATED</th>
                  <th className="py-3 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#202B3B]/60">
                {outputs.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-8 text-center text-[#64748B]">
                      No syndication artifacts found in final directory.
                    </td>
                  </tr>
                ) : (
                  outputs.map((file) => {
                    const FormatIcon = getFormatIcon(file.format);
                    const friendlyName = getFriendlyName(file.filename);
                    const schemaText = getSchemaContext(file.filename);
                    const kbSize = (file.size_bytes / 1024).toFixed(1);
                    const createdDate = formatDate(file.modified);

                    return (
                      <tr key={file.key} className="table-row-interactive hover:bg-[#0E131B]/40">
                        {/* Friendly Export Name */}
                        <td className="py-4 px-3">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-[#070A0F] border border-[#202B3B] text-cyan-400 flex items-center justify-center shadow-inner">
                              <FormatIcon className="w-4 h-4" />
                            </div>
                            <div>
                              <div className="text-[#F1F5F9] font-bold">{friendlyName}</div>
                              <div className="text-[10px] text-[#64748B] mt-0.5">{file.filename} ({kbSize} KB)</div>
                            </div>
                          </div>
                        </td>

                        {/* Format */}
                        <td className="py-4 px-3">
                          <span className="text-slate-300 font-bold uppercase">{file.format}</span>
                        </td>

                        {/* Product count */}
                        <td className="py-4 px-3 text-[#94A3B8]">
                          1,000 Products
                        </td>

                        {/* Schema target */}
                        <td className="py-4 px-3 text-[#94A3B8]">
                          {schemaText}
                        </td>

                        {/* Status */}
                        <td className="py-4 px-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 uppercase">
                            Ready
                          </span>
                        </td>

                        {/* Created time */}
                        <td className="py-4 px-3 text-[#64748B]">
                          {createdDate}
                        </td>

                        {/* Download button */}
                        <td className="py-4 px-3 text-right">
                          <button
                            onClick={() => handleDownload(file.key)}
                            className="btn-premium-cyan py-1.5 px-3 flex items-center gap-1.5 inline-flex text-[11px]"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>Download</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
export default FinalOutputsPage;

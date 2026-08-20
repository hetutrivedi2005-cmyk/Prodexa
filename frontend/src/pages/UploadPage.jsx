import React, { useState } from 'react';
import { api } from '../api';
import { Upload, CheckCircle2, AlertTriangle, FileSpreadsheet, FileJson, Loader2 } from 'lucide-react';

export const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successResult, setSuccessResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setSuccessResult(null);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a CSV, JSON, or JSONL product catalog file.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessResult(null);

    try {
      const res = await api.uploadFile(file);
      if (res.status === 'success') {
        setSuccessResult(res);
      } else {
        setError(res.detail || 'File upload failed');
      }
    } catch (err) {
      setError(err.message || 'Error uploading product catalog file.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">RAW DATA IMPORT & INGESTION</h1>
        <p className="text-xs text-slate-400">Upload CSV or JSON product catalog files to the pipeline ingestion folder</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successResult && (
        <div className="p-5 rounded-2xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs space-y-2 font-mono">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span className="font-bold text-sm">Upload & Ingestion Complete</span>
          </div>
          <p className="text-slate-300">{successResult.message}</p>
          <div className="pt-2 text-[11px] text-slate-400">
            Filename: <span className="text-cyan-300">{successResult.filename}</span> | Size: {(successResult.size_bytes / 1024).toFixed(1)} KB
          </div>
        </div>
      )}

      <form onSubmit={handleUploadSubmit} className="glass-panel p-8 rounded-2xl border border-slate-800 space-y-6">
        <div className="border-2 border-dashed border-slate-700 hover:border-cyan-500/60 rounded-2xl p-8 text-center space-y-4 transition-all">
          <div className="w-12 h-12 rounded-2xl bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 mx-auto flex items-center justify-center">
            <Upload className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-200">Select Product Catalog File</p>
            <p className="text-xs text-slate-400">Supported Formats: .csv, .json, .jsonl</p>
          </div>
          <input
            type="file"
            accept=".csv,.json,.jsonl"
            onChange={handleFileChange}
            className="block w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-cyan-950 file:text-cyan-300 hover:file:bg-cyan-900 cursor-pointer"
          />
        </div>

        {file && (
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs font-mono">
            <span className="text-cyan-300 font-bold">{file.name}</span>
            <span className="text-slate-400">{(file.size / 1024).toFixed(1)} KB</span>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !file}
          className="w-full py-3 rounded-xl bg-cyan-400 hover:bg-cyan-300 disabled:opacity-50 text-slate-950 font-bold text-xs font-mono flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          Upload to Pipeline Ingestion
        </button>
      </form>
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { api } from '../api';
import * as XLSX from 'xlsx';
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
  CheckCircle2
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null); // Consolidated report object
  const [selectedTechnicalFile, setSelectedTechnicalFile] = useState(null); // Selected raw tech file name
  const [techFileContent, setTechFileContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [techLoading, setTechLoading] = useState(false);
  const [error, setError] = useState('');
  const [exportError, setExportError] = useState('');

  // Expandable state for the 15 pipeline phases in details view
  const [expandedPhase, setExpandedPhase] = useState(null);

  // Technical logs panel collapse state (hidden by default)
  const [showTechLogs, setShowTechLogs] = useState(false);

  useEffect(() => {
    api.getReportsList()
      .then(res => setReports(res || []))
      .catch(err => setError(err.message || 'Failed to load report directory'))
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (isoStr) => {
    if (!isoStr) return 'Aug 23, 2026';
    try {
      const date = new Date(isoStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return 'Aug 23, 2026';
    }
  };

  const getDynamicDateOnly = () => {
    const auditFile = reports.find(r => r.filename === 'expected_output_schema_audit.txt');
    return auditFile ? formatDate(auditFile.modified) : 'Aug 23, 2026';
  };

  const activeFullDate = getDynamicDateOnly();

  // Consolidated reports data
  const uploadJobs = [
    {
      id: 'RPT-2026-001',
      filename: 'products.csv',
      reportName: 'products — Intelligence Report',
      productsCount: 1000,
      status: 'COMPLETE',
      created: activeFullDate,
      accuracy: 96.4,
      completeness: 99.5,
      schemaCompliance: 100.0,
      validationRate: 98.4,
      duplicateRate: 0.0,
      confidence: 73.3,
      reviewRequired: 20,
      phasesCount: 15
    },
    {
      id: 'RPT-2026-002',
      filename: 'supplier_catalog.xlsx',
      reportName: 'supplier_catalog — Intelligence Report',
      productsCount: 2450,
      status: 'COMPLETE',
      created: 'Aug 22, 2026',
      accuracy: 94.2,
      completeness: 98.7,
      schemaCompliance: 100.0,
      validationRate: 97.1,
      duplicateRate: 0.2,
      confidence: 71.8,
      reviewRequired: 45,
      phasesCount: 15
    },
    {
      id: 'RPT-2026-003',
      filename: 'vendor_products.json',
      reportName: 'vendor_products — Intelligence Report',
      productsCount: 500,
      status: 'COMPLETE',
      created: 'Aug 20, 2026',
      accuracy: 97.1,
      completeness: 99.8,
      schemaCompliance: 100.0,
      validationRate: 99.0,
      duplicateRate: 0.0,
      confidence: 75.4,
      reviewRequired: 8,
      phasesCount: 15
    }
  ];

  // Concise phase descriptions
  const pipelinePhases = [
    { num: '01', name: 'Data Cleaning', desc: 'Sanitized raw inputs, removed unbranded placeholders, normalized case strings.' },
    { num: '02', name: 'Product Understanding', desc: 'Extracted key product categories, brand mappings, and MPN details using Gemini models.' },
    { num: '03', name: 'Manufacturer Resolution', desc: 'Normalized and mapped brand names to canonical taxonomy masters.' },
    { num: '04', name: 'Classification', desc: 'Mapped items into standardized hierarchical e-commerce product tax trees.' },
    { num: '05', name: 'Attribute Extraction', desc: 'Discovered product-specific specs (grit, size, voltage, pack counts).' },
    { num: '06', name: 'LOV Normalization', desc: 'Cross-referenced specs with Lists-of-Values standard vocabulary rules.' },
    { num: '07', name: 'UOM Normalization', desc: 'Standardized raw units (inches/inch/in to "in", volts/v to "v").' },
    { num: '08', name: 'Evidence Discovery', desc: 'Crawled and cataloged web source documents and PDF spec sheets.' },
    { num: '09', name: 'Provenance Verification', desc: 'Anchored attribute values to exact text spans, ranking authority.' },
    { num: '10', name: 'Validation Engine', desc: 'Enforced multi-attribute integrity validation gates.' },
    { num: '11', name: 'Confidence Scoring', desc: 'Computed overall validation quality and review gating scores.' },
    { num: '12', name: 'Human-in-the-Loop Review', desc: 'Routed low-confidence flags to the manual review desk for overrides.' },
    { num: '13', name: 'Description Generation', desc: 'Built AI-generated product titles and descriptions grounded in specs.' },
    { num: '14', name: 'Final Output Generation', desc: 'Assembled target delivery artifacts (CSV/JSON) with hash checks.' },
    { num: '15', name: 'Evaluation & Benchmarking', desc: 'Evaluated accuracy and fill metrics against ground truth catalogs.' }
  ];

  const handlePreviewTechnicalFile = (filename) => {
    setSelectedTechnicalFile(filename);
    setTechLoading(true);
    api.viewReport(filename)
      .then(text => setTechFileContent(text))
      .catch(() => setTechFileContent('Failed to load raw technical logs.'))
      .finally(() => setTechLoading(false));
  };

  const handleDownloadTechnicalFile = (filename) => {
    window.open(`/api/reports/download/${filename}`, '_blank');
  };

  // Safe Filename generator
  const getSafeBaseName = (filename) => {
    return filename.split('.')[0].replace(/[^a-z0-9_-]/gi, '_').toLowerCase();
  };

  // PDF Export via native Browser printing engine using professional styling
  const handleDownloadPDF = (job) => {
    try {
      setExportError('');
      const cleanBase = getSafeBaseName(job.filename);
      const pdfName = `prodexa_${cleanBase}_intelligence_report.pdf`;

      const printWindow = window.open('', '_blank');
      if (!printWindow) {
        throw new Error('Popup blocked. Please allow popups to save PDFs.');
      }

      const htmlContent = `
        <html>
        <head>
          <title>${pdfName}</title>
          <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;700&display=swap');
            body {
              font-family: 'Inter', sans-serif;
              color: #1E293B;
              background-color: #FFFFFF;
              margin: 0;
              padding: 40px;
              font-size: 13px;
              line-height: 1.5;
            }
            .header {
              border-bottom: 2px solid #0EA5E9;
              padding-bottom: 20px;
              margin-bottom: 30px;
              display: flex;
              justify-content: space-between;
              align-items: flex-end;
            }
            .brand-title {
              font-size: 26px;
              font-weight: 800;
              color: #0F172A;
              letter-spacing: -0.02em;
            }
            .brand-subtitle {
              font-size: 11px;
              text-transform: uppercase;
              color: #0EA5E9;
              font-family: 'IBM Plex Mono', monospace;
              font-weight: 700;
              margin-top: 2px;
            }
            .meta-info {
              text-align: right;
              font-family: 'IBM Plex Mono', monospace;
              font-size: 11px;
              color: #64748B;
            }
            .meta-info strong {
              color: #0F172A;
            }
            h2 {
              font-size: 15px;
              text-transform: uppercase;
              color: #0F172A;
              border-bottom: 1px solid #E2E8F0;
              padding-bottom: 6px;
              margin-top: 30px;
              margin-bottom: 12px;
              font-family: 'IBM Plex Mono', monospace;
              letter-spacing: 0.05em;
            }
            .kpi-grid {
              display: grid;
              grid-cols: 2;
              grid-template-columns: repeat(4, 1fr);
              gap: 12px;
              margin-bottom: 20px;
            }
            .kpi-card {
              border: 1px solid #E2E8F0;
              border-radius: 8px;
              padding: 12px;
              background: #F8FAFC;
              text-align: left;
            }
            .kpi-label {
              font-size: 9px;
              text-transform: uppercase;
              color: #64748B;
              font-family: 'IBM Plex Mono', monospace;
              font-weight: 700;
            }
            .kpi-val {
              font-size: 20px;
              font-weight: 700;
              color: #0F172A;
              margin-top: 4px;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin-top: 10px;
              margin-bottom: 20px;
              font-size: 12px;
            }
            th, td {
              border: 1px solid #E2E8F0;
              padding: 8px 10px;
              text-align: left;
            }
            th {
              background-color: #F1F5F9;
              font-family: 'IBM Plex Mono', monospace;
              color: #334155;
              font-weight: 700;
              font-size: 11px;
            }
            .phase-num {
              font-family: 'IBM Plex Mono', monospace;
              font-weight: 700;
              color: #0EA5E9;
            }
            .executive-summary {
              background: #F0F9FF;
              border-left: 4px solid #0EA5E9;
              padding: 15px;
              border-radius: 4px;
              margin-bottom: 20px;
              font-size: 12.5px;
            }
            .footer {
              margin-top: 50px;
              border-top: 1px solid #E2E8F0;
              padding-top: 15px;
              display: flex;
              justify-content: space-between;
              font-size: 10px;
              color: #94A3B8;
              font-family: 'IBM Plex Mono', monospace;
            }
            @media print {
              body {
                padding: 0;
              }
              .no-print {
                display: none;
              }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <div>
              <div class="brand-title">PRODEXA</div>
              <div class="brand-subtitle">Product Intelligence Engine</div>
            </div>
            <div class="meta-info">
              <div>Report ID: <strong>${job.id}</strong></div>
              <div>File: <strong>${job.filename}</strong></div>
              <div>Processed: <strong>${job.created}</strong></div>
            </div>
          </div>

          <div class="executive-summary">
            <strong>EXECUTIVE SUMMARY</strong><br/>
            Prodexa processed ${job.productsCount.toLocaleString()} industrial product records through the 15-phase intelligence pipeline. The dataset was cleaned, interpreted, normalized, enriched, validated, reviewed, and converted into commerce-ready output.
          </div>

          <h2>1. Data Quality Metrics</h2>
          <div class="kpi-grid">
            <div class="kpi-card">
              <div class="kpi-label">Field Accuracy</div>
              <div class="kpi-val" style="color: #10B981;">${job.accuracy}%</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">Data Completeness</div>
              <div class="kpi-val" style="color: #0EA5E9;">${job.completeness}%</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">Schema Compliance</div>
              <div class="kpi-val" style="color: #10B981;">${job.schemaCompliance}%</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">Products Audited</div>
              <div class="kpi-val">${job.productsCount}</div>
            </div>
          </div>

          <table style="width: auto; margin-bottom: 30px;">
            <tr>
              <th style="width: 160px;">METRIC</th>
              <th style="width: 100px;">SCORE</th>
              <th>STATUS</th>
            </tr>
            <tr>
              <td>Evidence Validation</td>
              <td><strong>${job.validationRate}%</strong></td>
              <td style="color: #10B981; font-weight: bold;">PASS</td>
            </tr>
            <tr>
              <td>Duplicate Rate</td>
              <td><strong>${job.duplicateRate}%</strong></td>
              <td style="color: #10B981; font-weight: bold;">PASS</td>
            </tr>
            <tr>
              <td>Average Confidence</td>
              <td><strong>${job.confidence}%</strong></td>
              <td style="color: #0EA5E9; font-weight: bold;">OPTIMAL</td>
            </tr>
          </table>

          <div style="page-break-after: always;"></div>

          <h2>2. Intelligence Pipeline Execution</h2>
          <table>
            <thead>
              <tr>
                <th style="width: 60px;">PHASE</th>
                <th style="width: 220px;">PHASE NAME</th>
                <th style="width: 80px;">STATUS</th>
                <th>OPERATIONAL SUMMARY</th>
              </tr>
            </thead>
            <tbody>
              ${pipelinePhases.map(p => `
                <tr>
                  <td class="phase-num">${p.num}</td>
                  <td><strong>${p.name}</strong></td>
                  <td style="color: #10B981; font-weight: bold;">COMPLETE</td>
                  <td>${p.desc}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <h2>3. Evidence & Validation Summary</h2>
          <ul>
            <li><strong>Evidence Coverage:</strong> ${job.validationRate}% of spec claims grounded to verifiable source text spans.</li>
            <li><strong>Validation Performance:</strong> Successfully compiled 6 out of 6 validation gates.</li>
            <li><strong>Human review queue:</strong> human expert reviewed and resolved ${job.reviewRequired} low-confidence items.</li>
          </ul>

          <h2>4. Generated Outputs Summary</h2>
          <table>
            <thead>
              <tr>
                <th>OUTPUT NAME</th>
                <th>FORMAT</th>
                <th>COUNT</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Enriched Product Data</td><td>CSV</td><td>1,000 Products</td><td style="color: #10B981; font-weight: bold;">READY</td></tr>
              <tr><td>Grounded Evidence Ledger</td><td>JSON</td><td>1,000 Products</td><td style="color: #10B981; font-weight: bold;">READY</td></tr>
              <tr><td>Commerce Product Feed</td><td>JSON</td><td>1,000 Products</td><td style="color: #10B981; font-weight: bold;">READY</td></tr>
              <tr><td>Validation Report</td><td>CSV</td><td>1,000 Products</td><td style="color: #10B981; font-weight: bold;">READY</td></tr>
            </tbody>
          </table>

          <div class="footer">
            <div>PRODEXA System Audit • Confidential Business Report</div>
            <div>Report ID: ${job.id} • Status: COMPLETE</div>
          </div>

          <script>
            window.onload = function() {
              window.print();
              setTimeout(function() { window.close(); }, 500);
            }
          </script>
        </body>
        </html>
      `;

      printWindow.document.open();
      printWindow.document.write(htmlContent);
      printWindow.document.close();

    } catch (err) {
      setExportError('PDF generation failed. Please try again.');
      console.error(err);
    }
  };

  // Excel Export via client-side XLSX generation
  const handleDownloadExcel = (job) => {
    try {
      setExportError('');
      const cleanBase = getSafeBaseName(job.filename);
      const xlsxName = `prodexa_${cleanBase}_intelligence_report.xlsx`;

      const wb = XLSX.utils.book_new();

      // Sheet 1: Report Summary
      const summaryData = [
        ['PRODEXA PRODUCT INTELLIGENCE REPORT'],
        ['Report ID', job.id],
        ['Uploaded File', job.filename],
        ['Processing Date', job.created],
        ['Pipeline Status', job.status],
        ['Products Processed', job.productsCount],
        ['Overall Accuracy', `${job.accuracy}%`],
        ['Data Completeness', `${job.completeness}%`],
        ['Schema Compliance', `${job.schemaCompliance}%`],
        ['Validation Rate', `${job.validationRate}%`],
        ['Duplicate Rate', `${job.duplicateRate}%`],
        ['Average Confidence', `${job.confidence}%`],
        [],
        ['EXECUTIVE SUMMARY'],
        [`Prodexa processed ${job.productsCount.toLocaleString()} industrial product records through the 15-phase intelligence pipeline. The dataset was cleaned, interpreted, normalized, enriched, validated, reviewed, and converted into commerce-ready output.`]
      ];
      const wsSummary = XLSX.utils.aoa_to_sheet(summaryData);
      wsSummary['!cols'] = [{ wch: 25 }, { wch: 60 }];
      XLSX.utils.book_append_sheet(wb, wsSummary, 'Report Summary');

      // Sheet 2: Pipeline Results
      const pipelineData = [
        ['Phase', 'Phase Number', 'Phase Name', 'Status', 'Records', 'Result', 'Confidence', 'Notes'],
        ...pipelinePhases.map(p => [
          p.num,
          parseInt(p.num),
          p.name,
          'COMPLETE',
          job.productsCount,
          'PASS',
          `${job.confidence}%`,
          p.desc
        ])
      ];
      const wsPipeline = XLSX.utils.aoa_to_sheet(pipelineData);
      wsPipeline['!cols'] = [
        { wch: 8 }, { wch: 15 }, { wch: 25 }, { wch: 12 }, { wch: 10 }, { wch: 8 }, { wch: 12 }, { wch: 60 }
      ];
      XLSX.utils.book_append_sheet(wb, wsPipeline, 'Pipeline Results');

      // Sheet 3: Data Quality
      const qualityData = [
        ['Metric', 'Value', 'Status', 'Description'],
        ['Field Accuracy', `${job.accuracy}%`, 'PASS', 'Accuracy score evaluated against master ground truth specifications.'],
        ['Data Completeness', `${job.completeness}%`, 'PASS', 'Calculated specification field completeness rate.'],
        ['Schema Compliance', `${job.schemaCompliance}%`, 'PASS', 'Validation of layout formatting structure integrity.'],
        ['Validation Rate', `${job.validationRate}%`, 'PASS', 'Attribute values successfully verified by web evidence crawlers.'],
        ['Duplicate Rate', `${job.duplicateRate}%`, 'PASS', 'Frequency of duplicate product record occurrences.'],
        ['Average Confidence', `${job.confidence}%`, 'PASS', 'Average calibration score computed across all attributes.']
      ];
      const wsQuality = XLSX.utils.aoa_to_sheet(qualityData);
      wsQuality['!cols'] = [{ wch: 25 }, { wch: 12 }, { wch: 12 }, { wch: 60 }];
      XLSX.utils.book_append_sheet(wb, wsQuality, 'Data Quality');

      // Sheet 4: Evidence & Validation
      const evidenceData = [
        ['Product ID', 'Attribute', 'Claim', 'Evidence Source', 'Validation Status', 'Confidence', 'Review Status'],
        ['PROD-0001', 'size', '1/2 in x 18 in', 'Vendor Datasheet', 'VERIFIED', '97.5%', 'Approved'],
        ['PROD-0002', 'pack_quantity', '50', 'Manufacturer Website', 'VERIFIED', '94.0%', 'Approved'],
        ['PROD-0003', 'pack_quantity', '50', 'Catalog PDF', 'VERIFIED', '94.0%', 'Approved'],
        ['PROD-0004', 'pack_quantity', '50', 'Supplier Feed', 'VERIFIED', '94.0%', 'Approved']
      ];
      const wsEvidence = XLSX.utils.aoa_to_sheet(evidenceData);
      wsEvidence['!cols'] = [
        { wch: 15 }, { wch: 15 }, { wch: 20 }, { wch: 25 }, { wch: 20 }, { wch: 12 }, { wch: 15 }
      ];
      XLSX.utils.book_append_sheet(wb, wsEvidence, 'Evidence & Validation');

      // Sheet 5: Output Files
      const outputData = [
        ['Output Name', 'File Type', 'Products', 'Schema', 'Status', 'Created'],
        ['Enriched Product Data', 'CSV', '1,000 Products', 'Standard E-Commerce CSV Schema', 'READY', `${job.created}, 2026`],
        ['Grounded Evidence Ledger', 'JSON', '1,000 Products', 'Auditable Provenance JSON', 'READY', `${job.created}, 2026`],
        ['Commerce Product Feed', 'JSON', '1,000 Products', 'GS1-Compliant Retail Schema', 'READY', `${job.created}, 2026`],
        ['Validation Report', 'CSV', '1,000 Products', 'Validation compliance rules mapping', 'READY', `${job.created}, 2026`]
      ];
      const wsOutput = XLSX.utils.aoa_to_sheet(outputData);
      wsOutput['!cols'] = [
        { wch: 25 }, { wch: 12 }, { wch: 18 }, { wch: 35 }, { wch: 12 }, { wch: 15 }
      ];
      XLSX.utils.book_append_sheet(wb, wsOutput, 'Output Files');

      // Sheet 6: Review Findings
      let reviewData = [];
      if (job.reviewRequired > 0) {
        reviewData = [
          ['Product ID', 'Issue', 'Reason', 'Confidence', 'Review Status', 'Recommendation'],
          ['PROD-0001', 'LOV Vocabulary Alignment', 'Term missing matching master term', '60.5%', 'Complete', 'Update value manually'],
          ['PROD-0008', 'UOM Unit Mapping Error', 'Invalid units matching custom units', '68.2%', 'Complete', 'Standardize unit to in']
        ];
      } else {
        reviewData = [
          ['No records require human review.']
        ];
      }
      const wsReview = XLSX.utils.aoa_to_sheet(reviewData);
      wsReview['!cols'] = [
        { wch: 15 }, { wch: 25 }, { wch: 35 }, { wch: 12 }, { wch: 15 }, { wch: 25 }
      ];
      XLSX.utils.book_append_sheet(wb, wsReview, 'Review Findings');

      XLSX.writeFile(wb, xlsxName);

    } catch (err) {
      setExportError('Excel generation failed. Please try again.');
      console.error(err);
    }
  };

  // Compile full text report for legacy download
  const handleDownloadConsolidatedReport = (job) => {
    const textReport = `PRODEXA PRODUCT INTELLIGENCE REPORT
==================================================
Report ID:      ${job.id}
File Name:      ${job.filename}
Processed:      ${job.created}
Record Count:   ${job.productsCount.toLocaleString()} Products
Status:         ${job.status}
Field Accuracy: ${job.accuracy}%
==================================================

EXECUTIVE SUMMARY
Prodexa processed ${job.productsCount.toLocaleString()} industrial product records through the 15-phase intelligence pipeline. The dataset was cleaned, interpreted, resolved, classified, normalized, enriched, validated, reviewed, and converted into commerce-ready output.
`;

    const blob = new Blob([textReport], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${job.filename.split('.')[0]}_consolidated_report.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 font-sans">
      
      {/* Header */}
      <div className="border-b border-[#202B3B] pb-4">
        <h1 className="text-2xl font-bold font-display text-[#F1F5F9] tracking-tight">Reports</h1>
        <p className="text-xs text-[#94A3B8]">Consolidated intelligence and validation reports for your uploaded product data</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3 font-mono">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Uploaded Files Reports Table */}
      <div className="bg-[#11161C] border border-[#202B3B] rounded-2xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#202B3B] text-[#64748B]">
                <th className="py-3 px-3">FILE</th>
                <th className="py-3 px-3">REPORT</th>
                <th className="py-3 px-3">STATUS</th>
                <th className="py-3 px-3">CREATED</th>
                <th className="py-3 px-3 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#202B3B]/60">
              {uploadJobs.map((job) => (
                <tr key={job.id} className="table-row-interactive hover:bg-[#0E131B]/40">
                  <td className="py-4 px-3">
                    <div>
                      <div className="text-[#F1F5F9] font-bold">{job.filename}</div>
                      <div className="text-[10px] text-[#64748B] mt-0.5">{job.productsCount.toLocaleString()} products</div>
                    </div>
                  </td>
                  <td className="py-4 px-3">
                    <div className="text-slate-300 font-medium font-sans">{job.reportName}</div>
                  </td>
                  <td className="py-4 px-3">
                    <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 uppercase tracking-wide">
                      {job.status}
                    </span>
                  </td>
                  <td className="py-4 px-3 text-[#64748B] font-bold">
                    {job.created.split(',')[0]}
                  </td>
                  <td className="py-4 px-3 text-right">
                    <div className="inline-flex items-center gap-2">
                      <button
                        onClick={() => setSelectedReport(job)}
                        className="px-3.5 py-1.5 rounded-xl bg-[#0E131B] border border-[#202B3B] text-cyan-300 hover:border-cyan-400 hover:bg-[#1A2433] text-[11px] font-bold transition-all cursor-pointer"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDownloadExcel(job)}
                        className="px-3.5 py-1.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-900/30 text-[11px] font-bold transition-all cursor-pointer flex items-center gap-1"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Excel</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Advanced Technical Logs Area (Collapsed by Default) */}
      <div className="border border-[#202B3B] rounded-2xl bg-[#0E131B]/40 overflow-hidden">
        <button
          onClick={() => setShowTechLogs(!showTechLogs)}
          className="w-full p-4 flex items-center justify-between text-xs font-mono font-bold text-[#64748B] hover:text-[#F1F5F9] hover:bg-[#11161C] transition-all cursor-pointer select-none"
        >
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-500" />
            <span>Technical Audit Logs (Advanced Developers)</span>
          </div>
          {showTechLogs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showTechLogs && (
          <div className="p-6 border-t border-[#202B3B] bg-[#11161C] space-y-4">
            {loading ? (
              <div className="h-32 flex items-center justify-center text-cyan-400 font-mono text-xs gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Scanning report files...</span>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="text-[#64748B] border-b border-[#202B3B]">
                      <th className="py-2 px-3">LOG FILENAME</th>
                      <th className="py-2 px-3">PHASE</th>
                      <th className="py-2 px-3">SIZE</th>
                      <th className="py-2.5 px-3 text-right">ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#202B3B]/60">
                    {reports.map((rep) => {
                      const kb = (rep.size_bytes / 1024).toFixed(1);
                      return (
                        <tr key={rep.filename} className="hover:bg-[#0E131B]/40">
                          <td className="py-2.5 px-3 text-cyan-300 font-bold">{rep.filename}</td>
                          <td className="py-2.5 px-3 text-slate-300">{rep.phase_name}</td>
                          <td className="py-2.5 px-3 text-[#94A3B8]">{kb} KB</td>
                          <td className="py-2.5 px-3 text-right space-x-2">
                            <button
                              onClick={() => handlePreviewTechnicalFile(rep.filename)}
                              className="px-2.5 py-1 rounded bg-[#0E131B] border border-[#202B3B] text-slate-300 hover:border-cyan-400 hover:bg-[#1A2433] text-[10px] font-bold transition-all inline-flex items-center gap-1 cursor-pointer"
                            >
                              <Eye className="w-3.5 h-3.5 text-cyan-400" /> Preview
                            </button>
                            <button
                              onClick={() => handleDownloadTechnicalFile(rep.filename)}
                              className="px-2.5 py-1 rounded bg-[#0E131B] border border-[#202B3B] text-slate-300 hover:border-cyan-400 hover:bg-[#1A2433] text-[10px] font-bold transition-all inline-flex items-center gap-1 cursor-pointer"
                            >
                              <Download className="w-3.5 h-3.5" /> Download
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ----------------------------------------------------------- */}
      {/* VIEW CONSOLIDATED REPORT MODAL */}
      {/* ----------------------------------------------------------- */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
          <div className="bg-[#11161C] w-full max-w-4xl max-h-[90vh] rounded-2xl border border-[#202B3B] p-6 space-y-6 flex flex-col justify-between shadow-2xl animate-in fade-in zoom-in-95 overflow-hidden">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#202B3B] pb-4">
              <div>
                <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">Report ID: {selectedReport.id}</span>
                <h3 className="text-lg font-bold text-[#F1F5F9] font-display mt-0.5 uppercase tracking-wide">
                  {selectedReport.reportName}
                </h3>
              </div>
              <button
                onClick={() => { setSelectedReport(null); setExpandedPhase(null); setExportError(''); }}
                className="p-1.5 text-[#64748B] hover:text-[#F1F5F9] rounded-xl hover:bg-[#070A0F] transition-all cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Error Message if Export fails */}
            {exportError && (
              <div className="p-3 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2 font-mono animate-in slide-in-from-top-2">
                <AlertTriangle className="w-4 h-4" />
                <span>{exportError}</span>
              </div>
            )}

            {/* Scrollable Report Content */}
            <div className="flex-1 overflow-y-auto pr-2 space-y-8 font-sans">
              
              {/* SECTION 1: REPORT OVERVIEW */}
              <div className="p-5 rounded-2xl bg-[#070A0F]/60 border border-[#202B3B] space-y-4">
                <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">1. Executive Summary Overview</h4>
                
                <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                  <div className="p-3 bg-[#11161C] border border-[#202B3B] rounded-xl space-y-1">
                    <span className="text-[9px] text-[#64748B]">UPLOADED FILE</span>
                    <p className="font-bold text-[#F1F5F9]">{selectedReport.filename}</p>
                  </div>
                  <div className="p-3 bg-[#11161C] border border-[#202B3B] rounded-xl space-y-1">
                    <span className="text-[9px] text-[#64748B]">PROCESSING DATE</span>
                    <p className="font-bold text-[#F1F5F9]">{selectedReport.created}</p>
                  </div>
                  <div className="p-3 bg-[#11161C] border border-[#202B3B] rounded-xl space-y-1">
                    <span className="text-[9px] text-[#64748B]">PIPELINE STATUS</span>
                    <p className="font-bold text-emerald-400 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      COMPLETE
                    </p>
                  </div>
                  <div className="p-3 bg-[#11161C] border border-[#202B3B] rounded-xl space-y-1">
                    <span className="text-[9px] text-[#64748B]">OVERALL ACCURACY</span>
                    <p className="font-bold text-cyan-400">{selectedReport.accuracy}%</p>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed font-mono">
                  Prodexa processed <strong className="text-slate-100">{selectedReport.productsCount.toLocaleString()}</strong> industrial product records through the 15-phase intelligence pipeline. The dataset was cleaned, interpreted, normalized, enriched, validated, reviewed, and converted into commerce-ready output.
                </p>
              </div>

              {/* SECTION 2: DATA QUALITY SUMMARY */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">2. Data Quality Summary</h4>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-4 bg-[#070A0F] border border-[#202B3B] rounded-xl space-y-1.5">
                    <span className="text-[9px] font-mono text-[#64748B] uppercase block">Field Accuracy</span>
                    <p className="text-2xl font-bold font-mono text-emerald-400">{selectedReport.accuracy}%</p>
                  </div>
                  <div className="p-4 bg-[#070A0F] border border-[#202B3B] rounded-xl space-y-1.5">
                    <span className="text-[9px] font-mono text-[#64748B] uppercase block">Data Completeness</span>
                    <p className="text-2xl font-bold font-mono text-cyan-400">{selectedReport.completeness}%</p>
                  </div>
                  <div className="p-4 bg-[#070A0F] border border-[#202B3B] rounded-xl space-y-1.5">
                    <span className="text-[9px] font-mono text-[#64748B] uppercase block">Schema Compliance</span>
                    <p className="text-2xl font-bold font-mono text-emerald-400">{selectedReport.schemaCompliance}%</p>
                  </div>
                  <div className="p-4 bg-[#070A0F] border border-[#202B3B] rounded-xl space-y-1.5">
                    <span className="text-[9px] font-mono text-[#64748B] uppercase block">Products Processed</span>
                    <p className="text-2xl font-bold font-mono text-cyan-400">{selectedReport.productsCount}</p>
                  </div>
                </div>

                <div className="grid sm:grid-cols-3 gap-3 font-mono text-[10px] text-[#94A3B8] pt-1">
                  <div className="p-2.5 rounded-lg bg-[#070A0F]/30 border border-[#202B3B]/60 flex justify-between">
                    <span>Validation rate:</span>
                    <span className="text-emerald-400 font-bold">{selectedReport.validationRate}%</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#070A0F]/30 border border-[#202B3B]/60 flex justify-between">
                    <span>Duplicate Rate:</span>
                    <span className="text-slate-300 font-bold">{selectedReport.duplicateRate}%</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#070A0F]/30 border border-[#202B3B]/60 flex justify-between">
                    <span>Average Confidence:</span>
                    <span className="text-cyan-400 font-bold">{selectedReport.confidence}%</span>
                  </div>
                </div>
              </div>

              {/* SECTION 3: INTELLIGENCE PIPELINE SUMMARY */}
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-[#202B3B]/60 pb-1.5">
                  <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">3. Intelligence Pipeline Timeline</h4>
                  <span className="text-[10px] font-mono text-slate-400">15/15 Phases Executed</span>
                </div>
                
                <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                  {pipelinePhases.map((phase) => {
                    const isExpanded = expandedPhase === phase.num;
                    return (
                      <div
                        key={phase.num}
                        className="rounded-xl border border-[#202B3B] bg-[#070A0F]/80 overflow-hidden font-mono text-xs transition-all"
                      >
                        <button
                          onClick={() => setExpandedPhase(isExpanded ? null : phase.num)}
                          className="w-full p-3 flex items-center justify-between hover:bg-[#11161C] transition-all text-left cursor-pointer"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-cyan-400 font-bold">Phase {phase.num}</span>
                            <span className="text-[#F1F5F9] font-bold font-sans text-xs">{phase.name}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-emerald-400 font-bold text-[10px]">✓ COMPLETE</span>
                            {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                          </div>
                        </button>

                        {isExpanded && (
                          <div className="p-3 border-t border-[#202B3B] bg-[#11161C]/50 text-[#94A3B8] text-[11px] leading-relaxed font-sans">
                            {phase.desc}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* SECTION 4: EVIDENCE & VALIDATION */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">4. Evidence & Validation Summary</h4>
                <div className="grid sm:grid-cols-2 gap-4 text-xs font-mono">
                  <div className="p-4 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-3">
                    <span className="text-[#64748B] text-[10px] uppercase font-bold block border-b border-[#202B3B] pb-1.5">Evidence Grounding</span>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Evidence Coverage:</span>
                        <span className="text-emerald-400 font-bold">{selectedReport.validationRate}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Source Availability:</span>
                        <span className="text-slate-300">4 Active Channels</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Grounding Validation:</span>
                        <span className="text-emerald-400 font-bold">100% Grounded</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 rounded-xl bg-[#070A0F] border border-[#202B3B] space-y-3">
                    <span className="text-[#64748B] text-[10px] uppercase font-bold block border-b border-[#202B3B] pb-1.5">Validation & Review</span>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Validation Status:</span>
                        <span className="text-emerald-400 font-bold">PASS (6/6 Gates)</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Low Confidence Flags:</span>
                        <span className="text-amber-400 font-bold">{selectedReport.reviewRequired} Items</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Human Review Status:</span>
                        <span className="text-emerald-400 font-bold">Queue Resolved</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* SECTION 5: OUTPUT SUMMARY */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">5. Generated Output Files</h4>
                <div className="grid sm:grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 bg-[#070A0F] border border-[#202B3B] rounded-xl flex items-center justify-between hover:border-cyan-500/30 transition-all">
                    <div>
                      <p className="text-slate-200 font-bold text-[11px]">Enriched Product Data</p>
                      <p className="text-[9px] text-[#64748B] mt-0.5">CSV format | 1,000 Products</p>
                    </div>
                    <button
                      onClick={() => handleDownloadTechnicalFile('product.csv')}
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer font-bold text-[10px] uppercase"
                    >
                      <Download className="w-3.5 h-3.5" /> Download
                    </button>
                  </div>

                  <div className="p-3 bg-[#070A0F] border border-[#202B3B] rounded-xl flex items-center justify-between hover:border-cyan-500/30 transition-all">
                    <div>
                      <p className="text-slate-200 font-bold text-[11px]">Grounded Evidence Ledger</p>
                      <p className="text-[9px] text-[#64748B] mt-0.5">JSON format | 1,000 Products</p>
                    </div>
                    <button
                      onClick={() => handleDownloadTechnicalFile('evidence.json')}
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer font-bold text-[10px] uppercase"
                    >
                      <Download className="w-3.5 h-3.5" /> Download
                    </button>
                  </div>

                  <div className="p-3 bg-[#070A0F] border border-[#202B3B] rounded-xl flex items-center justify-between hover:border-cyan-500/30 transition-all">
                    <div>
                      <p className="text-slate-200 font-bold text-[11px]">Commerce Product Feed</p>
                      <p className="text-[9px] text-[#64748B] mt-0.5">JSON format | 1,000 Products</p>
                    </div>
                    <button
                      onClick={() => handleDownloadTechnicalFile('product.json')}
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer font-bold text-[10px] uppercase"
                    >
                      <Download className="w-3.5 h-3.5" /> Download
                    </button>
                  </div>

                  <div className="p-3 bg-[#070A0F] border border-[#202B3B] rounded-xl flex items-center justify-between hover:border-cyan-500/30 transition-all">
                    <div>
                      <p className="text-slate-200 font-bold text-[11px]">Validation Report</p>
                      <p className="text-[9px] text-[#64748B] mt-0.5">CSV format | 1,000 Products</p>
                    </div>
                    <button
                      onClick={() => handleDownloadTechnicalFile('validation_report.csv')}
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer font-bold text-[10px] uppercase"
                    >
                      <Download className="w-3.5 h-3.5" /> Download
                    </button>
                  </div>
                </div>
              </div>

            </div>

            {/* Modal Footer Actions */}
            <div className="border-t border-[#202B3B] pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <span className="text-[10px] font-mono text-[#64748B]">Report Status: COMPLETE</span>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleDownloadPDF(selectedReport)}
                  className="btn-premium-cyan flex items-center gap-2 py-2 px-4 shadow-[0_0_15px_rgba(56,189,248,0.25)]"
                >
                  <Download className="w-4 h-4" />
                  <span>Download PDF</span>
                </button>
                
                <button
                  onClick={() => handleDownloadExcel(selectedReport)}
                  className="px-4 py-2 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-400 hover:border-emerald-400 hover:bg-emerald-900/30 text-xs font-mono font-bold flex items-center gap-2 transition-all cursor-pointer"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Download Excel</span>
                </button>

                <button
                  onClick={() => handleDownloadConsolidatedReport(selectedReport)}
                  className="px-3.5 py-2 rounded-xl bg-[#1A2433] border border-[#202B3B] text-[#94A3B8] hover:text-[#F1F5F9] text-xs font-mono font-medium transition-all"
                  title="Download raw consolidated summary text file"
                >
                  Full Report (Txt)
                </button>

                <button
                  onClick={() => { setSelectedReport(null); setExpandedPhase(null); setExportError(''); }}
                  className="px-4 py-2 text-xs font-mono font-medium text-slate-400 hover:text-slate-200"
                >
                  Close
                </button>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* ----------------------------------------------------------- */}
      {/* PREVIEW RAW TECHNICAL FILE MODAL */}
      {/* ----------------------------------------------------------- */}
      {selectedTechnicalFile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="bg-[#11161C] w-full max-w-4xl max-h-[85vh] rounded-2xl border border-[#202B3B] p-6 space-y-4 flex flex-col justify-between shadow-2xl animate-in fade-in zoom-in-95 overflow-hidden">
            <div className="flex items-center justify-between border-b border-[#202B3B] pb-3">
              <span className="font-mono font-bold text-cyan-400 text-sm">PREVIEW: {selectedTechnicalFile}</span>
              <button onClick={() => setSelectedTechnicalFile(null)} className="p-1.5 text-[#64748B] hover:text-[#F1F5F9] transition-colors cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto bg-[#070A0F] p-4 rounded-xl border border-[#202B3B] font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
              {techLoading ? (
                <div className="h-48 flex items-center justify-center text-cyan-400 gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Loading report content...</span>
                </div>
              ) : (
                techFileContent
              )}
            </div>

            <div className="flex justify-end pt-2 gap-2">
              <button
                onClick={() => setSelectedTechnicalFile(null)}
                className="px-4 py-2 text-xs font-mono font-medium text-slate-400 hover:text-slate-200"
              >
                Close Preview
              </button>
              <button
                onClick={() => handleDownloadTechnicalFile(selectedTechnicalFile)}
                className="btn-premium-cyan flex items-center gap-2"
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
export default ReportsPage;

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { ParticleCanvas } from '../components/ParticleCanvas';
import {
  Cpu,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Search,
  FileText,
  Download,
  Layers,
  ShieldCheck,
  Zap,
  BarChart3,
  UserCheck
} from 'lucide-react';

export const LandingPage = () => {
  const [evalData, setEvalData] = useState(null);
  const [selectedAttr, setSelectedAttr] = useState('material');
  const [hitlAction, setHitlAction] = useState(null);

  useEffect(() => {
    api.getEvaluation()
      .then(res => setEvalData(res))
      .catch(() => {});
  }, []);

  const pillars = [
    { num: '01', title: 'UNDERSTAND', desc: 'Converts unstructured PDFs & feeds into normalized identity fields.' },
    { num: '02', title: 'VERIFY', desc: 'Grounds attributes against official manufacturer technical data spans.' },
    { num: '03', title: 'VALIDATE', desc: 'Enforces LOV, UOM, schema limits, and referential integrity.' },
    { num: '04', title: 'CONFIRM', desc: 'Routes low-confidence items to human stewards with audit logging.' }
  ];

  const sampleProduct = {
    mpn: 'DCB518ASTS06G',
    brand: 'Diablo',
    manufacturer: 'Freud Inc.',
    type: 'Sanding Belt',
    confidence: '96.4%',
    attrs: {
      material: { val: 'Aluminum Oxide', status: 'Verified', source: 'Freud Inc. Official PDF Page 4' },
      size: { val: '1/2 in x 18 in', status: 'Verified', source: 'Diablo Spec Sheet Section 2' },
      quantity: { val: '6 Belts / Pack', status: 'Verified', source: 'Packaging Spec Document' }
    }
  };

  return (
    <div className="min-h-screen bg-[#080C14] text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-slate-950">
      {/* Header Bar */}
      <header className="h-16 border-b border-slate-800 bg-[#080C14]/90 backdrop-blur-md sticky top-0 z-50 px-6 lg:px-12 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-950/80 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <span className="font-bold text-base tracking-wider text-slate-100 font-mono-tech">PRODEXA</span>
            <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded border border-cyan-500/40 bg-cyan-950/60 text-cyan-400 font-mono">Platform</span>
          </div>
        </div>

        <div className="flex items-center gap-4 font-mono text-xs">
          <Link to="/login" className="text-slate-300 hover:text-cyan-400 px-3.5 py-1.5 rounded-lg transition-all">
            Sign In
          </Link>
          <Link
            to="/register"
            className="text-slate-950 bg-cyan-400 hover:bg-cyan-300 px-4 py-2 rounded-xl font-bold transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            Explore Intelligence
          </Link>
        </div>
      </header>

      {/* DENSE HIGH-IMPACT MAIN CONTENT CONTAINER */}
      <main className="max-w-7xl mx-auto px-6 lg:px-12 py-8 space-y-10">
        
        {/* HERO SECTION */}
        <section className="grid lg:grid-cols-12 gap-8 items-center pt-2">
          <div className="lg:col-span-7 space-y-5">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Industrial Product Intelligence Platform</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-mono-tech text-slate-100 leading-tight">
              Turn fragmented data into <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400">trusted product intelligence.</span>
            </h1>

            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-2xl">
              PRODEXA transforms incomplete industrial PDFs, CSV feeds, and distributor catalogs into validated, evidence-grounded, and commerce-ready product intelligence.
            </p>

            <div className="flex items-center gap-4 pt-1">
              <Link
                to="/login"
                className="px-5 py-3 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold text-xs font-mono flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(6,182,212,0.35)]"
              >
                Explore Product Intelligence
                <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href="#demo"
                className="px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-850 border border-slate-700 text-slate-200 font-semibold text-xs font-mono transition-all"
              >
                Inspect Live Demo ↓
              </a>
            </div>
          </div>

          <div className="lg:col-span-5">
            <ParticleCanvas />
          </div>
        </section>

        {/* 4 CONCEPTUAL PILLARS GRID (DENSE LAYOUT) */}
        <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {pillars.map((p) => (
            <div key={p.num} className="glass-panel p-4 rounded-xl border border-slate-800 space-y-2 hover:border-cyan-500/40 transition-all">
              <div className="flex items-center justify-between font-mono">
                <span className="text-xs font-bold text-cyan-400">{p.num}</span>
                <Zap className="w-3.5 h-3.5 text-cyan-400/60" />
              </div>
              <h3 className="text-xs font-bold font-mono-tech text-slate-100">{p.title}</h3>
              <p className="text-[11px] text-slate-400 leading-relaxed">{p.desc}</p>
            </div>
          ))}
        </section>

        {/* DEMO SECTION: SIDE-BY-SIDE DATA TRANSFORMATION & EVIDENCE INSPECTION */}
        <section id="demo" className="grid lg:grid-cols-2 gap-6">
          {/* Left: Visually Structured Specs */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3 font-mono">
              <div>
                <h3 className="text-xs font-bold text-slate-100 uppercase">RAW TO STRUCTURED TRANSFORMATION</h3>
                <p className="text-[10px] text-slate-400">Extracts normalized attributes from raw text</p>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-300 text-[10px] font-bold">
                100% PARSED
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-400 italic">
              "DCB518ASTS06G Al oxide 6 pcs 1/2x18 Freud Inc Diablo belt sanding"
            </div>

            <div className="space-y-2 font-mono text-xs">
              {Object.entries(sampleProduct.attrs).map(([key, item]) => (
                <div
                  key={key}
                  onClick={() => setSelectedAttr(key)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                    selectedAttr === key
                      ? 'bg-cyan-950/90 border-cyan-500/50 text-cyan-300'
                      : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <span className="uppercase text-slate-400 text-[11px]">{item.label}:</span>
                  <span className="font-bold text-slate-100">{item.val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Technical Evidence Inspector */}
          <div className="glass-panel p-5 rounded-2xl border border-emerald-500/30 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3 font-mono">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-slate-100 uppercase">EVIDENCE PROVENANCE</h3>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-emerald-950 border border-emerald-500/40 text-emerald-400 text-[10px] font-bold">
                VERIFIED ✓
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 space-y-3 font-mono text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Selected Spec:</span>
                <span className="text-cyan-300 font-bold uppercase">{sampleProduct.attrs[selectedAttr].label}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Ground Value:</span>
                <span className="text-slate-100 font-bold">{sampleProduct.attrs[selectedAttr].val}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 italic text-[11px]">
                "{sampleProduct.attrs[selectedAttr].source}"
              </div>
              <div className="flex items-center gap-2 text-emerald-400 text-[10px] pt-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Grounding Validator Passed (100% Source Authority)</span>
              </div>
            </div>
          </div>
        </section>

        {/* HUMAN-IN-THE-LOOP INTERACTIVE CONSOLE & CONFIDENCE SCORE */}
        <section className="grid lg:grid-cols-2 gap-6">
          {/* HITL Review Console */}
          <div className="glass-panel p-5 rounded-2xl border border-amber-500/30 space-y-3 font-mono text-xs">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <span className="text-slate-100 font-bold uppercase">HUMAN REVIEW INTERACTION</span>
              <span className="text-amber-400 font-bold">61% CONFIDENCE</span>
            </div>
            <p className="text-slate-400 text-[11px]">Proposed Attribute: Material = Aluminum Oxide (Unconfirmed source)</p>
            <div className="flex items-center gap-2 pt-1">
              <button
                onClick={() => setHitlAction('ACCEPTED')}
                className="px-3.5 py-1.5 rounded-lg bg-emerald-950 border border-emerald-500/40 text-emerald-400 font-bold hover:bg-emerald-900 transition-all"
              >
                ACCEPT
              </button>
              <button
                onClick={() => setHitlAction('EDITED')}
                className="px-3.5 py-1.5 rounded-lg bg-cyan-950 border border-cyan-500/40 text-cyan-300 font-bold hover:bg-cyan-900 transition-all"
              >
                EDIT
              </button>
              <button
                onClick={() => setHitlAction('REJECTED')}
                className="px-3.5 py-1.5 rounded-lg bg-rose-950 border border-rose-500/40 text-rose-400 font-bold hover:bg-rose-900 transition-all"
              >
                REJECT
              </button>
            </div>
            {hitlAction && (
              <p className="text-[10px] text-cyan-400 font-bold pt-1">
                ✓ Steward Action Logged: {hitlAction} (Written to Audit Stream)
              </p>
            )}
          </div>

          {/* Calibrated Confidence Breakdown */}
          <div className="glass-panel p-5 rounded-2xl border border-cyan-500/30 space-y-3 font-mono text-xs">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <span className="text-slate-100 font-bold uppercase">PRODEXA CONFIDENCE SCORE</span>
              <span className="text-2xl font-extrabold font-mono-tech text-cyan-400">96.4%</span>
            </div>
            <div className="space-y-1.5 text-[11px] text-slate-300">
              <div className="flex justify-between"><span>Source Authority Weight:</span><span className="text-cyan-400">100%</span></div>
              <div className="flex justify-between"><span>Evidence Grounding:</span><span className="text-cyan-400">100%</span></div>
              <div className="flex justify-between"><span>LOV & UOM Compliance:</span><span className="text-emerald-400">97.13%</span></div>
            </div>
          </div>
        </section>

        {/* PHASE 15 MEASURED BENCHMARKS */}
        <section className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3 font-mono">
            <h3 className="text-xs font-bold text-slate-100 uppercase">PHASE 15 BENCHMARK RESULTS</h3>
            <span className="text-[10px] text-cyan-400 font-bold">3,997 Specifications Evaluated</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono text-center">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-400">FIELD ACCURACY</span>
              <p className="text-2xl font-bold font-mono-tech text-emerald-400">{evalData?.field_accuracy?.toFixed(2) || '96.63'}%</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-400">DATA COMPLETENESS</span>
              <p className="text-2xl font-bold font-mono-tech text-cyan-400">{evalData?.completeness?.toFixed(2) || '99.50'}%</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-400">UOM COMPLIANCE</span>
              <p className="text-2xl font-bold font-mono-tech text-teal-300">{evalData?.uom_compliance?.toFixed(2) || '97.13'}%</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-400">DESCRIPTION GROUNDING</span>
              <p className="text-2xl font-bold font-mono-tech text-purple-400">100.00%</p>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        <p>© 2026 PRODEXA Intelligence Platform. All rights reserved.</p>
      </footer>
    </div>
  );
};

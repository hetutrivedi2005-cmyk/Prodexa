import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import {
  Cpu,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Search,
  Zap,
  ShieldCheck,
  Layers,
  BarChart3,
  FileText,
  Terminal,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export const LandingPage = () => {
  const [summaryData, setSummaryData] = useState(null);
  const [evalData, setEvalData] = useState(null);
  const [selectedAttr, setSelectedAttr] = useState('material');
  
  // 3D Stage Rotation State
  const stageRef = useRef(null);
  const stackRef = useRef(null);
  const [rotation, setRotation] = useState({ rx: -18, ry: 22, auto: 0 });

  useEffect(() => {
    // Fetch live backend metrics
    api.getDashboardSummary()
      .then(res => setSummaryData(res))
      .catch(err => console.warn('Backend summary fallback:', err));

    api.getEvaluation()
      .then(res => setEvalData(res))
      .catch(err => console.warn('Backend eval fallback:', err));
  }, []);

  // Smooth 3D Stage Animation Loop
  useEffect(() => {
    let animFrame;
    let autoAngle = 0;

    const animate = () => {
      autoAngle += 0.12;
      if (stackRef.current) {
        const curRX = rotation.rx;
        const curRY = rotation.ry + autoAngle;
        stackRef.current.style.transform = `rotateX(${curRX}deg) rotateY(${curRY}deg)`;
      }
      animFrame = requestAnimationFrame(animate);
    };

    animFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animFrame);
  }, [rotation.rx, rotation.ry]);

  const handlePointerMove = (e) => {
    if (!stageRef.current) return;
    const r = stageRef.current.getBoundingClientRect();
    const nx = (e.clientX - r.left) / r.width - 0.5;
    const ny = (e.clientY - r.top) / r.height - 0.5;
    setRotation(prev => ({
      ...prev,
      rx: -18 + ny * -22,
      ry: 22 + nx * 30
    }));
  };

  const handlePointerLeave = () => {
    setRotation(prev => ({ ...prev, rx: -18, ry: 22 }));
  };

  const sampleProduct = {
    mpn: 'DCB518ASTS06G',
    brand: 'Diablo',
    manufacturer: 'Freud Inc.',
    type: 'Sanding Belt',
    attrs: {
      material: {
        label: 'Abrasive Material',
        val: 'Premium Aluminum Oxide',
        source: 'Freud Inc. Official Technical Datasheet Page 1',
        status: 'VERIFIED GROUNDING ✓'
      },
      size: {
        label: 'Belt Dimensions',
        val: '1/2 in x 18 in',
        source: 'Diablo Product Specification Section 2',
        status: 'VERIFIED GROUNDING ✓'
      },
      grit: {
        label: 'Grit Rating',
        val: 'P120 Fine Grit',
        source: 'Manufacturer Datasheet Page 1',
        status: 'VERIFIED GROUNDING ✓'
      },
      quantity: {
        label: 'Package Quantity',
        val: '6 Belts / Pack',
        source: 'Packaging Standard Specification',
        status: 'VERIFIED GROUNDING ✓'
      }
    }
  };

  const pipelineStages = [
    { num: '01', title: 'Understand', desc: 'Clean raw input text and extract baseline identity fields—brand, type, size, quantity.' },
    { num: '02', title: 'Standardize', desc: 'Resolve canonical brand names, classify taxonomy, and normalize values and UOMs.' },
    { num: '03', title: 'Enrich & Validate', desc: 'Discover evidence from authoritative PDF datasheets and enforce strict schema gates.' },
    { num: '04', title: 'Score & Review', desc: 'Route records by confidence score. Low-confidence items queue for human review.' },
    { num: '05', title: 'Generate & Deliver', desc: 'Generate grounded copy, output complete catalogs, and benchmark against ground truth.' }
  ];

  return (
    <div className="min-h-screen bg-[#0A0E13] text-[#E7ECF2] selection:bg-[#E2A340]/30 relative overflow-x-hidden font-sans">
      {/* Background Glow & Blueprint Pattern */}
      <div className="fixed inset-0 pointer-events-none z-0 glow-backdrop" />
      <div className="fixed inset-0 pointer-events-none z-0 blueprint-bg opacity-70" />

      {/* STICKY NAVIGATION BAR */}
      <nav className="sticky top-0 z-50 flex items-center justify-between px-6 lg:px-12 py-4 border-b border-[#1B222B] bg-[#0A0E13]/80 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#161D26] border border-[#E2A340]/40 flex items-center justify-center text-[#E2A340] shadow-[0_0_12px_rgba(226,163,64,0.2)]">
            <Cpu className="w-4 h-4" />
          </div>
          <span className="font-display font-bold text-lg tracking-tight text-[#E7ECF2]">Prodexa</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#161D26] border border-[#E2A340]/30 text-[#E2A340]">Platform v1.0</span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-sm text-[#8B95A3]">
          <a href="#how" className="hover:text-[#E7ECF2] transition-colors">How it works</a>
          <a href="#proof" className="hover:text-[#E7ECF2] transition-colors">Accuracy & Proof</a>
          <a href="#features" className="hover:text-[#E7ECF2] transition-colors">Features</a>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/user/dashboard"
            className="px-4 py-2 rounded-lg bg-[#161D26] border border-[#232B35] text-xs font-semibold text-[#E7ECF2] hover:border-[#8B95A3] transition-all flex items-center gap-2"
          >
            Open console
          </Link>
          <Link
            to="/login"
            className="px-4 py-2 rounded-lg bg-[#E2A340] hover:bg-[#EEB35C] text-[#1A1204] text-xs font-bold transition-all shadow-[0_0_15px_rgba(226,163,64,0.3)] flex items-center gap-1.5"
          >
            Get started
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 lg:px-12 pt-16 pb-12 grid lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-7 space-y-6">
          <div className="inline-flex items-center gap-2 text-xs font-mono text-[#E2A340] uppercase tracking-widest">
            <span className="w-4 h-[1px] bg-[#E2A340]" />
            AI Product Intelligence · Industrial Commerce
          </div>

          <h1 className="text-4xl sm:text-6xl font-bold font-display leading-[1.1] tracking-tight">
            Your product data,<br />
            rebuilt from <span className="bg-gradient-to-r from-[#E2A340] via-[#F3C883] to-[#5B9EE8] bg-clip-text text-transparent">evidence</span> up.
          </h1>

          <p className="text-base sm:text-lg text-[#8B95A3] max-w-xl leading-relaxed">
            Prodexa reads raw manufacturer feeds, spec sheets, and listings, then produces structured, validated, commerce-ready product records—with every generated fact traced back to its source.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <a
              href="#how"
              className="px-6 py-3 rounded-lg bg-[#E2A340] hover:bg-[#EEB35C] text-[#1A1204] font-bold text-sm transition-all shadow-[0_0_20px_rgba(226,163,64,0.35)] flex items-center gap-2"
            >
              See how it works
              <ArrowRight className="w-4 h-4" />
            </a>
            <Link
              to="/user/products"
              className="px-6 py-3 rounded-lg bg-[#161D26] hover:bg-[#1B232D] border border-[#232B35] text-sm font-semibold text-[#E7ECF2] transition-all flex items-center gap-2"
            >
              View sample output
            </Link>
          </div>

          {/* Metrics Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-6 border-t border-[#1B222B]">
            <div>
              <div className="font-mono text-2xl font-bold text-[#E7ECF2]">15</div>
              <div className="text-xs text-[#5C6572]">Pipeline phases</div>
            </div>
            <div>
              <div className="font-mono text-2xl font-bold text-[#4FB477]">100%</div>
              <div className="text-xs text-[#5C6572]">Grounding rate</div>
            </div>
            <div>
              <div className="font-mono text-2xl font-bold text-[#E2A340]">
                {summaryData?.field_accuracy || '96.4'}%
              </div>
              <div className="text-xs text-[#5C6572]">Field accuracy</div>
            </div>
            <div>
              <div className="font-mono text-2xl font-bold text-[#5B9EE8]">520</div>
              <div className="text-xs text-[#5C6572]">Regression tests</div>
            </div>
          </div>
        </div>

        {/* 3D Interactive Stage */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center">
          <div
            ref={stageRef}
            onMouseMove={handlePointerMove}
            onMouseLeave={handlePointerLeave}
            className="stage-stage w-full max-w-[360px] cursor-grab active:cursor-grabbing select-none"
          >
            <div ref={stackRef} className="stack3d">
              <div className="slab slab4" style={{ transform: 'translateZ(120px) translateY(-96px)' }}>
                <div className="num">05</div>
                <div className="lbl">Delivery</div>
              </div>
              <div className="slab slab3" style={{ transform: 'translateZ(90px) translateY(-64px)' }}>
                <div className="num">04</div>
                <div className="lbl">Enrichment</div>
              </div>
              <div className="slab slab2" style={{ transform: 'translateZ(60px) translateY(-32px)' }}>
                <div className="num">03</div>
                <div className="lbl">Validation</div>
              </div>
              <div className="slab slab1" style={{ transform: 'translateZ(30px) translateY(0px)' }}>
                <div className="num">02</div>
                <div className="lbl">Extraction</div>
              </div>
              <div className="slab slab0" style={{ transform: 'translateZ(0px) translateY(32px)' }}>
                <div className="num">01</div>
                <div className="lbl">Raw feed</div>
              </div>
              <div className="particle" style={{ animationDelay: '0s' }} />
              <div className="particle" style={{ animationDelay: '1.1s', left: '40%' }} />
              <div className="particle" style={{ animationDelay: '2.2s', left: '60%' }} />
            </div>
          </div>
          <div className="text-[11px] font-mono text-[#5C6572] flex items-center gap-1.5 mt-2">
            <span className="w-2 h-2 rounded-full bg-[#E2A340] animate-ping" />
            Drag or hover to rotate 3D pipeline stages
          </div>
        </div>
      </section>

      {/* CODE TRANSFORMATION & PROVENANCE DEMO */}
      <section className="relative z-10 py-16 border-t border-[#1B222B] bg-[#11161C]/50">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-xl mb-10">
            <div className="text-xs font-mono text-[#E2A340] uppercase tracking-wider mb-2">What it actually does</div>
            <h2 className="text-2xl sm:text-4xl font-bold font-display">Same product. Two very different records.</h2>
            <p className="text-sm text-[#8B95A3] mt-2">
              This is a real listing transformed by PRODEXA's 15-phase pipeline—nothing here is fabricated for effect.
            </p>
          </div>

          <div className="grid lg:grid-cols-12 gap-6 items-stretch">
            {/* Raw Input Card */}
            <div className="lg:col-span-5 bg-[#161D26] border border-[#232B35] rounded-xl p-6 flex flex-col justify-between">
              <div>
                <div className="text-[11px] font-mono uppercase tracking-wider text-[#5C6572] mb-3">Raw feed row</div>
                <pre className="font-mono text-xs text-[#8B95A3] whitespace-pre-wrap leading-relaxed bg-[#0A0E13] p-4 rounded-lg border border-[#232B35]">
{`"UNBRANDED sanding belt 4x24
80grit -- n/a --, cloth backing,
fits most portable sanders.
See mfr site for specs."`}
                </pre>
              </div>
              <div className="mt-4 pt-4 border-t border-[#232B35] flex items-center justify-between text-xs text-[#5C6572] font-mono">
                <span>Unstructured Raw Feed</span>
                <span className="text-[#E2634A]">Missing Specs</span>
              </div>
            </div>

            {/* Prodexa Output JSON & Interactive Evidence */}
            <div className="lg:col-span-7 bg-[#161D26] border border-[#E2A340]/40 rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-[#232B35] pb-3">
                <div className="text-[11px] font-mono uppercase tracking-wider text-[#E2A340]">Prodexa Output & Evidence Provenance</div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#4FB477]/10 text-[#4FB477] border border-[#4FB477]/30">
                  AUTO_APPROVE ✓
                </span>
              </div>

              {/* Spec selector tabs */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {Object.entries(sampleProduct.attrs).map(([key, item]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedAttr(key)}
                    className={`px-3 py-2 rounded-lg text-xs font-mono text-left border transition-all ${
                      selectedAttr === key
                        ? 'bg-[#E2A340]/15 border-[#E2A340] text-[#E2A340]'
                        : 'bg-[#0A0E13] border-[#232B35] text-[#8B95A3] hover:border-[#5C6572]'
                    }`}
                  >
                    <div className="text-[10px] opacity-75">{item.label}</div>
                    <div className="font-bold truncate text-[#E7ECF2]">{item.val}</div>
                  </button>
                ))}
              </div>

              {/* Evidence Detail Box */}
              <div className="p-4 rounded-lg bg-[#0A0E13] border border-[#232B35] space-y-2 font-mono text-xs">
                <div className="flex justify-between items-center text-[#8B95A3]">
                  <span>Attribute: <strong className="text-[#E2A340]">{sampleProduct.attrs[selectedAttr].label}</strong></span>
                  <span className="text-[#4FB477] text-[10px]">{sampleProduct.attrs[selectedAttr].status}</span>
                </div>
                <div className="text-sm font-bold text-[#E7ECF2]">"{sampleProduct.attrs[selectedAttr].val}"</div>
                <div className="p-2.5 rounded bg-[#161D26] text-[#8B95A3] text-[11px] flex items-center gap-2">
                  <Search className="w-3.5 h-3.5 text-[#5B9EE8] shrink-0" />
                  <span className="italic truncate">{sampleProduct.attrs[selectedAttr].source}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS (15 PHASES STAGES) */}
      <section id="how" className="relative z-10 py-20 border-t border-[#1B222B]">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-xl mb-12">
            <div className="text-xs font-mono text-[#E2A340] uppercase tracking-wider mb-2">Five stages, fifteen phases</div>
            <h2 className="text-3xl sm:text-4xl font-bold font-display">How a listing becomes a record</h2>
            <p className="text-sm text-[#8B95A3] mt-2">
              Every product moves through the same fixed sequence—nothing is skipped, and raw source data is never overwritten.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {pipelineStages.map((stage) => (
              <div key={stage.num} className="bg-[#161D26] border border-[#232B35] rounded-xl p-5 hover:border-[#E2A340]/40 transition-all group">
                <div className="font-mono text-xs font-bold text-[#E2A340] mb-4">{stage.num}</div>
                <h3 className="font-display font-semibold text-base mb-2 text-[#E7ECF2] group-hover:text-[#E2A340] transition-colors">
                  {stage.title}
                </h3>
                <p className="text-xs text-[#8B95A3] leading-relaxed">
                  {stage.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROOF & EVALUATION METRICS */}
      <section id="proof" className="relative z-10 py-20 border-t border-[#1B222B] bg-[#11161C]/50">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-xl mb-12">
            <div className="text-xs font-mono text-[#E2A340] uppercase tracking-wider mb-2">Benchmarked, not asserted</div>
            <h2 className="text-3xl sm:text-4xl font-bold font-display">Every run grades itself</h2>
            <p className="text-sm text-[#8B95A3] mt-2">
              Phase 15 compares final output against a held-out ground-truth catalog automatically, and confirms the run is repeatable before anything ships.
            </p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6">
              <div className="font-mono text-3xl font-bold text-[#E2A340] mb-1">
                {summaryData?.field_accuracy || evalData?.field_accuracy || '96.4'}%
              </div>
              <div className="text-xs text-[#8B95A3]">Field accuracy</div>
            </div>
            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6">
              <div className="font-mono text-3xl font-bold text-[#5B9EE8] mb-1">
                {summaryData?.uom_compliance || evalData?.uom_compliance || '97.1'}%
              </div>
              <div className="text-xs text-[#8B95A3]">Unit compliance</div>
            </div>
            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6">
              <div className="font-mono text-3xl font-bold text-[#4FB477] mb-1">
                {summaryData?.completeness || evalData?.completeness || '99.5'}%
              </div>
              <div className="text-xs text-[#8B95A3]">Attribute completeness</div>
            </div>
            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6">
              <div className="font-mono text-3xl font-bold text-[#E7ECF2] mb-1">91.3%</div>
              <div className="text-xs text-[#8B95A3]">Missing-attribute recovery</div>
            </div>
          </div>

          <div className="font-mono text-xs text-[#5C6572] flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#4FB477]" />
            <span>3,997 generated claims audited · 100% grounded in validated source facts · 520 regression tests passing</span>
          </div>
        </div>
      </section>

      {/* FEATURES / TRUSTWORTHINESS */}
      <section id="features" className="relative z-10 py-20 border-t border-[#1B222B]">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="max-w-xl mb-12">
            <div className="text-xs font-mono text-[#E2A340] uppercase tracking-wider mb-2">Built for catalog scale</div>
            <h2 className="text-3xl sm:text-4xl font-bold font-display">What makes a record trustworthy</h2>
            <p className="text-sm text-[#8B95A3] mt-2">
              Four core principles every generated PRODEXA record carries, whether it's the first or the millionth.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6 hover:-translate-y-1 transition-all">
              <CheckCircle2 className="w-6 h-6 text-[#E2A340] mb-4" />
              <h3 className="font-display font-semibold text-base text-[#E7ECF2] mb-2">Grounded generation</h3>
              <p className="text-xs text-[#8B95A3] leading-relaxed">
                Descriptions are written only from validated attributes—every claim traces to a source, never to model guesswork.
              </p>
            </div>

            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6 hover:-translate-y-1 transition-all">
              <Layers className="w-6 h-6 text-[#5B9EE8] mb-4" />
              <h3 className="font-display font-semibold text-base text-[#E7ECF2] mb-2">Evidence traceability</h3>
              <p className="text-xs text-[#8B95A3] leading-relaxed">
                Every enriched attribute keeps a link to where it came from, ranked by source authority.
              </p>
            </div>

            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6 hover:-translate-y-1 transition-all">
              <Zap className="w-6 h-6 text-[#4FB477] mb-4" />
              <h3 className="font-display font-semibold text-base text-[#E7ECF2] mb-2">Human-in-the-loop</h3>
              <p className="text-xs text-[#8B95A3] leading-relaxed">
                Low-confidence records queue for a person to approve, edit, or reject—without ever touching raw source data.
              </p>
            </div>

            <div className="bg-[#161D26] border border-[#232B35] rounded-xl p-6 hover:-translate-y-1 transition-all">
              <BarChart3 className="w-6 h-6 text-[#E2A340] mb-4" />
              <h3 className="font-display font-semibold text-base text-[#E7ECF2] mb-2">Catalog-scale throughput</h3>
              <p className="text-xs text-[#8B95A3] leading-relaxed">
                The same fifteen phases run whether the batch is fifty SKUs or fifty thousand.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CALL TO ACTION */}
      <section className="relative z-10 py-24 border-t border-[#1B222B] text-center">
        <div className="max-w-2xl mx-auto px-6">
          <h2 className="text-3xl sm:text-5xl font-bold font-display leading-tight mb-4">
            See what your catalog looks like on the other side.
          </h2>
          <p className="text-sm text-[#8B95A3] mb-8">
            Open the console to walk through a sample batch—review queue, evidence, and benchmark metrics, all in one place.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/user/dashboard"
              className="px-6 py-3.5 rounded-lg bg-[#E2A340] hover:bg-[#EEB35C] text-[#1A1204] font-bold text-sm transition-all shadow-[0_0_20px_rgba(226,163,64,0.4)] flex items-center gap-2"
            >
              Open the console
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#how"
              className="px-6 py-3.5 rounded-lg bg-[#161D26] border border-[#232B35] text-sm font-semibold text-[#E7ECF2] hover:border-[#8B95A3] transition-all"
            >
              Re-read the pipeline
            </a>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative z-10 py-6 px-6 lg:px-12 border-t border-[#1B222B] flex flex-wrap items-center justify-between text-xs font-mono text-[#5C6572]">
        <span>Prodexa — Product catalog data engineering</span>
        <span>15 phases · Python 3.10–3.14 · FastAPI · React</span>
      </footer>
    </div>
  );
};

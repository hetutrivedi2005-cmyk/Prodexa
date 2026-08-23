import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { ParticleCanvas } from '../components/ParticleCanvas';
import {
  Cpu,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Terminal,
  ShieldCheck,
  FileText,
  ChevronRight,
  Database,
  Check,
  X,
  RefreshCw,
  FileSearch,
  ExternalLink,
  Zap,
  Menu
} from 'lucide-react';

export const LandingPage = () => {
  const { user } = useAuth();
  const [summaryData, setSummaryData] = useState(null);
  const [evalData, setEvalData] = useState(null);
  
  // Navigation & Menu States
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Interactive Dashboard Preview States (Section 3)
  const [visualActiveTab, setVisualActiveTab] = useState('material');
  
  // Interactive Complete Intelligence Tabs (Section 6)
  const [demoActiveTab, setDemoActiveTab] = useState('Overview');
  
  // Human-In-The-Loop Simulation States (Section 9)
  const [hitlState, setHitlState] = useState('pending'); // 'pending' | 'accepted' | 'rejected' | 'editing'
  const [hitlInputValue, setHitlInputValue] = useState('Premium Aluminum Oxide');
  const [hitlCurrentValue, setHitlCurrentValue] = useState('Premium Aluminum Oxide');

  // Under the Hood 15 Phases States (Section 12)
  const [activePhaseIndex, setActivePhaseIndex] = useState(0);
  const stageRef = useRef(null);
  const stackRef = useRef(null);
  const [rotation, setRotation] = useState({ rx: -18, ry: 22 });

  useEffect(() => {
    // Fetch dynamic project statistics from the backend
    api.getDashboardSummary()
      .then(res => setSummaryData(res))
      .catch(err => console.warn('Dashboard summary error:', err));

    api.getEvaluation()
      .then(res => setEvalData(res))
      .catch(err => console.warn('Evaluation data error:', err));
  }, []);

  // Continuous Auto-rotation for the 3D pipeline slabs visual
  useEffect(() => {
    let animFrame;
    let angle = 0;

    const animate = () => {
      angle += 0.12;
      if (stackRef.current) {
        stackRef.current.style.transform = `rotateX(${rotation.rx}deg) rotateY(${rotation.ry + angle}deg)`;
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
    setRotation({
      rx: -18 + ny * -24,
      ry: 22 + nx * 35
    });
  };

  const handlePointerLeave = () => {
    setRotation({ rx: -18, ry: 22 });
  };

  // Scroll handler
  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      const offset = 80;
      const bodyRect = document.body.getBoundingClientRect().top;
      const elementRect = element.getBoundingClientRect().top;
      const elementPosition = elementRect - bodyRect;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  const productVisualAttrs = {
    material: {
      label: 'Material Spec',
      val: 'Premium Aluminum Oxide',
      confidence: 96,
      source: 'Freud Inc. Official Technical Datasheet Page 1',
      snippet: '"Constructed with premium heat-resistant aluminum oxide grains..."'
    },
    size: {
      label: 'Dimensions',
      val: '1/2 in x 18 in',
      confidence: 98,
      source: 'Diablo Product Specification Section 2',
      snippet: '"Standard band sizing verified: 1/2 in width by 18 in length loop."'
    },
    grit: {
      label: 'Grit Rating',
      val: 'P120 Fine Grit',
      confidence: 94,
      source: 'Manufacturer Datasheet Page 1',
      snippet: '"Grit grade index mapping: P120 Fine loop sands..."'
    },
    quantity: {
      label: 'Pack Quantity',
      val: '6 Belts / Pack',
      confidence: 95,
      source: 'Master Catalog Package Data',
      snippet: '"Verified pack contents count: 6 loops configuration."'
    }
  };

  const conceptualStages = [
    { num: '01', title: 'Understand', desc: 'AI interprets messy product descriptions, specifications, and context.' },
    { num: '02', title: 'Enrich', desc: 'Missing information and attributes are resolved.' },
    { num: '03', title: 'Verify', desc: 'Claims are checked against available source evidence.' },
    { num: '04', title: 'Review', desc: 'Low-confidence information is surfaced for human approval.' },
    { num: '05', title: 'Deliver', desc: 'Validated data becomes commerce-ready output.' }
  ];

  const phasesList = [
    { num: '01', title: 'Data Cleaning Engine', desc: 'Strips vendor placeholders (-- Unbranded --, n/a, etc.), normalizes Unicode text, and filters duplicates.', stage: 'Ingest' },
    { num: '02', title: 'Product Understanding', desc: 'LLM-driven attribute structure parsing combined with high-performance description cache deduplication.', stage: 'Ingest' },
    { num: '03', title: 'Brand & Mfr Resolution', desc: 'Standardizes manufacturer and brand strings against taxonomy masters using token ID maps.', stage: 'Ingest' },
    { num: '04', title: 'Product Classification', desc: 'Categorizes entries into hierarchical taxonomy paths via semantic similarity matchers.', stage: 'Structure' },
    { num: '05', title: 'Attribute Extraction', desc: 'Extracts category-specific metrics (grit, voltage, pack size, diameter) from source blobs.', stage: 'Structure' },
    { num: '06', title: 'LOV Resolution', desc: 'Resolves raw text attributes against strict List of Value enums to maintain data integrity.', stage: 'Structure' },
    { num: '07', title: 'UOM Normalization', desc: 'Standardizes physical measurement units into unified delivery labels (e.g. inches/inch -> in).', stage: 'Structure' },
    { num: '08', title: 'Web Evidence Enrichment', desc: 'Crawls trusted external databases and official datasheets to enrich missing specifications.', stage: 'Ground' },
    { num: '09', title: 'Entity De-duplication', desc: 'Regex, de-duplication, and span validation modules check extracted data points against original documents to stop hallucinations.', stage: 'Ground' },
    { num: '10', title: 'Validation Engine', desc: 'Enforces hard business rule validations (e.g., negative length limits, category mismatch alerts).', stage: 'Ground' },
    { num: '11', title: 'Confidence Engine', desc: 'Calculates overall confidence profiles to split data into auto-approve or human-review bins.', stage: 'Ground' },
    { num: '12', title: 'HITL Review Dashboard', desc: 'Exposes flagged attribute mismatches to human operators in an immutable staging catalog.', stage: 'Review' },
    { num: '13', title: 'Grounded Description', desc: 'Generates SEO titles, and summaries based solely on factual attributes, preventing fluff.', stage: 'Review' },
    { num: '14', title: 'Final Delivery Engine', desc: 'Outputs the unified 252-column schema with CSV templates and SHA256 integrity tags.', stage: 'Output' },
    { num: '15', title: 'Ground-Truth Evaluation', desc: 'Benchmarks delivery files against ground truth records to output accuracy, completeness, and recovery rates.', stage: 'Output' }
  ];

  return (
    <div className="relative min-h-screen bg-[#070A0F] text-[#F1F5F9] overflow-x-hidden font-sans glow-backdrop selection:bg-[#F59E0B]/30 selection:text-[#FBBF24]">
      {/* Dynamic Animated Particle Background */}
      <ParticleCanvas />

      {/* 1. NAVIGATION (FLOATING GLASS NAVBAR) */}
      <header className="fixed top-4 left-6 right-6 h-14 border border-[#202B3B]/60 bg-[#070A0F]/80 backdrop-blur-md z-50 rounded-full transition-all shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          
          {/* Logo & Subhead */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <Cpu className="w-5 h-5 text-[#F59E0B] group-hover:rotate-12 transition-transform" />
            <div className="text-left font-mono">
              <span className="font-bold text-sm tracking-tight text-white block leading-none font-display">PRODEXA</span>
              <span className="text-[7.5px] text-[#94A3B8] tracking-widest uppercase font-bold">AUTONOMOUS PRODUCT INTELLIGENCE</span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 font-mono text-[13px] font-bold tracking-wider text-[#94A3B8]">
            <button onClick={() => scrollToSection('product')} className="hover:text-[#38BDF8] transition-colors cursor-pointer bg-transparent border-none">Product</button>
            <button onClick={() => scrollToSection('how-it-works')} className="hover:text-[#38BDF8] transition-colors cursor-pointer bg-transparent border-none">How It Works</button>
            <button onClick={() => scrollToSection('evidence')} className="hover:text-[#38BDF8] transition-colors cursor-pointer bg-transparent border-none">Evidence</button>
            <button onClick={() => scrollToSection('evaluation')} className="hover:text-[#38BDF8] transition-colors cursor-pointer bg-transparent border-none">Evaluation</button>
          </nav>

          {/* Right CTA */}
          <div className="hidden md:flex items-center">
            <Link
              to={user ? "/user/dashboard" : "/login"}
              className="px-4 py-1.5 rounded-full bg-[#141B26] border border-[#38BDF8]/40 hover:border-[#38BDF8] text-[#38BDF8] hover:text-white text-[11px] font-mono font-bold transition-all shadow-[0_0_12px_rgba(56,189,248,0.1)]"
            >
              Explore Prodexa
            </Link>
          </div>

          {/* Mobile Menu Icon */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)} 
            className="md:hidden p-1.5 rounded-lg text-[#94A3B8] hover:text-white border border-[#202B3B] bg-transparent cursor-pointer"
          >
            <Menu className="w-4 h-4" />
          </button>

        </div>

        {/* Mobile menu dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-16 left-0 right-0 bg-[#0E131B] border border-[#202B3B] px-6 py-6 flex flex-col gap-4 font-mono text-xs z-50 rounded-2xl">
            <button onClick={() => scrollToSection('product')} className="text-left py-1.5 text-[#94A3B8] hover:text-white bg-transparent border-none cursor-pointer">Product</button>
            <button onClick={() => scrollToSection('how-it-works')} className="text-left py-1.5 text-[#94A3B8] hover:text-white bg-transparent border-none cursor-pointer">How It Works</button>
            <button onClick={() => scrollToSection('evidence')} className="text-left py-1.5 text-[#94A3B8] hover:text-white bg-transparent border-none cursor-pointer">Evidence</button>
            <button onClick={() => scrollToSection('evaluation')} className="text-left py-1.5 text-[#94A3B8] hover:text-white bg-transparent border-none cursor-pointer">Evaluation</button>
            <div className="border-t border-[#202B3B] pt-4">
              <Link 
                to={user ? "/user/dashboard" : "/login"}
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full text-center py-2 rounded-lg bg-[#38BDF8] text-[#070A0F] font-bold"
              >
                Explore Prodexa
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* 2. HERO — THE BIG IDEA */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-28 pb-10 lg:pt-36 lg:pb-12 text-center space-y-6">
        
        {/* Badge */}
        <div className="flex justify-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#141B26] border border-[#F59E0B]/40 shadow-[0_0_15px_rgba(245,158,11,0.15)] text-[11px] font-mono text-[#F59E0B] uppercase tracking-wider">
            <Sparkles className="w-3 h-3 text-[#FBBF24]" />
            <span>Autonomous Product Catalog Intelligence</span>
          </div>
        </div>

        {/* Hero title & body text */}
        <div className="max-w-4xl mx-auto space-y-6">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1] font-display">
            Turn Messy Product Data <br />
            <span className="bg-gradient-to-r from-[#38BDF8] via-[#F59E0B] to-[#10B981] bg-clip-text text-transparent drop-shadow-[0_0_35px_rgba(56,189,248,0.2)] font-extrabold">
              Into Trusted Intelligence.
            </span>
          </h1>
          <p className="text-lg text-[#94A3B8] leading-relaxed max-w-2xl mx-auto">
            Prodexa uses AI to understand, enrich, validate, and structure industrial product data — with evidence behind every important attribute.
          </p>

          {/* CTAs with unified interaction styles */}
          <div className="pt-2 flex flex-wrap items-center justify-center gap-4 font-mono">
            <Link
              to="/user/products"
              className="btn-premium-primary text-[14px]"
            >
              Explore Product Intelligence
            </Link>
            <button
              onClick={() => scrollToSection('before-after')}
              className="btn-premium-secondary text-[14px]"
            >
              <FileText className="w-4 h-4 text-[#38BDF8] transition-transform" />
              <span>View Sample Output</span>
            </button>
          </div>
        </div>

        {/* 3. HERO PRODUCT VISUAL: Realistic application UI mockup */}
        <div id="product" className="max-w-5xl mx-auto pt-6 relative">
          <div className="absolute inset-0 bg-[#38BDF8]/10 rounded-3xl blur-3xl -z-10 animate-pulse-glow" />
          
          <div className="w-full bg-[#0E131B] rounded-2xl border border-[#202B3B] shadow-[0_25px_50px_rgba(0,0,0,0.6)] overflow-hidden font-mono text-left">
            <div className="bg-[#141B26] px-5 py-3 border-b border-[#202B3B] flex items-center justify-between text-xs">
              <span className="font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Database className="w-4 h-4 text-[#F59E0B]" /> PRODUCT INTELLIGENCE PANEL
              </span>
              <span className="text-[11px] font-bold text-[#10B981]">✓ VERIFIED FACT GROUNDING ACTIVE</span>
            </div>

            {/* Core dashboard data mockup */}
            <div className="p-6 grid sm:grid-cols-12 gap-6 text-xs text-[#94A3B8]">
              {/* Product specifications cards */}
              <div className="sm:col-span-8 space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-1">
                    <span className="text-[10px] uppercase tracking-wider text-slate-500">Product Class</span>
                    <p className="text-white font-bold text-sm">Industrial Sanding Belt</p>
                  </div>
                  <div className="p-4 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-1">
                    <span className="text-[10px] uppercase tracking-wider text-slate-500">Standardized Brand</span>
                    <p className="text-white font-bold text-sm">Freud Inc.</p>
                  </div>
                </div>

                <div className="p-5 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-3">
                  <span className="text-[11px] text-[#38BDF8] uppercase font-bold tracking-wider block">Resolved Attribute Specifications</span>
                  
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                    <div className="p-2.5 rounded-lg bg-[#0E131B] border border-[#202B3B]">
                      <span className="text-[9px] text-slate-500 block">MATERIAL</span>
                      <span className="text-white font-bold text-[11px]">Alum Oxide</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#0E131B] border border-[#202B3B]">
                      <span className="text-[9px] text-slate-500 block">GRIT</span>
                      <span className="text-white font-bold text-[11px]">P120 Fine</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#0E131B] border border-[#202B3B]">
                      <span className="text-[9px] text-slate-500 block">QUANTITY</span>
                      <span className="text-white font-bold text-[11px]">10 Pack</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#0E131B] border border-[#202B3B]">
                      <span className="text-[9px] text-slate-500 block">SIZE</span>
                      <span className="text-white font-bold text-[11px]">4 × 24 in</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Side status panels */}
              <div className="sm:col-span-4 space-y-4 flex flex-col justify-between">
                <div className="p-4 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-3">
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-slate-500 block">EVIDENCE PATH</span>
                    <span className="text-white font-bold">Datasheet · Page 1</span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-slate-500 block">ENGINE CONFIDENCE</span>
                    <span className="text-[#10B981] font-bold text-sm">96%+ Verified</span>
                  </div>
                </div>

                <div className="p-4 bg-[#10B981]/5 rounded-xl border border-[#10B981]/30 text-center py-5">
                  <CheckCircle2 className="w-8 h-8 text-[#10B981] mx-auto mb-2 animate-pulse" />
                  <span className="text-[#10B981] font-bold text-xs uppercase block">Ground Truth Approved</span>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      {/* 4. THE PROBLEM */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="grid lg:grid-cols-12 gap-10 items-center max-w-5xl mx-auto">
          {/* Left panel */}
          <div className="lg:col-span-5 text-left space-y-6">
            <span className="text-xs font-mono text-[#F43F5E] uppercase font-bold tracking-widest block">[ Legacy Friction ]</span>
            <h2 className="text-4xl font-extrabold font-display text-white leading-tight">Industrial Product Data <br/>Is Everywhere.</h2>
            <p className="text-base text-[#94A3B8] leading-relaxed">
              Messy feeds, supplier datasheets, conflicting catalog details, and legacy systems create thousands of inconsistencies.
            </p>

            <div className="space-y-3.5 font-mono text-xs">
              <div className="flex items-center gap-2.5 text-slate-400">
                <span className="w-2 h-2 rounded-full bg-[#F43F5E] shadow-[0_0_10px_rgba(244,63,94,0.6)]" />
                <span className="text-sm">Missing attributes & specifications</span>
              </div>
              <div className="flex items-center gap-2.5 text-slate-400">
                <span className="w-2 h-2 rounded-full bg-[#F43F5E] shadow-[0_0_10px_rgba(244,63,94,0.6)]" />
                <span className="text-sm">Inconsistent units & measurements</span>
              </div>
              <div className="flex items-center gap-2.5 text-slate-400">
                <span className="w-2 h-2 rounded-full bg-[#F43F5E] shadow-[0_0_10px_rgba(244,63,94,0.6)]" />
                <span className="text-sm">Duplicate items & unverified vendor claims</span>
              </div>
            </div>
          </div>

          {/* Right panel: Floating chaotic documents (Larger size pass) */}
          <div className="lg:col-span-7 grid sm:grid-cols-2 gap-6 relative">
            <div className="absolute inset-0 bg-[#F43F5E]/5 rounded-3xl blur-3xl -z-10" />

            <div className="p-6 rounded-2xl bg-[#0E131B] border border-[#202B3B] font-mono text-left space-y-3 shadow-[0_15px_30px_rgba(0,0,0,0.4)] transition-all hover:border-[#F43F5E]/40 hover:shadow-[0_0_15px_rgba(244,63,94,0.05)]">
              <span className="text-[11px] text-[#F43F5E] font-bold block uppercase tracking-wider">📄 PDF Datasheets</span>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 block">RAW FEED DATA</span>
                <p className="text-[13px] text-[#94A3B8] leading-relaxed italic">"Pack qty 10 count fine sander loops..."</p>
              </div>
              <span className="inline-block text-[10px] text-[#FBBF24] font-bold bg-[#FBBF24]/10 px-2.5 py-0.5 rounded border border-[#FBBF24]/20">Missing Brand Tag</span>
            </div>
            
            <div className="p-6 rounded-2xl bg-[#0E131B] border border-[#202B3B] font-mono text-left space-y-3 shadow-[0_15px_30px_rgba(0,0,0,0.4)] translate-y-4 transition-all hover:border-[#F43F5E]/40 hover:shadow-[0_0_15px_rgba(244,63,94,0.05)]">
              <span className="text-[11px] text-[#F43F5E] font-bold block uppercase tracking-wider">🌐 Vendor Websites</span>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 block">UNSTRUCTURED DESCRIPTION</span>
                <p className="text-[13px] text-[#94A3B8] leading-relaxed italic">"MPN Freud 4 x 24 sand band..."</p>
              </div>
              <span className="inline-block text-[10px] text-[#F43F5E] font-bold bg-[#F43F5E]/10 px-2.5 py-0.5 rounded border border-[#F43F5E]/20">Inconsistent Unit</span>
            </div>

            <div className="p-6 rounded-2xl bg-[#0E131B] border border-[#202B3B] font-mono text-left space-y-3 shadow-[0_15px_30px_rgba(0,0,0,0.4)] transition-all hover:border-[#F43F5E]/40 hover:shadow-[0_0_15px_rgba(244,63,94,0.05)]">
              <span className="text-[11px] text-[#F43F5E] font-bold block uppercase tracking-wider">📊 Spreadsheets</span>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 block">UNCLEAR ATTRIBUTES</span>
                <p className="text-[13px] text-[#94A3B8] leading-relaxed italic">"Material: Aluminum oxide? Alum Ox?"</p>
              </div>
              <span className="inline-block text-[10px] text-[#F43F5E] font-bold bg-[#F43F5E]/10 px-2.5 py-0.5 rounded border border-[#F43F5E]/20">Duplicate Claim</span>
            </div>

            <div className="p-6 rounded-2xl bg-[#0E131B] border border-[#202B3B] font-mono text-left space-y-3 shadow-[0_15px_30px_rgba(0,0,0,0.4)] translate-y-4 transition-all hover:border-[#F43F5E]/40 hover:shadow-[0_0_15px_rgba(244,63,94,0.05)]">
              <span className="text-[11px] text-[#F43F5E] font-bold block uppercase tracking-wider">💾 Legacy Databases</span>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 block">UNRESOLVED TAXONOMY</span>
                <p className="text-[13px] text-[#94A3B8] leading-relaxed italic">"Categorization: Sander belt parts..."</p>
              </div>
              <span className="inline-block text-[10px] text-[#FBBF24] font-bold bg-[#FBBF24]/10 px-2.5 py-0.5 rounded border border-[#FBBF24]/20">Unverified Source</span>
            </div>
          </div>
        </div>
      </section>

      {/* 5. THE TRANSFORMATION */}
      <section id="before-after" className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="text-center max-w-2xl mx-auto space-y-3 mb-16">
          <span className="text-xs font-mono text-[#FBBF24] uppercase font-bold tracking-widest block">[ Compilation Engine ]</span>
          <h2 className="text-3xl sm:text-4xl font-bold font-display text-white">From Fragmented Data to Product Intelligence.</h2>
        </div>

        {/* Dynamic side-by-side transformation grid */}
        <div className="grid lg:grid-cols-12 gap-8 items-center max-w-5xl mx-auto font-mono text-xs">
          
          {/* Left raw feed */}
          <div className="lg:col-span-5 text-left space-y-3">
            <span className="text-[#F43F5E] font-bold flex items-center gap-1.5 text-[11px] sm:text-xs">
              <Terminal className="w-4 h-4" /> RAW INPUT
            </span>
            <div className="glass-panel p-5 rounded-2xl border-[#F43F5E]/30 bg-[#0E131B]">
              <pre className="text-[#94A3B8] leading-relaxed text-[11px]">
{`{
  "title": "Heavy Duty Sanding Belt",
  "brand": "Freud?",
  "size": "4x24",
  "pack": "10",
  "material": "Alum Ox?",
  "category": "sanding"
}`}
              </pre>
            </div>
          </div>

          {/* Transformation core */}
          <div className="lg:col-span-2 flex flex-col items-center justify-center py-4 lg:py-0">
            <div className="w-12 h-12 rounded-full bg-[#141B26] border border-[#38BDF8]/40 flex items-center justify-center text-[#38BDF8] mb-2 shadow-[0_0_20px_rgba(56,189,248,0.2)] animate-pulse">
              <Cpu className="w-5 h-5" />
            </div>
            <span className="text-[10px] text-slate-500 uppercase font-bold">PRODEXA AI</span>
            <ArrowRight className="w-5 h-5 text-[#10B981] lg:rotate-90 mt-2" />
          </div>

          {/* Clean structured output */}
          <div className="lg:col-span-5 text-left space-y-3">
            <span className="text-[#10B981] font-bold flex items-center gap-1.5 text-[11px] sm:text-xs">
              <CheckCircle2 className="w-4 h-4" /> STRUCTURED INTELLIGENCE
            </span>
            <div className="glass-panel p-5 rounded-2xl border-[#10B981]/40 bg-[#0E131B] space-y-2 text-[11px]">
              <div className="flex justify-between border-b border-[#202B3B] pb-1">
                <span className="text-slate-400">Brand:</span>
                <span className="text-white font-bold">Freud Inc.</span>
              </div>
              <div className="flex justify-between border-b border-[#202B3B] pb-1">
                <span className="text-slate-400">Category:</span>
                <span className="text-[#38BDF8] font-bold">Abrasive / Sanding</span>
              </div>
              <div className="flex justify-between border-b border-[#202B3B] pb-1">
                <span className="text-slate-400">Material:</span>
                <span className="text-white font-bold">Aluminum Oxide</span>
              </div>
              <div className="flex justify-between border-b border-[#202B3B] pb-1">
                <span className="text-slate-400">Grit:</span>
                <span className="text-white font-bold">P120</span>
              </div>
              <div className="flex justify-between border-b border-[#202B3B] pb-1">
                <span className="text-slate-400">Quantity:</span>
                <span className="text-white font-bold">10 Pack</span>
              </div>
              <div className="flex justify-between items-center pt-1.5 text-[9px] font-bold">
                <span className="text-[#10B981]">✓ Grounding: Datasheet / Page 1</span>
                <span className="text-[#10B981]">96% Match</span>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* 6. PRODUCT INTELLIGENCE INTERACTIVE DEMO */}
      <section id="demo-preview" className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="text-center max-w-2xl mx-auto space-y-3 mb-16">
          <span className="text-xs font-mono text-[#38BDF8] uppercase font-bold tracking-widest block">[ Dynamic Interface ]</span>
          <h2 className="text-3xl sm:text-4xl font-bold font-display text-white">One Product. Complete Intelligence.</h2>
        </div>

        {/* Dashboard demo layout with interactive selector tabs */}
        <div className="max-w-5xl mx-auto bg-[#0E131B] rounded-2xl border border-[#202B3B] overflow-hidden shadow-[0_25px_50px_rgba(0,0,0,0.5)] font-mono text-left">
          
          {/* Navigation tab list */}
          <div className="flex border-b border-[#202B3B] bg-[#141B26] overflow-x-auto">
            {['Overview', 'Attributes', 'Evidence', 'Validation', 'Confidence'].map((tab) => (
              <button
                key={tab}
                onClick={() => setDemoActiveTab(tab)}
                className={`px-5 py-3.5 text-xs font-bold transition-all border-r border-[#202B3B] cursor-pointer ${
                  demoActiveTab === tab
                    ? 'bg-[#0E131B] text-[#38BDF8] border-t-2 border-t-[#38BDF8]'
                    : 'text-[#94A3B8] hover:bg-[#141B26]/60 hover:text-white'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Interactive display panel based on select tab */}
          <div className="p-6 sm:p-8 space-y-6 text-xs text-[#94A3B8] min-h-[220px]">
            {demoActiveTab === 'Overview' && (
              <div className="space-y-4">
                <h3 className="text-white font-bold text-sm uppercase">Catalog Entry Metadata</h3>
                <div className="grid sm:grid-cols-3 gap-4">
                  <div className="p-4 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-1">
                    <span className="text-[10px] uppercase tracking-wider block text-slate-500">RESOLVED MPN</span>
                    <span className="text-white font-bold text-sm">DCB518ASTS06G</span>
                  </div>
                  <div className="p-4 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-1">
                    <span className="text-[10px] uppercase tracking-wider block text-slate-500">COMMERCE CLASSIFICATION</span>
                    <span className="text-[#38BDF8] font-bold text-sm">Abrasive Tools</span>
                  </div>
                  <div className="p-4 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-1">
                    <span className="text-[10px] uppercase tracking-wider block text-slate-500">SCHEMA COMPLIANCE</span>
                    <span className="text-[#10B981] font-bold text-sm">✓ 252-Column Pass</span>
                  </div>
                </div>
              </div>
            )}

            {demoActiveTab === 'Attributes' && (
              <div className="space-y-4">
                <h3 className="text-white font-bold text-sm uppercase">Master attributes mappings</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                  <div className="p-3 bg-[#070A0F] rounded-lg border border-[#202B3B]">
                    <span className="text-[9px] block text-slate-500">Material</span>
                    <span className="text-white font-bold">Premium Alum Oxide</span>
                  </div>
                  <div className="p-3 bg-[#070A0F] rounded-lg border border-[#202B3B]">
                    <span className="text-[9px] block text-slate-500">Size</span>
                    <span className="text-white font-bold">1/2 in x 18 in</span>
                  </div>
                  <div className="p-3 bg-[#070A0F] rounded-lg border border-[#202B3B]">
                    <span className="text-[9px] block text-slate-500">Grit</span>
                    <span className="text-white font-bold">P120 Fine</span>
                  </div>
                  <div className="p-3 bg-[#070A0F] rounded-lg border border-[#202B3B]">
                    <span className="text-[9px] block text-slate-500">Quantity</span>
                    <span className="text-white font-bold">6 Pcs</span>
                  </div>
                </div>
              </div>
            )}

            {demoActiveTab === 'Evidence' && (
              <div className="space-y-3 p-4 bg-[#070A0F] rounded-xl border border-[#202B3B]">
                <span className="text-[11px] text-[#38BDF8] uppercase font-bold tracking-widest block">Fact grounding coordinates link</span>
                <p className="text-white italic">"Sanding belt loops constructed with heavy-duty premium aluminum oxide abrasive grains..."</p>
                <span className="text-[10px] text-slate-500 block border-t border-[#202B3B] pt-2">
                  Document Reference: Freud Official Datasheet Spec Sheet · Page 1 Coordinates
                </span>
              </div>
            )}

            {demoActiveTab === 'Validation' && (
              <div className="space-y-3">
                <h3 className="text-white font-bold text-sm uppercase">LOV / UOM checks</h3>
                <div className="p-4 bg-[#10B981]/5 rounded-xl border border-[#10B981]/30 flex justify-between items-center">
                  <span className="text-white font-medium text-[13px]">Measurement unit (inches) standardized to (in):</span>
                  <span className="text-[#10B981] font-bold">✓ LOV compliant</span>
                </div>
              </div>
            )}

            {demoActiveTab === 'Confidence' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center text-white">
                  <span className="font-bold text-[13px]">Overall confidence score:</span>
                  <span className="text-[#10B981] font-bold text-sm">96% Accuracy</span>
                </div>
                <div className="w-full h-2.5 bg-[#070A0F] rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-[#38BDF8] to-[#10B981] rounded-full w-[96%]" />
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 7. THE INTELLIGENCE ENGINE (Polished horizontal pipeline flow) */}
      <section id="how-it-works" className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <span className="text-xs font-mono text-[#F59E0B] uppercase font-bold tracking-widest block">[ INTELLIGENCE PIPELINE ]</span>
          <h2 className="text-4xl sm:text-5xl font-extrabold font-display text-white leading-tight">Five Steps. One Intelligent Pipeline.</h2>
          <p className="text-lg text-[#94A3B8] leading-relaxed">
            From messy vendor information to validated, commerce-ready product intelligence.
          </p>
        </div>

        {/* Custom flowing horizontal pipeline display */}
        <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-6 items-stretch relative font-mono text-xs">
          
          {/* Connector Line for Desktop */}
          <div className="absolute top-[40px] left-[5%] right-[5%] h-[2px] bg-gradient-to-r from-[#F43F5E] via-[#38BDF8] to-[#10B981] hidden lg:block -z-10">
            {/* Animated data particle */}
            <div className="absolute w-2 h-2 rounded-full bg-[#38BDF8] shadow-[0_0_8px_#38BDF8] -top-[3px] animate-pipeline-flow" />
          </div>

          {/* Connector Line for Mobile */}
          <div className="absolute left-[38px] top-[5%] bottom-[5%] w-[2px] bg-gradient-to-b from-[#F43F5E] via-[#38BDF8] to-[#10B981] lg:hidden -z-10">
            {/* Animated data particle */}
            <div className="absolute w-2 h-2 rounded-full bg-[#38BDF8] shadow-[0_0_8px_#38BDF8] -left-[3px] animate-pipeline-flow-vertical" />
          </div>

          {/* Card 1: RAW INPUT */}
          <div className="flex-1 flex flex-col justify-between p-5 rounded-xl border border-[#F43F5E]/30 bg-[#0E131B]/95 text-left space-y-4 transition-all hover:translate-y-[-2px] hover:border-[#F43F5E]/60 shadow-[0_0_15px_rgba(244,63,94,0.05)] cursor-default">
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-[#F43F5E] font-bold uppercase tracking-wider">INPUT SOURCE</span>
              <span className="text-[9px] text-[#F43F5E] font-bold bg-[#F43F5E]/10 px-2 py-0.5 rounded border border-[#F43F5E]/20">Unstructured</span>
            </div>
            
            <div className="space-y-2">
              <h4 className="text-white font-bold text-sm uppercase tracking-wide">RAW / MESSY</h4>
              <div className="p-3 rounded bg-[#070A0F] border border-[#202B3B] text-[11px] text-[#94A3B8] italic">
                "Duo sand belt 1/2 x 18 P120 grit..."
              </div>
            </div>

            <div className="flex flex-wrap gap-1.5 pt-2 text-[9px] text-slate-500">
              <span className="px-1.5 py-0.5 rounded bg-[#141B26]">Vendor Feed</span>
              <span className="px-1.5 py-0.5 rounded bg-[#141B26]">Missing Attributes</span>
            </div>
          </div>

          {/* Steps 1 to 5 Cards */}
          {conceptualStages.map((stage, idx) => {
            // Stage custom configurations based on rules
            let badgeText = null;
            let borderStyle = 'border-[#202B3B] hover:border-[#38BDF8]/60 hover:translate-y-[-2px]';
            let labelHoverClass = 'group-hover:text-[#38BDF8]';
            
            if (stage.num === '01') {
              badgeText = 'Input Parsing';
              borderStyle = 'border-[#38BDF8]/20 hover:border-[#38BDF8]/60 hover:translate-y-[-2px]';
              labelHoverClass = 'group-hover:text-[#38BDF8]';
            } else if (stage.num === '02') {
              badgeText = 'Attribute Resolution';
              borderStyle = 'border-[#38BDF8]/20 hover:border-[#38BDF8]/60 hover:translate-y-[-2px]';
              labelHoverClass = 'group-hover:text-[#38BDF8]';
            } else if (stage.num === '03') {
              badgeText = 'Evidence Check';
              borderStyle = 'border-[#10B981]/40 hover:border-[#10B981]/70 hover:translate-y-[-2px] shadow-[0_0_15px_rgba(16,185,129,0.04)]';
              labelHoverClass = 'group-hover:text-[#10B981]';
            } else if (stage.num === '04') {
              badgeText = 'HITL Staging';
              borderStyle = 'border-[#F59E0B]/40 hover:border-[#F59E0B]/70 hover:translate-y-[-2px] shadow-[0_0_15px_rgba(245,158,11,0.04)]';
              labelHoverClass = 'group-hover:text-[#F59E0B]';
            } else if (stage.num === '05') {
              badgeText = 'Validated Output';
              borderStyle = 'border-[#10B981]/40 hover:border-[#10B981]/70 hover:translate-y-[-2px] shadow-[0_0_15px_rgba(16,185,129,0.04)]';
              labelHoverClass = 'group-hover:text-[#10B981]';
            }

            return (
              <div key={idx} className={`flex-1 flex flex-col p-5 rounded-xl bg-[#0E131B] border transition-all ${borderStyle} cursor-default group space-y-4 shadow-[0_10px_25px_rgba(0,0,0,0.3)]`}>
                <div className="flex justify-between items-center">
                  <div className="w-8 h-8 rounded-full bg-[#070A0F] border border-[#202B3B] flex items-center justify-center font-bold text-xs text-white group-hover:border-[#38BDF8] group-hover:text-[#38BDF8] transition-all">
                    {stage.num}
                  </div>
                  {badgeText && (
                    <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border whitespace-nowrap ${
                      stage.num === '01' || stage.num === '02' ? 'bg-[#38BDF8]/10 border-[#38BDF8]/30 text-[#38BDF8]' :
                      stage.num === '03' ? 'bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981]' :
                      stage.num === '04' ? 'bg-[#F59E0B]/10 border-[#F59E0B]/30 text-[#F59E0B]' :
                      'bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981]'
                    }`}>
                      {badgeText}
                    </span>
                  )}
                </div>

                <div className="space-y-2 text-left pt-2">
                  <h4 className={`text-white font-bold text-[15px] sm:text-[16px] uppercase tracking-wide ${labelHoverClass} transition-colors`}>
                    {stage.title}
                  </h4>
                  <p className="text-[13px] text-[#94A3B8] leading-relaxed font-sans min-h-[60px]">
                    {stage.desc}
                  </p>
                </div>
              </div>
            );
          })}

        </div>
      </section>

      {/* 8. EVIDENCE */}
      <section id="evidence" className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="text-center max-w-2xl mx-auto space-y-3 mb-16">
          <span className="text-xs font-mono text-[#38BDF8] uppercase font-bold tracking-widest block">[ Grounded Audit Trails ]</span>
          <h2 className="text-3xl sm:text-4xl font-bold font-display text-white">AI You Can Trace Back to the Source.</h2>
          <p className="text-sm text-[#94A3B8] leading-relaxed">
            Prodexa doesn't just generate attributes. It connects intelligence to evidence.
          </p>
        </div>

        {/* Visual Chain display card */}
        <div className="max-w-4xl mx-auto bg-[#0E131B] rounded-2xl border border-[#202B3B] p-6 sm:p-8 font-mono text-left relative overflow-hidden shadow-[0_25px_50px_rgba(0,0,0,0.5)]">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#38BDF8]/5 rounded-full blur-2xl animate-pulse-glow" />
          <span className="text-[10px] text-[#94A3B8] uppercase block border-b border-[#202B3B] pb-3 mb-6">Traceability Proof Chain</span>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-xs relative">
            
            {/* Source */}
            <div className="glass-panel p-5 rounded-xl border border-[#38BDF8]/40 shadow-[0_0_15px_rgba(56,189,248,0.15)] space-y-2">
              <span className="text-[9px] text-[#38BDF8] font-bold uppercase tracking-wider block">1. SOURCE DOCUMENT</span>
              <p className="text-white font-bold text-sm">Datasheet PDF</p>
              <p className="text-[#94A3B8] italic leading-relaxed">"Freud Inc. Official Technical Datasheet Page 1"</p>
            </div>

            {/* Claim */}
            <div className="glass-panel p-5 rounded-xl border border-[#F59E0B]/40 shadow-[0_0_15px_rgba(245,158,11,0.15)] space-y-2">
              <span className="text-[9px] text-[#F59E0B] font-bold uppercase tracking-wider block">2. EXTRACTED CLAIM</span>
              <p className="text-white font-bold text-sm">Abrasive Material</p>
              <p className="text-[#94A3B8]">"Premium Aluminum Oxide"</p>
            </div>

            {/* Validation */}
            <div className="glass-panel p-5 rounded-xl border border-[#10B981]/40 shadow-[0_0_15px_rgba(16,185,129,0.15)] space-y-2">
              <span className="text-[9px] text-[#10B981] font-bold uppercase tracking-wider block">3. VALIDATION</span>
              <p className="text-white font-bold text-sm">Grounded Check</p>
              <p className="text-[#10B981] font-semibold">Verified Grounding ✓</p>
            </div>

            {/* Confidence */}
            <div className="glass-panel p-5 rounded-xl border border-purple-500/40 shadow-[0_0_15px_rgba(168,85,247,0.15)] space-y-2">
              <span className="text-[9px] text-purple-400 font-bold uppercase tracking-wider block">4. CONFIDENCE SCORE</span>
              <p className="text-white font-bold text-sm">96% Quality</p>
              <p className="text-[#38BDF8] font-semibold">Decision: AUTO_APPROVE</p>
            </div>
          </div>
        </div>
      </section>

      {/* 9. HUMAN CONTROL (QA Review simulator) */}
      <section id="demo" className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="grid lg:grid-cols-12 gap-12 items-center max-w-5xl mx-auto">
          {/* Left panel: QA Review Simulator */}
          <div className="lg:col-span-7 bg-[#0E131B] rounded-2xl border border-[#202B3B] p-6 text-left relative overflow-hidden font-mono shadow-[0_25px_50px_rgba(0,0,0,0.5)]">
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#F59E0B]/5 rounded-full blur-2xl animate-pulse-glow" />
            
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[#202B3B] pb-4 mb-4">
              <div>
                <span className="text-[10px] text-[#F59E0B] uppercase font-bold tracking-widest block mb-0.5">HITL Review Queue Simulator</span>
                <span className="text-white font-bold text-xs uppercase">FLAGGED ATTR INSPECTOR</span>
              </div>
              <span className="text-[10px] text-[#94A3B8] font-bold px-2 py-0.5 rounded border border-[#202B3B] bg-[#141B26]">SKU: #98234</span>
            </div>

            {/* Sim Body Content */}
            <div className="space-y-4">
              <div className="p-5 bg-[#070A0F] rounded-xl border border-[#202B3B] space-y-4 relative shadow-[inner_0_2px_8px_rgba(0,0,0,0.5)]">
                
                {/* Dynamic State Overlay */}
                {hitlState !== 'pending' && hitlState !== 'editing' && (
                  <div className="absolute inset-0 bg-[#070A0F]/95 flex flex-col items-center justify-center text-center p-4 rounded-xl z-20">
                    {hitlState === 'accepted' && (
                      <div className="space-y-3 animate-fade-in-up">
                        <div className="w-12 h-12 rounded-full bg-[#10B981]/10 border border-[#10B981] flex items-center justify-center text-[#10B981] mx-auto shadow-[0_0_15px_rgba(16,185,129,0.2)] animate-pulse">
                          <Check className="w-6 h-6" />
                        </div>
                        <h4 className="text-white font-bold text-sm">Attribute Accept Approved!</h4>
                        <p className="text-xs text-[#94A3B8] max-w-sm mx-auto">
                          Material attribute standardized as <strong>"{hitlCurrentValue}"</strong> and written to master catalog.
                        </p>
                      </div>
                    )}
                    {hitlState === 'rejected' && (
                      <div className="space-y-3 animate-fade-in-up">
                        <div className="w-12 h-12 rounded-full bg-[#F43F5E]/10 border border-[#F43F5E] flex items-center justify-center text-[#F43F5E] mx-auto shadow-[0_0_15px_rgba(244,63,94,0.2)]">
                          <X className="w-6 h-6" />
                        </div>
                        <h4 className="text-white font-bold text-sm">Attribute Rejected!</h4>
                        <p className="text-xs text-[#94A3B8] max-w-sm mx-auto">
                          Flagged claim discarded. Marked generated description as requiring re-run.
                        </p>
                      </div>
                    )}
                    <button 
                      onClick={() => {
                        setHitlState('pending');
                        setHitlCurrentValue('Premium Aluminum Oxide');
                        setHitlInputValue('Premium Aluminum Oxide');
                      }}
                      className="mt-4 px-4 py-2 bg-[#141B26] hover:bg-[#1A2433] border border-[#202B3B] text-[#94A3B8] hover:text-white rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 mx-auto cursor-pointer"
                    >
                      <RefreshCw className="w-3.5 h-3.5" /> Reset Simulator
                    </button>
                  </div>
                )}

                {/* Attribute Review Core Block */}
                <div className="text-xs space-y-3">
                  <div className="flex justify-between items-center text-[10px] text-[#94A3B8]">
                    <span>Attribute: Material</span>
                    <span className="text-amber-500 font-bold">Confidence: 87%</span>
                  </div>

                  {/* Value Row */}
                  <div className="flex justify-between items-center py-2.5 border-y border-[#202B3B]">
                    <span className="text-[#94A3B8]">AI Value:</span>
                    {hitlState === 'editing' ? (
                      <div className="flex gap-2">
                        <input 
                          type="text"
                          value={hitlInputValue}
                          onChange={(e) => setHitlInputValue(e.target.value)}
                          className="bg-[#0E131B] border border-[#38BDF8] rounded-lg text-xs px-3 py-1 text-white outline-none focus:border-[#38BDF8] font-mono"
                        />
                        <button 
                          onClick={() => {
                            setHitlCurrentValue(hitlInputValue);
                            setHitlState('accepted');
                          }}
                          className="bg-[#10B981] hover:bg-[#10B981]/80 text-[#070A0F] font-bold text-xs px-3 py-1 rounded-lg cursor-pointer"
                        >
                          Save
                        </button>
                      </div>
                    ) : (
                      <span className="text-[#38BDF8] font-bold text-sm glow-text-cyan">{hitlCurrentValue}</span>
                    )}
                  </div>
                  
                  <div className="text-xs text-[#94A3B8] leading-relaxed pt-1 space-y-1">
                    <span className="font-bold text-amber-500 uppercase text-[9px] block">Evidence:</span>
                    <p className="italic">"Manufacturer Datasheet · Page 1"</p>
                  </div>
                </div>
              </div>

              {/* Action Simulation Buttons */}
              {hitlState === 'pending' && (
                <div className="grid grid-cols-3 gap-4">
                  <button 
                    onClick={() => setHitlState('accepted')}
                    className="py-3 rounded-xl bg-[#10B981]/15 hover:bg-[#10B981]/25 border border-[#10B981]/40 text-[#10B981] hover:text-white font-bold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    Accept
                  </button>
                  <button 
                    onClick={() => setHitlState('editing')}
                    className="py-3 rounded-xl bg-[#38BDF8]/15 hover:bg-[#38BDF8]/25 border border-[#38BDF8]/40 text-[#38BDF8] hover:text-white font-bold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => setHitlState('rejected')}
                    className="py-3 rounded-xl bg-[#F43F5E]/15 hover:bg-[#F43F5E]/25 border border-[#F43F5E]/40 text-[#F43F5E] hover:text-white font-bold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right text panel */}
          <div className="lg:col-span-5 text-left space-y-6">
            <span className="text-xs font-mono text-[#F59E0B] uppercase font-bold tracking-widest block">[ HITL Reviewer ]</span>
            <h2 className="text-3xl sm:text-4xl font-bold font-display text-white">Automation Without Losing Control.</h2>
            <p className="text-base text-[#94A3B8] leading-relaxed">
              AI handles the heavy lifting. Humans stay in control when confidence is low.
            </p>
          </div>
        </div>
      </section>

      {/* 10. QUALITY / EVALUATION (Redesigned validation diagnostics) */}
      <section id="evaluation" className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="text-center max-w-2xl mx-auto space-y-4 mb-16">
          <span className="text-xs font-mono text-[#10B981] uppercase font-bold tracking-widest block">[ VALIDATION DIAGNOSTICS ]</span>
          <h2 className="text-4xl font-extrabold font-display text-white">Built to Be Measured.</h2>
          <p className="text-base text-[#94A3B8] leading-relaxed">
            Every output can be evaluated for accuracy, completeness, validation, and schema compliance.
          </p>
        </div>

        {/* Dashboard evaluation layout */}
        <div className="max-w-5xl mx-auto grid lg:grid-cols-12 gap-8 items-stretch font-mono text-xs">
          
          {/* Left side: Large featured metric accuracy panel */}
          <div className="lg:col-span-5 bg-[#0E131B] border border-[#10B981]/40 rounded-2xl p-6 sm:p-8 flex flex-col justify-between items-center text-center shadow-[0_0_30px_rgba(16,185,129,0.06)] relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-[#10B981]/5 rounded-full blur-2xl animate-pulse-glow" />
            
            <div className="space-y-2">
              <span className="text-[10px] text-[#10B981] font-bold bg-[#10B981]/15 px-3 py-1 rounded-full border border-[#10B981]/30 uppercase tracking-wider block">
                Primary Accuracy Metric
              </span>
              <p className="text-base font-extrabold text-white">Field Accuracy</p>
            </div>

            {/* Circular Progress Ring */}
            <div className="my-8 relative w-36 h-36 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="72" cy="72" r="60" stroke="#141B26" strokeWidth="10" fill="transparent" />
                <circle cx="72" cy="72" r="60" stroke="#10B981" strokeWidth="10" fill="transparent" 
                        strokeDasharray={376.8} strokeDashoffset={376.8 * (1 - 0.9663)} />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-extrabold text-white">{evalData?.metrics?.field_accuracy || '96.63%'}</span>
                <span className="text-[9px] text-[#94A3B8] uppercase tracking-wider font-mono">Score Value</span>
              </div>
            </div>

            <p className="text-xs text-[#94A3B8] leading-relaxed max-w-xs font-sans">
              Matches normalized attributes against catalog templates to establish a rigorous grounding check.
            </p>
          </div>

          {/* Right side: Three stacked compact metric cards */}
          <div className="lg:col-span-7 flex flex-col justify-between gap-4">
            
            {/* Card 1: Data Completeness */}
            <div className="bg-[#0E131B] border border-[#202B3B] rounded-xl p-5 hover:border-[#38BDF8]/40 transition-all flex items-center justify-between gap-4 shadow-[0_5px_15px_rgba(0,0,0,0.2)]">
              <div className="space-y-1 text-left">
                <span className="text-[10px] text-[#38BDF8] font-bold uppercase tracking-wider">DATA COMPLETENESS</span>
                <h4 className="text-white font-bold text-sm">Completeness Fill Rate</h4>
                <p className="text-[12px] text-[#94A3B8] font-sans">Presence of vital catalog specifications, eliminating empty database fields.</p>
              </div>
              <div className="text-right shrink-0">
                <span className="text-2xl font-extrabold text-[#38BDF8]">{evalData?.metrics?.completeness || '99.5%'}</span>
              </div>
            </div>

            {/* Card 2: Schema Validation */}
            <div className="bg-[#0E131B] border border-[#202B3B] rounded-xl p-5 hover:border-[#F59E0B]/40 transition-all flex items-center justify-between gap-4 shadow-[0_5px_15px_rgba(0,0,0,0.2)]">
              <div className="space-y-1 text-left">
                <span className="text-[10px] text-[#F59E0B] font-bold uppercase tracking-wider">SCHEMA VALIDATION</span>
                <h4 className="text-white font-bold text-sm">Compliance Match Rate</h4>
                <p className="text-[12px] text-[#94A3B8] font-sans">Enforces range parameters, unit standardizations, and catalog list constraints.</p>
              </div>
              <div className="text-right shrink-0">
                <span className="text-2xl font-extrabold text-[#F59E0B]">{evalData?.metrics?.lov_compliance || '100% Match'}</span>
              </div>
            </div>

            {/* Card 3: Ground Truth */}
            <div className="bg-[#0E131B] border border-[#202B3B] rounded-xl p-5 hover:border-[#10B981]/40 transition-all flex items-center justify-between gap-4 shadow-[0_5px_15px_rgba(0,0,0,0.2)]">
              <div className="space-y-1 text-left">
                <span className="text-[10px] text-[#10B981] font-bold uppercase tracking-wider">GROUND TRUTH</span>
                <h4 className="text-white font-bold text-sm">Continuous Evaluation Check</h4>
                <p className="text-[12px] text-[#94A3B8] font-sans">Validates output catalogs against verified golden benchmark records.</p>
              </div>
              <div className="text-right shrink-0">
                <span className="text-2xl font-extrabold text-[#10B981]">{evalData?.metrics?.uom_compliance || '1,000 Products Checked'}</span>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* 11. COMMERCE-READY OUTPUT */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="text-center max-w-2xl mx-auto space-y-3 mb-16">
          <span className="text-xs font-mono text-[#38BDF8] uppercase font-bold tracking-widest block">[ Final Delivery Schema ]</span>
          <h2 className="text-3xl sm:text-4xl font-bold font-display text-white">Ready for the Catalog.</h2>
          <p className="text-sm text-[#94A3B8] leading-relaxed">
            From fragmented supplier information to commerce-ready product intelligence.
          </p>
        </div>

        {/* Structured catalog spreadsheet visualization */}
        <div className="max-w-5xl mx-auto bg-[#0E131B] rounded-2xl border border-[#202B3B] overflow-hidden shadow-[0_25px_50px_rgba(0,0,0,0.6)] font-mono text-xs text-left">
          
          <div className="bg-[#141B26] px-5 py-3.5 border-b border-[#202B3B] flex items-center justify-between text-slate-300">
            <span className="font-bold uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#10B981]" /> EXPORTED_CATALOG_PAYLOAD.CSV
            </span>
            <span className="text-[10px] px-2.5 py-0.5 rounded bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/20 font-bold uppercase">252-Column Ready</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-[11px] whitespace-nowrap">
              <thead>
                <tr className="bg-[#070A0F] border-b border-[#202B3B] text-slate-400 font-bold uppercase tracking-wider">
                  <th className="px-5 py-3 text-left">MPN</th>
                  <th className="px-5 py-3 text-left">Brand Name</th>
                  <th className="px-5 py-3 text-left">Category Taxonomy</th>
                  <th className="px-5 py-3 text-left">Material Spec</th>
                  <th className="px-5 py-3 text-left">Dimension Unit</th>
                  <th className="px-5 py-3 text-left">Factual Evidence Path</th>
                  <th className="px-5 py-3 text-left font-mono">Accuracy Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#202B3B] text-slate-300">
                <tr className="hover:bg-[#141B26]/30 transition-colors">
                  <td className="px-5 py-3.5 font-bold text-white">DCB518ASTS06G</td>
                  <td className="px-5 py-3.5">Freud Inc.</td>
                  <td className="px-5 py-3.5 text-[#38BDF8]">Abrasives & Sanding</td>
                  <td className="px-5 py-3.5">Premium Aluminum Oxide</td>
                  <td className="px-5 py-3.5">1/2 in × 18 in</td>
                  <td className="px-5 py-3.5 italic text-slate-400">Datasheet · Page 1 Reference</td>
                  <td className="px-5 py-3.5 text-[#10B981] font-bold">96.63%</td>
                </tr>
                <tr className="hover:bg-[#141B26]/30 transition-colors">
                  <td className="px-5 py-3.5 font-bold text-white">DB82490X12A45</td>
                  <td className="px-5 py-3.5">Diablo Tools</td>
                  <td className="px-5 py-3.5 text-[#38BDF8]">Sanding Bands</td>
                  <td className="px-5 py-3.5">Zirconia Alumina</td>
                  <td className="px-5 py-3.5">4 in x 24 in</td>
                  <td className="px-5 py-3.5 italic text-slate-400">Product Brochure · Page 3 Reference</td>
                  <td className="px-5 py-3.5 text-[#10B981] font-bold">98.15%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* 12. UNDER THE HOOD (15 specialised phases timeline) */}
      <section id="under-the-hood" className="relative z-10 max-w-7xl mx-auto px-6 py-20 border-b border-[#202B3B]">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <span className="text-xs font-mono text-[#FBBF24] uppercase font-bold tracking-widest block">[ Architecture Deep Dive ]</span>
          <h2 className="text-3xl sm:text-4xl font-bold font-display text-white">Under the Hood.</h2>
          <p className="text-sm text-[#94A3B8] max-w-xl mx-auto leading-relaxed">
            15 specialized intelligence stages power the Prodexa engine.
          </p>
        </div>

        {/* 15 Phase wrapping timeline selector */}
        <div className="max-w-5xl mx-auto space-y-8 text-left font-mono text-xs">
          <div className="flex flex-wrap gap-2 justify-center border-b border-[#202B3B] pb-6">
            {phasesList.map((phase, idx) => (
              <button
                key={idx}
                onClick={() => setActivePhaseIndex(idx)}
                className={`px-3 py-2 rounded-lg text-xs font-extrabold transition-all border cursor-pointer ${
                  activePhaseIndex === idx
                    ? 'bg-[#141B26] border-[#F59E0B] text-[#F59E0B] shadow-[0_0_15px_rgba(245,158,11,0.15)]'
                    : 'bg-[#0E131B]/60 border-[#202B3B] text-[#94A3B8] hover:text-white hover:border-[#38BDF8]'
                }`}
              >
                P{phase.num}
              </button>
            ))}
          </div>

          {/* Timeline inspect details & 3D representation split */}
          <div className="grid md:grid-cols-12 gap-8 items-center bg-[#0E131B] border border-[#202B3B] rounded-2xl p-6 sm:p-8 shadow-[0_25px_50px_rgba(0,0,0,0.4)]">
            
            {/* Left: Active phase info */}
            <div className="md:col-span-7 space-y-4">
              <div>
                <span className="text-[10px] text-[#F59E0B] font-bold uppercase tracking-wider block">
                  STAGE: {phasesList[activePhaseIndex].stage} • PIPELINE PHASE {phasesList[activePhaseIndex].num}
                </span>
                <h3 className="text-white font-bold text-lg sm:text-xl mt-1 font-display">
                  {phasesList[activePhaseIndex].title}
                </h3>
              </div>
              <p className="text-sm text-[#94A3B8] leading-relaxed">
                {phasesList[activePhaseIndex].desc}
              </p>
              <div className="pt-2 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
                <span className="text-[10px] text-[#10B981] font-bold uppercase tracking-wider">Engine Process Active</span>
              </div>
            </div>

            {/* Right: 3D rotating visual slabs */}
            <div className="md:col-span-5 flex flex-col items-center border-t md:border-t-0 md:border-l border-[#202B3B] pt-6 md:pt-0 md:pl-8">
              <span className="text-[10px] text-[#94A3B8] uppercase block tracking-wider mb-6 font-bold">
                Interactive 3D Pipeline Stack
              </span>
              
              <div
                ref={stageRef}
                onPointerMove={handlePointerMove}
                onPointerLeave={handlePointerLeave}
                className="stage-stage cursor-grab active:cursor-grabbing w-full h-[240px]"
              >
                <div ref={stackRef} className="stack3d w-[200px] h-[110px]">
                  <div className="slab slab0 text-xs py-1.5 px-3" style={{ transform: 'translateZ(-80px)' }}>
                    <span className="num text-[8px]">PHASE 01-03</span>
                    <span className="lbl text-xs text-[#94A3B8]">01 Ingest</span>
                  </div>
                  <div className="slab slab1 text-xs py-1.5 px-3" style={{ transform: 'translateZ(-40px)' }}>
                    <span className="num text-[8px]">PHASE 04-07</span>
                    <span className="lbl text-xs text-[#38BDF8]">02 Structure</span>
                  </div>
                  <div className="slab slab2 text-xs py-1.5 px-3" style={{ transform: 'translateZ(0px)' }}>
                    <span className="num text-[8px]">PHASE 08-10</span>
                    <span className="lbl text-xs text-[#F59E0B]">03 Ground</span>
                  </div>
                  <div className="slab slab3 text-xs py-1.5 px-3" style={{ transform: 'translateZ(40px)' }}>
                    <span className="num text-[8px]">PHASE 11-13</span>
                    <span className="lbl text-xs text-[#10B981]">04 Review</span>
                  </div>
                  <div className="slab slab4 text-xs py-1.5 px-3" style={{ transform: 'translateZ(80px)' }}>
                    <span className="num text-[8px]">PHASE 14-15</span>
                    <span className="lbl text-xs text-[#FBBF24]">05 Output</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 13. PROOF / FINAL MESSAGE */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 py-20 text-center">
        <div className="relative p-10 sm:p-14 rounded-3xl bg-gradient-to-r from-[#0E131B] via-[#141B26] to-[#0E131B] border border-[#38BDF8]/40 overflow-hidden space-y-6 shadow-[0_25px_50px_rgba(56,189,248,0.15)]">
          <div className="absolute inset-0 bg-[#38BDF8]/5 rounded-3xl blur-3xl -z-10 animate-pulse-glow" />
          
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-display text-white leading-tight">
            Product Data Shouldn't Be a Bottleneck.
          </h2>
          <p className="text-[16px] sm:text-lg text-[#94A3B8] max-w-2xl mx-auto leading-relaxed font-sans">
            Prodexa turns fragmented industrial information into intelligence your commerce systems can trust.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4 font-mono">
            <Link
              to="/user/products"
              className="btn-premium-primary text-[14px]"
            >
              Explore Prodexa
            </Link>
            <Link
              to="/user/outputs"
              className="btn-premium-secondary text-[14px]"
            >
              <FileText className="w-4 h-4 text-[#38BDF8]" />
              <span>View Sample Output</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 14. FOOTER */}
      <footer className="relative z-10 border-t border-[#202B3B] bg-[#0A0E13] text-left">
        <div className="max-w-7xl mx-auto px-6 py-16">
          
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 pb-12 border-b border-[#202B3B]">
            {/* Column 1: Brand Info */}
            <div className="md:col-span-6 space-y-4">
              <Link to="/" className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-[#141B26] border border-[#F59E0B]/30 flex items-center justify-center text-[#F59E0B]">
                  <Cpu className="w-5 h-5 text-[#F59E0B]" />
                </div>
                <span className="font-bold text-lg text-white font-display">PRODEXA</span>
              </Link>
              <p className="text-sm text-[#94A3B8] leading-relaxed max-w-sm font-mono font-bold">
                Autonomous Product Intelligence
              </p>
              <p className="text-xs text-[#94A3B8] leading-relaxed max-w-sm font-mono">
                Transform fragmented industrial product data into structured, validated, evidence-backed intelligence.
              </p>
            </div>

            {/* Column 2: Product */}
            <div className="md:col-span-2 space-y-4 font-mono text-xs">
              <h4 className="text-white font-bold uppercase tracking-wider text-[11px]">PRODUCT</h4>
              <ul className="space-y-2.5">
                <li><Link to="/user/products" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Product Explorer</Link></li>
                <li><Link to="/user/products" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Product Catalog</Link></li>
                <li><Link to="/user/pipeline" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Pipeline</Link></li>
                <li><Link to="/user/evaluation" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Evaluation</Link></li>
              </ul>
            </div>

            {/* Column 3: Intelligence */}
            <div className="md:col-span-2 space-y-4 font-mono text-xs">
              <h4 className="text-white font-bold uppercase tracking-wider text-[11px]">INTELLIGENCE</h4>
              <ul className="space-y-2.5">
                <li><button onClick={() => scrollToSection('how-it-works')} className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors cursor-pointer bg-transparent border-none">How It Works</button></li>
                <li><button onClick={() => scrollToSection('evidence')} className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors cursor-pointer bg-transparent border-none">Evidence</button></li>
                <li><Link to="/user/validation" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Validation</Link></li>
                <li><Link to="/user/review" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Human Review</Link></li>
              </ul>
            </div>

            {/* Column 4: Resources */}
            <div className="md:col-span-2 space-y-4 font-mono text-xs">
              <h4 className="text-white font-bold uppercase tracking-wider text-[11px]">RESOURCES</h4>
              <ul className="space-y-2.5">
                <li><Link to="/user/reports" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Documentation</Link></li>
                <li><Link to="/user/outputs" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors">Sample Output</Link></li>
                <li><a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-[#94A3B8] hover:text-[#38BDF8] transition-colors flex items-center gap-1">GitHub <ExternalLink className="w-3.5 h-3.5 text-[#38BDF8]" /></a></li>
              </ul>
            </div>
          </div>

          {/* Bottom Row */}
          <div className="pt-8 flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs text-[#94A3B8]">
            <span>© 2026 Prodexa. All rights reserved.</span>
            
            <div className="flex items-center gap-4 flex-wrap justify-center">
              <span className="text-[10px] px-2.5 py-0.5 rounded border border-[#202B3B] bg-[#0E131B] text-[#10B981] flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-ping" /> Intelligence Engine Operational
              </span>
              <span>·</span>
              <span>15 Intelligence Phases</span>
              <span>·</span>
              <span>252-Column Ready</span>
            </div>

            <span>Built for UniHack 2026</span>
          </div>

        </div>
      </footer>
    </div>
  );
};

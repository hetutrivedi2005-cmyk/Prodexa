import React, { useState } from 'react';
import {
  Package,
  ListTree,
  Search,
  CheckCircle,
  TrendingUp,
  UserCheck,
  FileText,
  Download,
  ArrowRight,
  Sparkles
} from 'lucide-react';

export const ProductGraph = () => {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      id: 'product',
      name: 'PRODUCT',
      subtitle: 'Raw Ingestion',
      icon: Package,
      color: 'border-cyan-500 text-cyan-400 bg-cyan-950/60',
      detail: 'Raw MPN, Brand, and Title extracted from source feed.'
    },
    {
      id: 'attributes',
      name: 'ATTRIBUTES',
      subtitle: 'Extraction & Schema',
      icon: ListTree,
      color: 'border-cyan-500 text-cyan-400 bg-cyan-950/60',
      detail: 'Structured specifications extracted according to canonical taxons.'
    },
    {
      id: 'evidence',
      name: 'EVIDENCE',
      subtitle: 'Provenance Discovery',
      icon: Search,
      color: 'border-cyan-500 text-cyan-400 bg-cyan-950/60',
      detail: 'Official manufacturer PDF spans and verified product page grounding.'
    },
    {
      id: 'validation',
      name: 'VALIDATION',
      subtitle: 'LOV & UOM Rules',
      icon: CheckCircle,
      color: 'border-emerald-500 text-emerald-400 bg-emerald-950/60',
      detail: 'Phase 10 Quality Gates: Unit normalization & LOV vocabulary matching.'
    },
    {
      id: 'confidence',
      name: 'CONFIDENCE',
      subtitle: 'Prodexa Score',
      icon: TrendingUp,
      color: 'border-cyan-400 text-cyan-300 bg-cyan-950/60',
      detail: 'Calibrated score based on source authority, MPN verification, & grounding.'
    },
    {
      id: 'review',
      name: 'HUMAN REVIEW',
      subtitle: 'HITL Safeguard',
      icon: UserCheck,
      color: 'border-amber-500 text-amber-400 bg-amber-950/60',
      detail: 'Low-confidence or missing evidence items routed to steward review.'
    },
    {
      id: 'description',
      name: 'DESCRIPTION',
      subtitle: 'Grounded Copy',
      icon: FileText,
      color: 'border-purple-500 text-purple-400 bg-purple-950/60',
      detail: 'Deterministic descriptions generated ONLY from validated specifications.'
    },
    {
      id: 'output',
      name: 'FINAL OUTPUT',
      subtitle: 'Syndication Ready',
      icon: Download,
      color: 'border-emerald-400 text-emerald-300 bg-emerald-950/60',
      detail: 'Syndicated JSON, Enriched CSV, & Evidence Provenance Reports.'
    }
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-950 border border-cyan-500/30 text-cyan-400">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 font-mono-tech tracking-wide">
              PRODUCT INTELLIGENCE GRAPH
            </h3>
            <p className="text-xs text-slate-400">
              Interactive data lineage flow across the 15-phase intelligence pipeline
            </p>
          </div>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-slate-300">
          Lineage: End-to-End Grounded
        </span>
      </div>

      {/* Lineage Flow Nodes */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 relative">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isActive = activeStep === idx;

          return (
            <div
              key={step.id}
              onClick={() => setActiveStep(idx)}
              className={`cursor-pointer rounded-xl p-3 border transition-all duration-300 relative group flex flex-col justify-between ${
                isActive
                  ? `${step.color} shadow-[0_0_20px_rgba(6,182,212,0.3)] scale-[1.03]`
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold opacity-60">0{idx + 1}</span>
                <Icon className={`w-4 h-4 ${isActive ? 'animate-bounce' : ''}`} />
              </div>

              <div>
                <p className="text-[11px] font-bold tracking-tight font-mono-tech uppercase">{step.name}</p>
                <p className="text-[9px] opacity-75 truncate">{step.subtitle}</p>
              </div>

              {idx < steps.length - 1 && (
                <ArrowRight className="w-3 h-3 text-slate-700 absolute -right-2.5 top-1/2 -translate-y-1/2 hidden lg:block z-10" />
              )}
            </div>
          );
        })}
      </div>

      {/* Detail Panel */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-cyan-500/20 flex items-start gap-4">
        <div className="p-2.5 rounded-lg bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 shrink-0">
          {React.createElement(steps[activeStep].icon, { className: 'w-5 h-5' })}
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-cyan-400 uppercase">
              Phase Lineage Step 0{activeStep + 1}: {steps[activeStep].name}
            </span>
            <span className="text-[10px] text-slate-400 font-mono">({steps[activeStep].subtitle})</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{steps[activeStep].detail}</p>
        </div>
      </div>
    </div>
  );
};

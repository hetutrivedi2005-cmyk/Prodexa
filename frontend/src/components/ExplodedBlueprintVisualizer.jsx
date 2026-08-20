import React, { useState } from 'react';
import { Layers, SearchCheck, CheckCircle2, Sliders, ChevronRight } from 'lucide-react';

export const ExplodedBlueprintVisualizer = () => {
  const [explosionFactor, setExplosionFactor] = useState(0.65); // 0 (assembled) to 1 (fully exploded)
  const [selectedPart, setSelectedPart] = useState('material');

  const components = [
    {
      id: 'mpn',
      name: 'MPN ASSEMBLY CORE',
      spec: 'DCB518ASTS06G',
      source: 'Freud Inc. Official Spec Document Page 1',
      validation: 'Exact Match',
      confidence: 1.0,
      offsetMultiplier: -1.4
    },
    {
      id: 'material',
      name: 'MATERIAL COMPOUND',
      spec: 'Aluminum Oxide',
      source: 'Diablo Technical PDF Section 4.2',
      validation: 'LOV Match',
      confidence: 0.98,
      offsetMultiplier: -0.6
    },
    {
      id: 'dimensions',
      name: 'DIMENSIONAL PROFILE',
      spec: '1/2 in x 18 in',
      source: 'Packaging Dimensional CAD Schematics',
      validation: 'UOM Standardized',
      confidence: 0.97,
      offsetMultiplier: 0.2
    },
    {
      id: 'quantity',
      name: 'PACK QUANTITY',
      spec: '6 Belts / Pack',
      source: 'Distributor Master Feed Item #60',
      validation: 'Verified',
      confidence: 0.99,
      offsetMultiplier: 1.0
    },
    {
      id: 'grit',
      name: 'GRIT GRADE',
      spec: 'Medium 80 Grit',
      source: 'Manufacturer Product Matrix',
      validation: 'Verified',
      confidence: 0.96,
      offsetMultiplier: 1.8
    }
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6 bg-slate-950/90 shadow-2xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-950 border border-cyan-500/40 text-cyan-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold font-mono-tech text-slate-100 uppercase tracking-wide">
              EXPLODED CAD BLUEPRINT DISASSEMBLY
            </h3>
            <p className="text-xs text-slate-400">
              Scrub timeline to explode product mechanical specs and inspect grounding lineage
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="text-slate-400">DISASSEMBLY EXPANSION:</span>
          <span className="text-cyan-400 font-bold font-mono-tech">{Math.round(explosionFactor * 100)}%</span>
        </div>
      </div>

      {/* CAD Schematic Canvas Area */}
      <div className="relative h-72 rounded-2xl bg-slate-950 border border-slate-800/80 overflow-hidden flex items-center justify-center p-6 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px]">
        {/* Central CAD Guideline Axis */}
        <div className="absolute w-full h-[1px] bg-cyan-500/20 left-0 top-1/2 -translate-y-1/2" />
        <div className="absolute h-full w-[1px] bg-cyan-500/10 left-1/2 top-0 -translate-x-1/2" />

        {/* Exploded Mechanical Parts Rendering */}
        <div className="relative w-full max-w-3xl h-full flex items-center justify-center">
          {components.map((comp) => {
            const offsetX = comp.offsetMultiplier * explosionFactor * 140;
            const isSelected = selectedPart === comp.id;

            return (
              <div
                key={comp.id}
                onClick={() => setSelectedPart(comp.id)}
                style={{ transform: `translateX(${offsetX}px)` }}
                className={`absolute cursor-pointer transition-all duration-500 p-3 rounded-xl border flex flex-col items-center gap-1 group ${
                  isSelected
                    ? 'bg-cyan-950/90 border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.4)] z-20 scale-105'
                    : 'bg-slate-900/80 border-slate-700 hover:border-slate-500 z-10'
                }`}
              >
                {/* CAD Mechanical Ring Wireframe Illustration */}
                <div className={`w-14 h-14 rounded-full border-2 border-dashed flex items-center justify-center transition-all ${
                  isSelected ? 'border-cyan-400 bg-cyan-950/50' : 'border-slate-600 group-hover:border-cyan-500'
                }`}>
                  <div className="w-8 h-8 rounded-full border border-slate-500 flex items-center justify-center text-[9px] font-mono font-bold text-slate-300">
                    {comp.id.toUpperCase().slice(0, 3)}
                  </div>
                </div>

                <span className="text-[10px] font-mono font-bold text-slate-200 mt-1 whitespace-nowrap">
                  {comp.spec}
                </span>
                <span className="text-[8px] font-mono text-cyan-400 opacity-80">{comp.validation}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Interactive CAD Timeline Scrubber Bar (Anime.js Scrubber Style) */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
        <div className="flex justify-between items-center text-xs font-mono">
          <span className="text-slate-400 flex items-center gap-2">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            <span>TIMELINE DISASSEMBLY SCRUBBER</span>
          </span>
          <span className="text-cyan-400 font-bold">
            {explosionFactor < 0.2 ? 'ASSEMBLED CATALOG RECORD' : explosionFactor > 0.8 ? 'FULLY EXPLODED SPECIFICATIONS' : 'DISASSEMBLY IN PROGRESS'}
          </span>
        </div>

        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={explosionFactor}
          onChange={(e) => setExplosionFactor(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-cyan-400 border border-slate-700"
        />

        <div className="flex justify-between text-[10px] font-mono text-slate-500 pt-1">
          <span>0.0 (Collapsed Product)</span>
          <span>0.5 (Exploded Assembly)</span>
          <span>1.0 (Full Spec Lineage)</span>
        </div>
      </div>

      {/* Selected Mechanical Spec Grounding Details */}
      {selectedPart && (
        <div className="p-4 rounded-xl bg-slate-950/90 border border-cyan-500/30 flex items-start gap-4 animate-in fade-in">
          <div className="p-2.5 rounded-xl bg-cyan-950 border border-cyan-500/40 text-cyan-400 font-mono font-bold text-xs shrink-0">
            {selectedPart.toUpperCase()}
          </div>
          <div className="space-y-1 text-xs font-mono">
            <div className="flex items-center gap-3">
              <span className="text-slate-100 font-bold text-sm">
                {components.find(c => c.id === selectedPart)?.name}: {components.find(c => c.id === selectedPart)?.spec}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 border border-emerald-500/40 text-emerald-400 font-bold">
                {components.find(c => c.id === selectedPart)?.validation}
              </span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Evidence Source: <span className="text-cyan-300">{components.find(c => c.id === selectedPart)?.source}</span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

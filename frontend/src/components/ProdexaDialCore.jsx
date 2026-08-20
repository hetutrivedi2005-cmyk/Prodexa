import React, { useEffect, useRef, useState } from 'react';

export const ProdexaDialCore = () => {
  const canvasRef = useRef(null);
  const [activeStage, setActiveStage] = useState('VERIFIED');
  const [rotationAngle, setRotationAngle] = useState(0);
  const mousePosRef = useRef({ x: 0, y: 0, targetRotation: 0, currentRotation: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resizeCanvas = () => {
      const container = canvas.parentElement;
      canvas.width = container.clientWidth;
      canvas.height = Math.min(480, container.clientHeight || 480);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Mouse movement physics
    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left - canvas.width / 2;
      const y = e.clientY - rect.top - canvas.height / 2;
      const angle = Math.atan2(y, x);
      mousePosRef.current.targetRotation = angle;
    };

    canvas.addEventListener('mousemove', handleMouseMove);

    let time = 0;

    const render = () => {
      time += 0.02;

      // Smooth rotational physics interpolation
      mousePosRef.current.currentRotation += (mousePosRef.current.targetRotation - mousePosRef.current.currentRotation) * 0.05;
      const rot = mousePosRef.current.currentRotation + time * 0.2;
      setRotationAngle(rot);

      const width = canvas.width;
      const height = canvas.height;
      const centerX = width / 2;
      const centerY = height / 2;
      const radius = Math.min(width, height) * 0.38;

      ctx.clearRect(0, 0, width, height);

      // Background Radial Dark Ambient Glow
      const bgGlow = ctx.createRadialGradient(centerX, centerY, 10, centerX, centerY, radius * 1.5);
      bgGlow.addColorStop(0, 'rgba(6, 182, 212, 0.15)');
      bgGlow.addColorStop(0.6, 'rgba(16, 185, 129, 0.05)');
      bgGlow.addColorStop(1, 'rgba(8, 12, 20, 0)');
      ctx.fillStyle = bgGlow;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius * 1.5, 0, Math.PI * 2);
      ctx.fill();

      // Outer Dial Metallic Housing
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(rot * 0.1);

      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 12;
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Precision Tick Marks around the Rim
      const ticks = 72;
      for (let i = 0; i < ticks; i++) {
        const tickAngle = (i * Math.PI * 2) / ticks;
        const tickLen = i % 6 === 0 ? 12 : 6;
        const rInner = radius - 16;
        const rOuter = rInner - tickLen;

        ctx.strokeStyle = i % 6 === 0 ? 'rgba(6, 182, 212, 0.8)' : 'rgba(148, 163, 184, 0.3)';
        ctx.lineWidth = i % 6 === 0 ? 2 : 1;
        ctx.beginPath();
        ctx.moveTo(Math.cos(tickAngle) * rInner, Math.sin(tickAngle) * rInner);
        ctx.lineTo(Math.cos(tickAngle) * rOuter, Math.sin(tickAngle) * rOuter);
        ctx.stroke();
      }
      ctx.restore();

      // Multi-colored Glowing RGB Arc Segments (Anime.js Dial style)
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(rot * 0.5);

      const segmentRadius = radius - 26;
      ctx.lineWidth = 6;

      // Arc 1: Green (LOV Valid)
      ctx.strokeStyle = '#10B981';
      ctx.shadowColor = '#10B981';
      ctx.shadowBlur = 15;
      ctx.beginPath();
      ctx.arc(0, 0, segmentRadius, -Math.PI * 0.8, -Math.PI * 0.1);
      ctx.stroke();

      // Arc 2: Amber (UOM Standardization)
      ctx.strokeStyle = '#F59E0B';
      ctx.shadowColor = '#F59E0B';
      ctx.shadowBlur = 15;
      ctx.beginPath();
      ctx.arc(0, 0, segmentRadius, 0.05, Math.PI * 0.65);
      ctx.stroke();

      // Arc 3: Cyan (Prodexa Intelligence Core)
      ctx.strokeStyle = '#06B6D4';
      ctx.shadowColor = '#06B6D4';
      ctx.shadowBlur = 18;
      ctx.beginPath();
      ctx.arc(0, 0, segmentRadius, Math.PI * 0.8, Math.PI * 1.45);
      ctx.stroke();
      ctx.restore();

      // Center Lens & Sine Wave Spectrum Graphic (Anime.js Lens style)
      const innerRadius = radius * 0.52;

      ctx.save();
      ctx.translate(centerX, centerY);

      // Lens Mirror Glass Surface
      const lensGradient = ctx.createLinearGradient(-innerRadius, -innerRadius, innerRadius, innerRadius);
      lensGradient.addColorStop(0, 'rgba(30, 41, 59, 0.9)');
      lensGradient.addColorStop(0.5, 'rgba(15, 23, 42, 0.95)');
      lensGradient.addColorStop(1, 'rgba(2, 6, 23, 0.98)');
      ctx.fillStyle = lensGradient;
      ctx.beginPath();
      ctx.arc(0, 0, innerRadius, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Sine Wave Harmonics Plot inside the Lens
      ctx.strokeStyle = '#F43F5E';
      ctx.shadowColor = '#F43F5E';
      ctx.shadowBlur = 8;
      ctx.lineWidth = 2;
      ctx.beginPath();

      const wavePoints = 60;
      for (let i = 0; i <= wavePoints; i++) {
        const x = -innerRadius * 0.7 + (i / wavePoints) * (innerRadius * 1.4);
        const y = Math.sin(i * 0.2 + time * 3) * 18 * Math.cos(i * 0.1);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Dotted Red Carrier Wave
      ctx.fillStyle = '#F43F5E';
      for (let i = 0; i <= wavePoints; i += 3) {
        const x = -innerRadius * 0.7 + (i / wavePoints) * (innerRadius * 1.4);
        const y = Math.sin(i * 0.2 + time * 3) * 18 * Math.cos(i * 0.1);
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();

      // Center Readout Display
      ctx.fillStyle = '#F8FAFC';
      ctx.font = 'bold 16px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('96.63%', centerX, centerY - 6);

      ctx.fillStyle = '#06B6D4';
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillText('ACCURACY', centerX, centerY + 12);

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="relative w-full h-[460px] rounded-2xl overflow-hidden glass-panel border border-slate-800 flex flex-col justify-between p-4 group">
      {/* Top Header Controls */}
      <div className="flex items-center justify-between text-xs font-mono z-10">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
          <span className="text-slate-100 font-bold tracking-wider">PRODEXA PRECISION ENGINE CORE</span>
        </div>
        <span className="px-2.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-300 font-bold text-[10px]">
          REAL-TIME SPECTROGRAM
        </span>
      </div>

      {/* Main Canvas */}
      <canvas ref={canvasRef} className="w-full h-full block cursor-grab active:cursor-grabbing" />

      {/* Bottom Interactive Readouts */}
      <div className="z-10 grid grid-cols-3 gap-2 text-center text-[10px] font-mono">
        <div className="p-2 rounded-xl bg-slate-950/80 border border-emerald-500/30 text-emerald-400">
          <p className="opacity-70">LOV MATCH</p>
          <p className="font-bold text-xs mt-0.5">100% CANONICAL</p>
        </div>
        <div className="p-2 rounded-xl bg-slate-950/80 border border-amber-500/30 text-amber-300">
          <p className="opacity-70">UOM STANDARDIZED</p>
          <p className="font-bold text-xs mt-0.5">97.13% COMPLIANT</p>
        </div>
        <div className="p-2 rounded-xl bg-slate-950/80 border border-cyan-500/30 text-cyan-300">
          <p className="opacity-70">CONFIDENCE BAND</p>
          <p className="font-bold text-xs mt-0.5">AUTO APPROVED</p>
        </div>
      </div>
    </div>
  );
};

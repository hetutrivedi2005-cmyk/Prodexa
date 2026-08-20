import React, { useEffect, useRef } from 'react';

export const ParticleCanvas = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resizeCanvas = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = Math.min(420, canvas.parentElement.clientHeight || 420);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle nodes
    const particleCount = 28;
    const labels = ['PDF', 'CSV', 'MPN', 'Catalog', 'Material', 'Size', 'UOM', 'LOV', 'Brand', 'Freud Inc'];
    const particles = Array.from({ length: particleCount }).map((_, i) => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 2.5 + 1.5,
      speedX: (Math.random() - 0.5) * 0.8,
      speedY: (Math.random() - 0.5) * 0.8,
      label: labels[i % labels.length],
      angle: Math.random() * Math.PI * 2,
      orbitRadius: 100 + Math.random() * 120
    }));

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      // Draw Central Core Glow
      const gradient = ctx.createRadialGradient(centerX, centerY, 10, centerX, centerY, 120);
      gradient.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
      gradient.addColorStop(0.5, 'rgba(16, 185, 129, 0.15)');
      gradient.addColorStop(1, 'rgba(8, 12, 20, 0)');

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, 140, 0, Math.PI * 2);
      ctx.fill();

      // Core Ring
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([6, 6]);
      ctx.beginPath();
      ctx.arc(centerX, centerY, 75, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw Core Badge Text
      ctx.fillStyle = '#F8FAFC';
      ctx.font = 'bold 12px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('PRODEXA CORE', centerX, centerY - 4);
      ctx.fillStyle = '#06B6D4';
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillText('VERIFIED DATA', centerX, centerY + 12);

      // Render Floating Nodes and Connections to Core
      particles.forEach((p) => {
        p.angle += 0.005;
        p.x = centerX + Math.cos(p.angle) * p.orbitRadius;
        p.y = centerY + Math.sin(p.angle) * (p.orbitRadius * 0.6);

        // Draw connecting laser line
        ctx.strokeStyle = 'rgba(6, 182, 212, 0.15)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(centerX, centerY);
        ctx.stroke();

        // Draw Particle Circle
        ctx.fillStyle = '#06B6D4';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        // Label Tag
        ctx.fillStyle = '#94A3B8';
        ctx.font = '9px "JetBrains Mono", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(p.label, p.x, p.y - 8);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="relative w-full h-[420px] rounded-2xl overflow-hidden glass-panel border border-slate-800 flex items-center justify-center">
      <canvas ref={canvasRef} className="w-full h-full block" />
      <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-[11px] font-mono text-slate-400 pointer-events-none px-4 py-2 rounded-xl bg-slate-950/80 border border-slate-800">
        <span>Incoming Fragmented Input Sources</span>
        <span className="text-cyan-400 font-bold animate-pulse">● Live Lineage Convergence</span>
        <span>Verified Commerce-Ready Intelligence</span>
      </div>
    </div>
  );
};

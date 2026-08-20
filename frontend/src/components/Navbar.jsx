import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Cpu, ShieldCheck, UserCheck, LogOut, Terminal, Activity } from 'lucide-react';

export const Navbar = () => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Left: Brand Identity */}
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:border-cyan-400 group-hover:shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-wider text-slate-100 font-mono-tech">PRODEXA</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded border border-cyan-500/40 bg-cyan-950/60 text-cyan-400 font-mono">v1.0.0</span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Product Intelligence Platform</p>
          </div>
        </Link>
      </div>

      {/* Center: System Status */}
      <div className="hidden md:flex items-center gap-6 px-4 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="text-slate-300 font-medium">Pipeline:</span>
          <span className="text-emerald-400 font-mono">Verified Complete (15/15)</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-2 text-slate-400">
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          <span>Evaluation Accuracy:</span>
          <span className="text-slate-200 font-mono font-semibold">96.63%</span>
        </div>
      </div>

      {/* Right: User & Role Controls */}
      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            {/* Role Badge */}
            <div className={`px-2.5 py-1 rounded-md text-xs font-mono font-semibold flex items-center gap-1.5 border ${
              role === 'ADMIN'
                ? 'bg-rose-950/60 border-rose-500/40 text-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.2)]'
                : 'bg-cyan-950/60 border-cyan-500/40 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
            }`}>
              {role === 'ADMIN' ? <ShieldCheck className="w-3.5 h-3.5" /> : <UserCheck className="w-3.5 h-3.5" />}
              <span>{role}</span>
            </div>

            {/* Profile Menu */}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-medium text-slate-200">{user.name || user.email}</p>
                <p className="text-[10px] text-slate-400 font-mono">{user.email}</p>
              </div>
              <button
                onClick={handleLogout}
                title="Logout"
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="text-xs font-semibold text-slate-300 hover:text-cyan-400 px-3 py-1.5 rounded-lg hover:bg-slate-900 transition-all"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="text-xs font-semibold text-slate-950 bg-cyan-400 hover:bg-cyan-300 px-3.5 py-1.5 rounded-lg font-mono transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
            >
              Get Access
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

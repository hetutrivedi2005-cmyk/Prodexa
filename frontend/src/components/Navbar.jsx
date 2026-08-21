import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Cpu, ShieldCheck, UserCheck, LogOut, Activity } from 'lucide-react';

export const Navbar = () => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="h-16 border-b border-[#232B35] bg-[#0A0E13]/90 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Left: Brand Identity */}
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-[#161D26] border border-[#E2A340]/40 flex items-center justify-center text-[#E2A340] group-hover:border-[#E2A340] group-hover:shadow-[0_0_15px_rgba(226,163,64,0.3)] transition-all">
            <Cpu className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-[#E7ECF2] font-display">Prodexa</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded border border-[#E2A340]/30 bg-[#161D26] text-[#E2A340] font-mono">Platform v1.0</span>
            </div>
            <p className="text-[10px] text-[#8B95A3] font-mono">Product Intelligence Engine</p>
          </div>
        </Link>
      </div>

      {/* Center: Pipeline Health Indicator */}
      <div className="hidden md:flex items-center gap-6 px-4 py-1.5 rounded-full bg-[#11161C] border border-[#232B35] text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#4FB477] animate-ping" />
          <span className="text-[#8B95A3]">Pipeline:</span>
          <span className="text-[#4FB477] font-semibold">15/15 Phases Complete</span>
        </div>
        <span className="text-[#232B35]">|</span>
        <div className="flex items-center gap-2 text-[#8B95A3]">
          <Activity className="w-3.5 h-3.5 text-[#5B9EE8]" />
          <span>Field Accuracy:</span>
          <span className="text-[#E7ECF2] font-bold">96.4%</span>
        </div>
      </div>

      {/* Right: User Role & Actions */}
      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            {/* Role Badge */}
            <div className={`px-2.5 py-1 rounded-md text-xs font-mono font-semibold flex items-center gap-1.5 border ${
              role === 'ADMIN'
                ? 'bg-[#E2634A]/10 border-[#E2634A]/40 text-[#E2634A]'
                : 'bg-[#5B9EE8]/10 border-[#5B9EE8]/40 text-[#5B9EE8]'
            }`}>
              {role === 'ADMIN' ? <ShieldCheck className="w-3.5 h-3.5" /> : <UserCheck className="w-3.5 h-3.5" />}
              <span>{role}</span>
            </div>

            {/* Profile Info */}
            <div className="flex items-center gap-2 pl-2 border-l border-[#232B35]">
              <div className="text-right hidden sm:block font-mono">
                <p className="text-xs font-semibold text-[#E7ECF2]">{user.name || user.email}</p>
                <p className="text-[10px] text-[#8B95A3]">{user.email}</p>
              </div>
              <button
                onClick={handleLogout}
                title="Logout"
                className="p-2 rounded-lg text-[#8B95A3] hover:text-[#E2634A] hover:bg-[#161D26] border border-transparent hover:border-[#232B35] transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="text-xs font-semibold text-[#8B95A3] hover:text-[#E7ECF2] px-3 py-1.5 rounded-lg hover:bg-[#161D26] transition-all font-mono"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="text-xs font-bold text-[#1A1204] bg-[#E2A340] hover:bg-[#EEB35C] px-3.5 py-1.5 rounded-lg font-mono transition-all shadow-[0_0_12px_rgba(226,163,64,0.3)]"
            >
              Get Access
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

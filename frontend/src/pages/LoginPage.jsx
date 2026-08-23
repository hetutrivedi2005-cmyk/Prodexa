import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Cpu, ShieldCheck, UserCheck, AlertTriangle, Loader2, ArrowRight } from 'lucide-react';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const user = await login(email, password);
      if (user.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/user/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setLoading(true);
    setError('');
    try {
      const user = await login(demoEmail, demoPass);
      if (user?.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/user/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0E13] text-[#E7ECF2] flex items-center justify-center p-4 relative selection:bg-[#E2A340]/30 font-sans overflow-hidden">
      {/* Background Glow & Blueprint Pattern */}
      <div className="fixed inset-0 pointer-events-none z-0 glow-backdrop" />
      <div className="fixed inset-0 pointer-events-none z-0 blueprint-bg opacity-70" />

      <div className="relative z-10 w-full max-w-md bg-[#11161C] border border-[#232B35] p-8 rounded-2xl space-y-6 shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <Link to="/" className="inline-flex items-center gap-3 group mb-1">
            <div className="w-12 h-12 rounded-xl bg-[#161D26] border border-[#E2A340]/40 flex items-center justify-center text-[#E2A340] shadow-[0_0_15px_rgba(226,163,64,0.25)] group-hover:scale-105 transition-all">
              <Cpu className="w-6 h-6 animate-pulse" />
            </div>
          </Link>
          <h2 className="text-2xl font-bold font-display tracking-tight text-[#E7ECF2]">PRODEXA PLATFORM</h2>
          <p className="text-xs text-[#8B95A3]">Sign in to access industrial product intelligence</p>
        </div>

        {/* Preset Quick Demo Login Shortcuts */}
        <div className="p-3.5 rounded-xl bg-[#161D26] border border-[#232B35] space-y-2">
          <span className="text-[10px] font-mono text-[#E2A340] uppercase font-semibold block">Quick Demo Role Shortcuts</span>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickLogin('user@prodexa.com', 'user123')}
              className="px-3 py-1.5 rounded-lg bg-[#5B9EE8]/10 border border-[#5B9EE8]/40 text-[#5B9EE8] hover:bg-[#5B9EE8]/20 text-xs font-mono flex items-center justify-center gap-1.5 transition-all"
            >
              <UserCheck className="w-3.5 h-3.5" />
              USER Role
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('admin@prodexa.com', 'admin123')}
              className="px-3 py-1.5 rounded-lg bg-[#E2634A]/10 border border-[#E2634A]/40 text-[#E2634A] hover:bg-[#E2634A]/20 text-xs font-mono flex items-center justify-center gap-1.5 transition-all"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              ADMIN Role
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-[#E2634A]/10 border border-[#E2634A]/40 text-[#E2634A] text-xs flex items-center gap-2 font-mono">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#8B95A3] font-mono uppercase">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none transition-all"
              placeholder="name@prodexa.com"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#8B95A3] font-mono uppercase">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-[#E2A340] hover:bg-[#EEB35C] text-[#1A1204] font-bold text-xs font-mono flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(226,163,64,0.3)] disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authenticating Session...</span>
              </>
            ) : (
              <>
                <span>Sign In to Platform</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-[#232B35]">
          <p className="text-xs text-[#8B95A3]">
            Don't have an account?{' '}
            <Link to="/register" className="text-[#E2A340] font-bold hover:underline">
              Request Platform Access
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

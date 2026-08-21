import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Cpu, ShieldCheck, UserCheck, AlertTriangle, Loader2, ArrowRight } from 'lucide-react';

export const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('USER');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const user = await register(email, password, name, role);
      if (user.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/user/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
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
          <h2 className="text-2xl font-bold font-display tracking-tight text-[#E7ECF2]">PLATFORM REGISTRATION</h2>
          <p className="text-xs text-[#8B95A3]">Create a new PRODEXA intelligence account</p>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-[#E2634A]/10 border border-[#E2634A]/40 text-[#E2634A] text-xs flex items-center gap-2 font-mono">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#8B95A3] font-mono uppercase">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none transition-all"
              placeholder="Product Specialist"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#8B95A3] font-mono uppercase">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] text-xs font-mono focus:border-[#E2A340] focus:outline-none transition-all"
              placeholder="name@company.com"
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

          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#8B95A3] font-mono uppercase">Access Role</label>
            <div className="grid grid-cols-2 gap-2 pt-1">
              <button
                type="button"
                onClick={() => setRole('USER')}
                className={`py-2 px-3 rounded-xl border text-xs font-mono flex items-center justify-center gap-1.5 transition-all ${
                  role === 'USER'
                    ? 'bg-[#5B9EE8]/15 border-[#5B9EE8] text-[#5B9EE8] font-bold'
                    : 'bg-[#0A0E13] border-[#232B35] text-[#8B95A3] hover:border-[#5C6572]'
                }`}
              >
                <UserCheck className="w-3.5 h-3.5" />
                USER Role
              </button>
              <button
                type="button"
                onClick={() => setRole('ADMIN')}
                className={`py-2 px-3 rounded-xl border text-xs font-mono flex items-center justify-center gap-1.5 transition-all ${
                  role === 'ADMIN'
                    ? 'bg-[#E2634A]/15 border-[#E2634A] text-[#E2634A] font-bold'
                    : 'bg-[#0A0E13] border-[#232B35] text-[#8B95A3] hover:border-[#5C6572]'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                ADMIN Role
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-[#E2A340] hover:bg-[#EEB35C] text-[#1A1204] font-bold text-xs font-mono flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(226,163,64,0.3)] disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Creating Account...</span>
              </>
            ) : (
              <>
                <span>Complete Registration</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-[#232B35]">
          <p className="text-xs text-[#8B95A3]">
            Already have an account?{' '}
            <Link to="/login" className="text-[#E2A340] font-bold hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

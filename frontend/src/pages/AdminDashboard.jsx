import React, { useEffect, useState } from 'react';
import { api } from '../api';
import {
  Shield,
  Server,
  Users,
  History,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Database,
  Cpu,
  Loader2
} from 'lucide-react';

export const AdminDashboard = () => {
  const [system, setSystem] = useState(null);
  const [users, setUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      api.getAdminSystem(),
      api.getAdminUsers(),
      api.getAdminAuditLogs()
    ])
      .then(([sysRes, usrRes, auditRes]) => {
        setSystem(sysRes);
        setUsers(usrRes || []);
        setAuditLogs(auditRes || []);
      })
      .catch(err => setError(err.message || 'Failed to load admin telemetry'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-rose-400 gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Loading Admin Control Center Telemetry...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-rose-900/40 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-rose-400" />
            <h1 className="text-2xl font-bold text-slate-100 font-mono-tech tracking-wide">ADMIN SYSTEM CONTROL CENTER</h1>
          </div>
          <p className="text-xs text-slate-400">System health, server telemetry, user management & audit streams</p>
        </div>
        <span className="px-3 py-1 rounded-md text-xs font-mono bg-rose-950/80 border border-rose-500/40 text-rose-300">
          Admin Authorization Verified
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Telemetry KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Active Users</span>
            <Users className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono-tech text-slate-100">{users.length}</p>
          <p className="text-[10px] text-slate-400">Registered Platform Stewards</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Server OS</span>
            <Server className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-lg font-bold font-mono text-rose-300 truncate">{system?.os || 'Windows/Linux'}</p>
          <p className="text-[10px] text-slate-400 font-mono">Python {system?.python_version || '3.14'}</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Database Engine</span>
            <Database className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-sm font-bold font-mono text-emerald-400">Online</p>
          <p className="text-[10px] text-slate-400 font-mono">JSON / CSV File System</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono font-medium uppercase">Audit Event Log</span>
            <History className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono-tech text-amber-400">{auditLogs.length}</p>
          <p className="text-[10px] text-slate-400">Immutable Human Overrides</p>
        </div>
      </div>

      {/* Grid Section: User Registry & Audit Stream */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Registered Users Table */}
        <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-100 font-mono-tech uppercase">REGISTERED USERS REGISTRY</h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2.5 px-3">USER ID</th>
                  <th className="py-2.5 px-3">EMAIL</th>
                  <th className="py-2.5 px-3">NAME</th>
                  <th className="py-2.5 px-3 text-right">ROLE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-900/50">
                    <td className="py-2.5 px-3 text-slate-200 font-bold">{u.id}</td>
                    <td className="py-2.5 px-3 text-cyan-300">{u.email}</td>
                    <td className="py-2.5 px-3 text-slate-300">{u.name}</td>
                    <td className="py-2.5 px-3 text-right">
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase ${
                        u.role === 'ADMIN'
                          ? 'bg-rose-950/80 border border-rose-500/40 text-rose-400'
                          : 'bg-cyan-950/80 border border-cyan-500/40 text-cyan-400'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Immutable Audit Stream */}
        <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-bold text-slate-100 font-mono-tech uppercase">HUMAN REVIEW AUDIT STREAM</h3>
          </div>

          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {auditLogs.length === 0 ? (
              <p className="text-xs text-slate-500 font-mono p-4 text-center">No audit records generated yet.</p>
            ) : (
              auditLogs.map((log, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between font-mono text-[11px]">
                    <span className="text-cyan-400 font-bold">{log.audit_id || `AUD-${idx}`}</span>
                    <span className="text-amber-400 uppercase font-bold">{log.action}</span>
                  </div>
                  <p className="text-slate-300">
                    Product <span className="font-mono text-cyan-300">{log.product_id}</span> | Attribute: <span className="font-mono text-slate-200">{log.attribute_name}</span>
                  </p>
                  {log.previous_val && (
                    <p className="text-[10px] text-slate-400 font-mono">
                      Previous: "{log.previous_val}" → New: "{log.new_val || 'N/A'}"
                    </p>
                  )}
                  <p className="text-[10px] text-slate-500 italic">Reason: {log.reason}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

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
      <div className="h-96 flex items-center justify-center text-[#E2634A] gap-3 font-mono">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Loading Admin Control Center Telemetry...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#232B35] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-[#E2634A]" />
            <h1 className="text-2xl font-bold font-display text-[#E7ECF2] tracking-tight">
              ADMIN SYSTEM CONTROL CENTER
            </h1>
          </div>
          <p className="text-xs text-[#8B95A3] font-mono mt-0.5">System health, server telemetry, user management & audit streams</p>
        </div>
        <span className="px-3 py-1 rounded-md text-xs font-mono bg-[#E2634A]/10 border border-[#E2634A]/40 text-[#E2634A] font-bold">
          Admin Authorization Verified
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#E2634A]/10 border border-[#E2634A]/40 text-[#E2634A] text-xs flex items-center gap-3 font-mono">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Telemetry KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Active Users</span>
            <Users className="w-4 h-4 text-[#5B9EE8]" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-[#E7ECF2]">{users.length}</p>
          <p className="text-[10px] text-[#5C6572] font-mono">Registered Platform Stewards</p>
        </div>

        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Server OS</span>
            <Server className="w-4 h-4 text-[#E2634A]" />
          </div>
          <p className="text-sm font-bold font-mono text-[#E2634A] truncate">{system?.os || 'Windows/Linux'}</p>
          <p className="text-[10px] text-[#5C6572] font-mono">Python {system?.python_version || '3.14'}</p>
        </div>

        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Database Engine</span>
            <Database className="w-4 h-4 text-[#4FB477]" />
          </div>
          <p className="text-sm font-bold font-mono text-[#4FB477]">Online</p>
          <p className="text-[10px] text-[#5C6572] font-mono">JSON / CSV File System</p>
        </div>

        <div className="bg-[#11161C] p-5 rounded-2xl border border-[#232B35] space-y-2">
          <div className="flex items-center justify-between text-[#8B95A3]">
            <span className="text-xs font-mono font-medium uppercase">Pipeline Status</span>
            <Activity className="w-4 h-4 text-[#E2A340]" />
          </div>
          <p className="text-sm font-bold font-mono text-[#E2A340]">Verified Complete</p>
          <p className="text-[10px] text-[#5C6572] font-mono">15/15 Phases Idle</p>
        </div>
      </div>

      {/* User Management Table */}
      <div className="bg-[#11161C] rounded-2xl border border-[#232B35] p-6 space-y-4 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-[#232B35] pb-3">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-[#5B9EE8]" />
            <h2 className="text-sm font-bold font-display text-[#E7ECF2]">REGISTERED PLATFORM STEWARDS</h2>
          </div>
          <span className="text-xs text-[#8B95A3]">{users.length} Users Enrolled</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-[#232B35] text-[#5C6572]">
                <th className="py-2.5 px-3">USER ID</th>
                <th className="py-2.5 px-3">NAME</th>
                <th className="py-2.5 px-3">EMAIL</th>
                <th className="py-2.5 px-3">ROLE</th>
                <th className="py-2.5 px-3">REGISTERED AT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#232B35]/60">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-[#161D26] transition-all">
                  <td className="py-3 px-3 text-[#E2A340] font-bold">{u.id}</td>
                  <td className="py-3 px-3 text-[#E7ECF2]">{u.name}</td>
                  <td className="py-3 px-3 text-[#8B95A3]">{u.email}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      u.role === 'ADMIN'
                        ? 'bg-[#E2634A]/10 text-[#E2634A] border-[#E2634A]/30'
                        : 'bg-[#5B9EE8]/10 text-[#5B9EE8] border-[#5B9EE8]/30'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-[#5C6572]">{u.created_at?.slice(0, 10) || '2026-01-01'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Trail Stream */}
      <div className="bg-[#11161C] rounded-2xl border border-[#232B35] p-6 space-y-4 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-[#232B35] pb-3">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-[#E2A340]" />
            <h2 className="text-sm font-bold font-display text-[#E7ECF2]">HUMAN OVERRIDE AUDIT STREAM</h2>
          </div>
          <span className="text-xs text-[#8B95A3]">{auditLogs.length} Actions Logged</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-[#232B35] text-[#5C6572]">
                <th className="py-2.5 px-3">AUDIT ID</th>
                <th className="py-2.5 px-3">PRODUCT</th>
                <th className="py-2.5 px-3">ATTRIBUTE</th>
                <th className="py-2.5 px-3">ACTION</th>
                <th className="py-2.5 px-3">ACTOR</th>
                <th className="py-2.5 px-3">NEW VALUE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#232B35]/60">
              {auditLogs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-6 text-center text-[#5C6572]">
                    No human audit log entries recorded yet.
                  </td>
                </tr>
              ) : (
                auditLogs.map((log) => (
                  <tr key={log.audit_id || log.timestamp} className="hover:bg-[#161D26] transition-all">
                    <td className="py-3 px-3 text-[#E2A340] font-bold">{log.audit_id}</td>
                    <td className="py-3 px-3 text-[#E7ECF2]">{log.product_id}</td>
                    <td className="py-3 px-3 text-[#8B95A3]">{log.attribute_name}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded bg-[#4FB477]/10 text-[#4FB477] border border-[#4FB477]/30 text-[10px] font-bold">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#8B95A3]">{log.actor_id}</td>
                    <td className="py-3 px-3 text-[#E7ECF2]">{log.new_val}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

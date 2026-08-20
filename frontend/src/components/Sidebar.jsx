import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Package,
  SearchCheck,
  UserCheck,
  FileText,
  Download,
  FileSpreadsheet,
  GitMerge,
  Upload,
  Shield,
  Server,
  Users,
  History
} from 'lucide-react';

export const Sidebar = () => {
  const { role } = useAuth();

  const workspaceNav = [
    { name: 'Overview', path: '/user/dashboard', icon: LayoutDashboard },
    { name: 'Products', path: '/user/products', icon: Package },
    { name: 'Evidence', path: '/user/evidence', icon: SearchCheck },
    { name: 'Review Queue', path: '/user/review', icon: UserCheck },
    { name: 'Descriptions', path: '/user/descriptions', icon: FileText },
    { name: 'Outputs', path: '/user/outputs', icon: Download }
  ];

  const governanceNav = [
    { name: 'Reports', path: '/user/reports', icon: FileSpreadsheet },
    { name: 'System Architecture', path: '/user/pipeline', icon: GitMerge },
    { name: 'Upload Data', path: '/user/upload', icon: Upload }
  ];

  const adminNav = [
    { name: 'System Telemetry', path: '/admin/system', icon: Server },
    { name: 'User Management', path: '/admin/users', icon: Users },
    { name: 'Audit Stream', path: '/admin/audit', icon: History }
  ];

  return (
    <aside className="w-64 bg-[#080C14] border-r border-slate-800/80 shrink-0 flex flex-col justify-between hidden md:flex">
      <div className="p-4 space-y-6">
        {/* Workspace Nav Section */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
            WORKSPACE
          </div>
          <nav className="space-y-1">
            {workspaceNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.2)] font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 text-cyan-400/80" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Governance Nav Section */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
            GOVERNANCE
          </div>
          <nav className="space-y-1">
            {governanceNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.2)] font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 text-teal-400/80" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Admin Section (Role Gated) */}
        {role === 'ADMIN' && (
          <div className="pt-4 border-t border-slate-900">
            <div className="px-3 mb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-rose-500 flex items-center gap-1.5">
              <Shield className="w-3 h-3" />
              <span>ADMINISTRATION</span>
            </div>
            <nav className="space-y-1">
              {adminNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-rose-950/80 border border-rose-500/40 text-rose-300 shadow-[0_0_12px_rgba(244,63,94,0.2)] font-semibold'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0 text-rose-400/80" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-900 bg-slate-950/50 text-[11px]">
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-400 font-mono">
          <p className="text-slate-200 font-bold">PRODEXA Core v1.0</p>
          <p className="text-[10px] mt-0.5 text-emerald-400">● 15 Phases Verified</p>
        </div>
      </div>
    </aside>
  );
};

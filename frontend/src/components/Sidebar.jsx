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
    <aside className="w-64 bg-[#0A0E13] border-r border-[#232B35] shrink-0 flex flex-col justify-between hidden md:flex font-mono text-xs">
      <div className="p-4 space-y-6">
        {/* Workspace Nav */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#5C6572]">
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
                    `flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                      isActive
                        ? 'bg-[#161D26] border border-[#E2A340]/40 text-[#E2A340] shadow-[0_0_12px_rgba(226,163,64,0.15)] font-bold'
                        : 'text-[#8B95A3] hover:text-[#E7ECF2] hover:bg-[#11161C] border border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 text-[#E2A340]" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Governance Nav */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#5C6572]">
            GOVERNANCE & REPORTS
          </div>
          <nav className="space-y-1">
            {governanceNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                      isActive
                        ? 'bg-[#161D26] border border-[#5B9EE8]/40 text-[#5B9EE8] shadow-[0_0_12px_rgba(91,158,232,0.15)] font-bold'
                        : 'text-[#8B95A3] hover:text-[#E7ECF2] hover:bg-[#11161C] border border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 text-[#5B9EE8]" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Admin Telemetry Section */}
        {role === 'ADMIN' && (
          <div>
            <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#E2634A]">
              ADMINISTRATION
            </div>
            <nav className="space-y-1">
              {adminNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                        isActive
                          ? 'bg-[#E2634A]/15 border border-[#E2634A]/40 text-[#E2634A] font-bold'
                          : 'text-[#8B95A3] hover:text-[#E7ECF2] hover:bg-[#11161C] border border-transparent'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0 text-[#E2634A]" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#232B35] text-[10px] text-[#5C6572] space-y-1">
        <div>PRODEXA Pipeline Core v1.0</div>
        <div>15 Intelligence Phases Active</div>
      </div>
    </aside>
  );
};

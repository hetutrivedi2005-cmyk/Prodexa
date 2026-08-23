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
  GitMerge,
  CheckCircle2,
  Activity,
  Settings,
  HelpCircle,
  Server,
  Users,
  History
} from 'lucide-react';

export const Sidebar = () => {
  const { user, role } = useAuth();

  const workspaceNav = [
    { name: 'Overview', path: '/user/dashboard', icon: LayoutDashboard },
    { name: 'Products', path: '/user/products', icon: Package },
    { name: 'Evidence', path: '/user/evidence', icon: SearchCheck },
    { name: 'Review Queue', path: '/user/review', icon: UserCheck },
    { name: 'Descriptions', path: '/user/descriptions', icon: FileText },
    { name: 'Outputs', path: '/user/outputs', icon: Download }
  ];

  const governanceNav = [
    { name: 'Reports', path: '/user/reports', icon: FileText },
    { name: 'Data Quality', path: '/user/validation', icon: CheckCircle2 },
    { name: 'Evaluation', path: '/user/evaluation', icon: Activity }
  ];

  const intelligenceNav = [
    { name: 'Pipeline', path: '/user/pipeline', icon: GitMerge }
  ];

  const accountNav = [
    { name: 'Settings', path: '/user/settings', icon: Settings },
    { name: 'Help', path: '/user/help', icon: HelpCircle }
  ];

  const adminNav = [
    { name: 'System Telemetry', path: '/admin/system', icon: Server },
    { name: 'User Management', path: '/admin/users', icon: Users },
    { name: 'Audit Stream', path: '/admin/audit', icon: History }
  ];

  // Helper for generating dynamic initials
  const getInitials = (name) => {
    if (!name) return 'PS';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <aside className="w-64 fixed top-16 bottom-0 left-0 bg-[#070A0F] border-r border-[#202B3B] z-30 shrink-0 flex flex-col justify-between hidden md:flex font-mono text-xs select-none">
      <div className="p-4 space-y-6 flex-1 overflow-y-auto">
        {/* Workspace Nav */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#64748B]">
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
                    `flex items-center gap-3 px-3 py-2 rounded-xl transition-all border ${
                      isActive
                        ? 'bg-[#0E131B] border-[#38BDF8]/40 text-[#38BDF8] shadow-[0_0_12px_rgba(56,189,248,0.1)] font-bold'
                        : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#0E131B] border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 transition-colors" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Governance & Reports Nav */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#64748B]">
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
                    `flex items-center gap-3 px-3 py-2 rounded-xl transition-all border ${
                      isActive
                        ? 'bg-[#0E131B] border-[#38BDF8]/40 text-[#38BDF8] shadow-[0_0_12px_rgba(56,189,248,0.1)] font-bold'
                        : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#0E131B] border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 transition-colors" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Intelligence Nav */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#64748B]">
            INTELLIGENCE
          </div>
          <nav className="space-y-1">
            {intelligenceNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-xl transition-all border ${
                      isActive
                        ? 'bg-[#0E131B] border-[#38BDF8]/40 text-[#38BDF8] shadow-[0_0_12px_rgba(56,189,248,0.1)] font-bold'
                        : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#0E131B] border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 transition-colors" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Governance / Admin (Only for ADMIN role) */}
        {role === 'ADMIN' && (
          <div>
            <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#F43F5E]">
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
                      `flex items-center gap-3 px-3 py-2 rounded-xl transition-all border ${
                        isActive
                          ? 'bg-rose-950/20 border-rose-500/40 text-rose-400 font-bold'
                          : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#0E131B] border-transparent'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0 transition-colors" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        )}

        {/* Account Nav */}
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-[#64748B]">
            ACCOUNT
          </div>
          <nav className="space-y-1">
            {accountNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-xl transition-all border ${
                      isActive
                        ? 'bg-[#0E131B] border-[#38BDF8]/40 text-[#38BDF8] shadow-[0_0_12px_rgba(56,189,248,0.1)] font-bold'
                        : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#0E131B] border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 transition-colors" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* User Info footer section */}
      {user && (
        <div className="p-4 border-t border-[#202B3B] bg-[#0E131B]/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#1A2433] border border-[#202B3B] flex items-center justify-center text-cyan-300 font-bold select-none text-[11px] uppercase tracking-wide">
            {getInitials(user.name)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-bold text-[#F1F5F9] truncate font-sans text-xs">{user.name || 'Product Specialist'}</p>
            <p className="text-[10px] text-[#64748B] truncate font-mono mt-0.5">{user.email || 'user@prodexa.com'}</p>
          </div>
        </div>
      )}
    </aside>
  );
};
export default Sidebar;

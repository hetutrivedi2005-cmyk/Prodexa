import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Building, Bell, Sliders, CheckCircle2, Shield } from 'lucide-react';

export const SettingsPage = () => {
  const { user, role } = useAuth();
  const [activeTab, setActiveTab] = useState('Profile');
  const [toast, setToast] = useState('');

  // Form states
  const [profileName, setProfileName] = useState(user?.name || 'Product Specialist');
  const [profileEmail, setProfileEmail] = useState(user?.email || 'user@prodexa.com');
  const [workspaceName, setWorkspaceName] = useState('Prodexa Catalog Operations');
  const [dataRetention, setDataRetention] = useState('30 days');
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [slackAlerts, setSlackAlerts] = useState(false);
  const [theme, setTheme] = useState('dark');
  const [confidenceThreshold, setConfidenceThreshold] = useState('85');

  const handleSave = (e) => {
    e.preventDefault();
    setToast('Settings saved successfully!');
    setTimeout(() => setToast(''), 3000);
  };

  const tabs = [
    { id: 'Profile', label: 'User Profile', icon: User },
    { id: 'Workspace', label: 'Workspace Config', icon: Building },
    { id: 'Notifications', label: 'Notifications', icon: Bell },
    { id: 'Preferences', label: 'Preferences', icon: Sliders }
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="border-b border-[#232B35] pb-4">
        <h1 className="text-2xl font-bold font-display text-[#E7ECF2] tracking-tight">SETTINGS</h1>
        <p className="text-xs text-[#8B95A3]">Manage user settings, notification rules, and workspace metadata</p>
      </div>

      {toast && (
        <div className="p-3 bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 text-xs font-mono rounded-xl flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4" />
          <span>{toast}</span>
        </div>
      )}

      {/* Tabs and Content Container */}
      <div className="grid md:grid-cols-12 gap-6">
        {/* Navigation Sidebar (internal tabs) */}
        <div className="md:col-span-3 flex flex-row md:flex-col gap-2 overflow-x-auto md:overflow-visible">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-xs font-mono font-bold shrink-0 transition-all ${
                  activeTab === tab.id
                    ? 'bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)]'
                    : 'text-[#8B95A3] hover:text-[#E7ECF2] hover:bg-[#11161C] border border-transparent'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Setting Panel Content */}
        <div className="md:col-span-9 bg-[#11161C] border border-[#232B35] rounded-2xl p-6">
          <form onSubmit={handleSave} className="space-y-6">
            
            {activeTab === 'Profile' && (
              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-[#232B35] pb-3 mb-4">
                  <User className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-sm font-bold font-display text-[#E7ECF2] uppercase">User Profile Settings</h3>
                </div>
                
                <div className="grid sm:grid-cols-2 gap-4 font-mono text-xs">
                  <div className="space-y-1.5">
                    <label className="text-[#8B95A3]">Full Name</label>
                    <input
                      type="text"
                      value={profileName}
                      onChange={(e) => setProfileName(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] focus:border-cyan-400 focus:outline-none"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[#8B95A3]">Email Address</label>
                    <input
                      type="email"
                      value={profileEmail}
                      onChange={(e) => setProfileEmail(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] focus:border-cyan-400 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="pt-2">
                  <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-500/20 flex items-start gap-3">
                    <Shield className="w-4 h-4 text-cyan-400 mt-0.5 shrink-0" />
                    <div className="text-[11px] font-mono text-slate-400">
                      <p className="text-slate-200 font-bold">Role: {role}</p>
                      <p className="mt-0.5">Permissions are managed by your administrator. Contact support to request adjustments.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'Workspace' && (
              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-[#232B35] pb-3 mb-4">
                  <Building className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-sm font-bold font-display text-[#E7ECF2] uppercase">Workspace Configurations</h3>
                </div>

                <div className="grid sm:grid-cols-2 gap-4 font-mono text-xs">
                  <div className="space-y-1.5">
                    <label className="text-[#8B95A3]">Workspace Display Name</label>
                    <input
                      type="text"
                      value={workspaceName}
                      onChange={(e) => setWorkspaceName(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] focus:border-cyan-400 focus:outline-none"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[#8B95A3]">Audit retention Period</label>
                    <select
                      value={dataRetention}
                      onChange={(e) => setDataRetention(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] focus:border-cyan-400 focus:outline-none"
                    >
                      <option value="30 days">30 Days</option>
                      <option value="90 days">90 Days</option>
                      <option value="180 days">180 Days</option>
                      <option value="indefinite">Indefinite</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'Notifications' && (
              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-[#232B35] pb-3 mb-4">
                  <Bell className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-sm font-bold font-display text-[#E7ECF2] uppercase">Notification Rules</h3>
                </div>

                <div className="space-y-3 font-mono text-xs text-slate-300">
                  <label className="flex items-center gap-3 p-3 rounded-xl bg-[#0A0E13] border border-[#232B35] cursor-pointer hover:border-cyan-500/30 transition-all">
                    <input
                      type="checkbox"
                      checked={emailAlerts}
                      onChange={(e) => setEmailAlerts(e.target.checked)}
                      className="accent-cyan-400 h-4 w-4"
                    />
                    <div>
                      <p className="text-slate-200 font-bold">Email Notifications</p>
                      <p className="text-[10px] text-slate-500">Send alerts for failed validations and items needing review.</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 rounded-xl bg-[#0A0E13] border border-[#232B35] cursor-pointer hover:border-cyan-500/30 transition-all">
                    <input
                      type="checkbox"
                      checked={slackAlerts}
                      onChange={(e) => setSlackAlerts(e.target.checked)}
                      className="accent-cyan-400 h-4 w-4"
                    />
                    <div>
                      <p className="text-slate-200 font-bold">Slack Slack Integration</p>
                      <p className="text-[10px] text-slate-500">Broadcast review alerts into designated Slack channels.</p>
                    </div>
                  </label>
                </div>
              </div>
            )}

            {activeTab === 'Preferences' && (
              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-[#232B35] pb-3 mb-4">
                  <Sliders className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-sm font-bold font-display text-[#E7ECF2] uppercase">Interface Preferences</h3>
                </div>

                <div className="grid sm:grid-cols-2 gap-4 font-mono text-xs">
                  <div className="space-y-1.5">
                    <label className="text-[#8B95A3]">System Theme</label>
                    <select
                      value={theme}
                      onChange={(e) => setTheme(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] focus:border-cyan-400 focus:outline-none"
                    >
                      <option value="dark">Deep Space (Dark)</option>
                      <option value="classic">Enterprise Dark</option>
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[#8B95A3]">Min Confidence Alert Threshold</label>
                    <input
                      type="number"
                      min="50"
                      max="100"
                      value={confidenceThreshold}
                      onChange={(e) => setConfidenceThreshold(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-[#0A0E13] border border-[#232B35] text-[#E7ECF2] focus:border-cyan-400 focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Form Footer Action */}
            <div className="border-t border-[#232B35] pt-4 flex justify-end">
              <button
                type="submit"
                className="btn-premium-cyan"
              >
                Save Settings
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
};
export default SettingsPage;

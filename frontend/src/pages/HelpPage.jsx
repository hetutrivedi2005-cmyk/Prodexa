import React, { useState } from 'react';
import { HelpCircle, FileText, Mail, ShieldAlert, BookOpen, MessageSquare } from 'lucide-react';

export const HelpPage = () => {
  const [activeTab, setActiveTab] = useState('FAQ');

  const faqs = [
    {
      q: 'How does the Prodexa Confidence Score work?',
      a: 'The Prodexa Confidence Score is dynamically calculated during Phase 10 based on evidence authority, schema compliance, unit standardization, and reference matches. Lower confidence scores trigger Human-in-the-Loop review rules.'
    },
    {
      q: 'How do I export validated product specifications?',
      a: 'Navigate to Workspace → Outputs where validated catalog data is exported in CSV and JSON formats. You can directly syndicates these files into commerce systems.'
    },
    {
      q: 'What should I do if a product is flagged as "Needs Review"?',
      a: 'Open the Review Queue under Workspace, inspect the flagged attributes alongside the matching evidence references, and either approve the suggestion, edit the value, or reject it.'
    },
    {
      q: 'How is data quality calculated?',
      a: 'Data Quality scores compliance with standard vocabularies (LOVs), Unit of Measure (UOM) compliance, attribute completeness, and schema rules across all processed catalog items.'
    }
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="border-b border-[#232B35] pb-4">
        <h1 className="text-2xl font-bold font-display text-[#E7ECF2] tracking-tight">HELP & SUPPORT</h1>
        <p className="text-xs text-[#8B95A3]">Find answers, consult the catalog manual, or contact the operations team</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        
        {/* Help Cards */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-[#11161C] border border-[#232B35] rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2 border-b border-[#232B35] pb-3">
              <BookOpen className="w-5 h-5 text-cyan-400" />
              <h2 className="text-sm font-bold font-display text-[#E7ECF2] uppercase">Frequently Asked Questions</h2>
            </div>
            
            <div className="space-y-4">
              {faqs.map((faq, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-[#0A0E13] border border-[#232B35] space-y-2">
                  <h4 className="text-xs font-bold font-mono text-cyan-300">{faq.q}</h4>
                  <p className="text-xs text-slate-300 font-sans leading-relaxed">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Support Sidebar Info */}
        <div className="space-y-6">
          <div className="bg-[#11161C] border border-[#232B35] rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2 border-b border-[#232B35] pb-3">
              <Mail className="w-5 h-5 text-cyan-400" />
              <h2 className="text-sm font-bold font-display text-[#E7ECF2] uppercase">Support Contacts</h2>
            </div>

            <div className="space-y-3 font-mono text-xs text-slate-300">
              <div className="p-3 rounded-xl bg-[#0A0E13] border border-[#232B35] space-y-1">
                <span className="text-[10px] text-slate-500 uppercase">Operational Support</span>
                <p className="text-slate-200 font-bold">ops-support@prodexa.com</p>
                <p className="text-[9px] text-slate-400">Response time: &lt; 2 Hours</p>
              </div>

              <div className="p-3 rounded-xl bg-[#0A0E13] border border-[#232B35] space-y-1">
                <span className="text-[10px] text-slate-500 uppercase">Technical Escalations</span>
                <p className="text-slate-200 font-bold">tech-leads@prodexa.com</p>
                <p className="text-[9px] text-slate-400">System architecture anomalies</p>
              </div>
            </div>
          </div>

          <div className="bg-[#11161C] border border-[#232B35] rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2 border-b border-[#232B35] pb-3">
              <ShieldAlert className="w-5 h-5 text-cyan-400" />
              <h2 className="text-sm font-bold font-display text-[#E7ECF2] uppercase">System Info</h2>
            </div>

            <div className="space-y-2 font-mono text-xs text-slate-400">
              <div className="flex justify-between border-b border-[#232B35] pb-1.5">
                <span>App Version:</span>
                <span className="text-slate-200 font-bold">Prodexa v1.0.0</span>
              </div>
              <div className="flex justify-between border-b border-[#232B35] pb-1.5">
                <span>Node Environment:</span>
                <span className="text-slate-200 font-bold">Production</span>
              </div>
              <div className="flex justify-between">
                <span>Active Workspace:</span>
                <span className="text-slate-200 font-bold">Workspace 1</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
export default HelpPage;

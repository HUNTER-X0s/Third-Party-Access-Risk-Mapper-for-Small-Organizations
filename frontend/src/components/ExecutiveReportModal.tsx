import React from 'react';
import { Shield, FileText, Download, CheckCircle2, AlertTriangle, Printer, X } from 'lucide-react';

interface ExecutiveReportModalProps {
  reportData: any;
  onClose: () => void;
}

export const ExecutiveReportModal: React.FC<ExecutiveReportModalProps> = ({ reportData, onClose }) => {
  if (!reportData) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden text-slate-800 font-sans shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-600" />
            <h2 className="font-bold text-sm text-slate-900">Executive Security Summary Report</h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="bg-white hover:bg-slate-50 text-slate-700 px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 border border-slate-200 transition-colors shadow-xs cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5 text-slate-500" />
              <span>Print / Save PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-slate-200/60 rounded-md text-slate-400 hover:text-slate-600 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Report Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs font-sans print:p-0 print:text-black">
          {/* Cover Metadata */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 flex items-center justify-between shadow-xs">
            <div>
              <div className="text-base font-bold text-slate-900">{reportData.organization_name}</div>
              <div className="text-slate-500 text-xs mt-0.5">Domain: {reportData.domain} · Assessment Date: {reportData.assessment_date}</div>
              <div className="text-slate-400 text-[11px] mt-1 font-mono">Engine: v1.5.0 · Deterministic BFS/DFS Verification</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Posture Score</div>
              <div className="text-2xl font-bold text-slate-900 font-mono mt-0.5">{reportData.security_posture_score} <span className="text-xs text-slate-400 font-normal">/ 100</span></div>
              <div className="text-[11px] text-red-600 font-bold uppercase mt-0.5">{reportData.posture_severity} Risk</div>
            </div>
          </div>

          {/* Executive Summary Paragraph */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-100 pb-1.5">1. Assessment Overview</h3>
            <p className="text-slate-600 leading-relaxed text-xs">
              AccessGuard conducted an automated, deterministic security inspection of 3rd-party SaaS integrations for <strong>{reportData.organization_name}</strong>.
              Out of <strong>{reportData.total_monitored_applications}</strong> monitored applications, <strong>{reportData.critical_risk_applications_count}</strong> are operating at Critical risk level, exposing <strong>{reportData.crown_jewel_assets_count}</strong> Crown Jewel data asset(s).
            </p>
          </div>

          {/* Key Metrics Table */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-100 pb-1.5">2. Risk Metrics Breakdown</h3>
            <div className="grid grid-cols-4 gap-3 text-center">
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <div className="text-slate-500 text-[11px]">Monitored Apps</div>
                <div className="text-lg font-bold text-slate-900 font-mono mt-1">{reportData.total_monitored_applications}</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <div className="text-slate-500 text-[11px]">Critical Findings</div>
                <div className="text-lg font-bold text-red-600 font-mono mt-1">{reportData.critical_findings_count}</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <div className="text-slate-500 text-[11px]">Crown Jewels</div>
                <div className="text-lg font-bold text-red-600 font-mono mt-1">{reportData.crown_jewel_assets_count}</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <div className="text-slate-500 text-[11px]">Data Assets Exposed</div>
                <div className="text-lg font-bold text-slate-900 font-mono mt-1">{reportData.sensitive_data_assets_count}</div>
              </div>
            </div>
          </div>

          {/* Top Priority Remediation Table */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-100 pb-1.5">3. Top Remediation Priorities (Action Required)</h3>
            <div className="bg-white border border-slate-200 rounded-lg divide-y divide-slate-100 overflow-hidden">
              {reportData.top_priorities && reportData.top_priorities.map((p: any, i: number) => (
                <div key={i} className="p-3.5 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="bg-red-50 text-red-700 border border-red-200 text-[10px] px-2 py-0.5 rounded font-bold">
                      {p.priority}
                    </span>
                    <span className="text-slate-500 font-mono">+{p.risk_contribution} pts</span>
                  </div>
                  <div className="font-semibold text-slate-900 text-xs">{p.title}</div>
                  <div className="text-slate-500 text-[11px]">Recommended: <strong className="text-emerald-700">{p.recommended_action}</strong></div>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance & Sign-off Section */}
          <div className="pt-4 border-t border-slate-200 text-[11px] text-slate-400 space-y-1">
            <div>Report verified by AccessGuard Engine with deterministic hash provenance.</div>
            <div>Sign-off: _________________________ (Chief Information Security Officer)</div>
          </div>
        </div>
      </div>
    </div>
  );
};

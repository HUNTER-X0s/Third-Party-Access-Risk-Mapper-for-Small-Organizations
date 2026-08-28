import React from 'react';
import { RiskFinding } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { AlertTriangle, FileCode, ChevronRight } from 'lucide-react';

interface FindingsPageProps {
  findings: RiskFinding[];
  onSelectFinding: (finding: RiskFinding) => void;
}

export const FindingsPage: React.FC<FindingsPageProps> = ({ findings, onSelectFinding }) => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto font-sans">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Security Findings</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {findings.length} prioritized third-party access risks, permission excesses, and attack path vulnerabilities.
          </p>
        </div>
        <div className="self-start sm:self-auto">
          <span className="text-xs font-mono text-slate-500 bg-white border border-slate-200 px-3 py-1.5 rounded-md shadow-xs">
            SHA-256 Grounded
          </span>
        </div>
      </div>

      {/* Findings Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden overflow-x-auto">
        <table className="ag-table min-w-[640px]">
          <thead>
            <tr>
              <th className="w-28">Severity</th>
              <th>Finding Title</th>
              <th>Application</th>
              <th>Type</th>
              <th>Affected Asset</th>
              <th className="text-right">Risk Impact</th>
              <th className="w-10"></th>
            </tr>
          </thead>
          <tbody>
            {findings.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-slate-400 text-xs">
                  No security findings currently recorded.
                </td>
              </tr>
            ) : (
              findings.map((f) => (
                <tr
                  key={f.id}
                  onClick={() => onSelectFinding(f)}
                  className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                >
                  <td>
                    <SeverityBadge severity={f.severity} showDot />
                  </td>
                  <td>
                    <div className="font-semibold text-slate-900 text-xs">{f.title}</div>
                    <div className="text-slate-500 text-[11px] line-clamp-1 mt-0.5">{f.description}</div>
                  </td>
                  <td className="font-medium text-slate-700">{f.affected_application_name}</td>
                  <td>
                    <span className="bg-slate-100 text-slate-600 border border-slate-200 px-2 py-0.5 rounded text-[10px] font-mono">
                      {f.finding_type}
                    </span>
                  </td>
                  <td className="text-slate-600 text-xs">{f.affected_data_name || 'N/A'}</td>
                  <td className="text-right font-mono font-bold text-red-600 text-xs">
                    +{f.risk_score_contribution} pts
                  </td>
                  <td className="text-right">
                    <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

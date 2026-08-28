import React, { useEffect, useState } from 'react';
import { DashboardSummary, RiskFinding, ApplicationInstance, SecuritySnapshot } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { SnapshotComparisonDrawer } from '../components/SnapshotComparisonDrawer';
import { api } from '../services/api';
import { Shield, AlertTriangle, Box, Database, Key, Lock, ArrowUpRight, History, GitCompare, Zap, TrendingUp, CheckCircle, ChevronRight } from 'lucide-react';
import { PRIORITY_STYLES } from '../designTokens';

interface DashboardPageProps {
  summary: DashboardSummary | null;
  searchQuery?: string;
  onSelectApplication: (app: ApplicationInstance) => void;
  onSelectFinding: (finding: RiskFinding) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  summary,
  searchQuery = '',
  onSelectApplication,
  onSelectFinding,
}) => {
  const [snapshots, setSnapshots] = useState<SecuritySnapshot[]>([]);
  const [selectedSnapshotA, setSelectedSnapshotA] = useState<string | null>(null);
  const [selectedSnapshotB, setSelectedSnapshotB] = useState<string | null>(null);

  useEffect(() => {
    api.getSnapshots().then(data => {
      setSnapshots(data);
    }).catch(err => console.error(err));
  }, []);

  if (!summary) {
    return (
      <div className="p-8 text-center text-slate-500 text-xs font-medium">
        Loading organizational security posture...
      </div>
    );
  }

  const handleTriggerCompare = () => {
    if (snapshots.length >= 2) {
      setSelectedSnapshotA(snapshots[1].id);
      setSelectedSnapshotB(snapshots[0].id);
    }
  };

  const q = searchQuery.toLowerCase().trim();
  const filteredFindings = summary.top_findings.filter(f =>
    !q || f.title.toLowerCase().includes(q) || f.affected_application_name.toLowerCase().includes(q) || f.description.toLowerCase().includes(q)
  );

  const filteredApps = summary.applications.filter(a =>
    !q || a.display_name.toLowerCase().includes(q) || (a.application.vendor?.name || '').toLowerCase().includes(q)
  );

  // Central Priority Action Queue
  const priorityQueue = [
    {
      priority: 'P0',
      title: 'GitHub Organization Admin Privilege Excess',
      app: 'GitHub Production Sync',
      currentRisk: 94.5,
      crownJewel: 'Source Code & Prop Algorithms',
      recommendedAction: 'Reduce scopes to Repository Read-Only',
      expectedReduction: '-40.9 pts',
      targetScore: '53.6',
      blastRadiusReduction: '75.0 → 50.0',
      finding: summary.top_findings.find(f => f.affected_application_name.includes('GitHub')) || summary.top_findings[0],
    },
    {
      priority: 'P1',
      title: 'Zapier Unapproved Customer Support Workflow',
      app: 'Zapier Support Automation',
      currentRisk: 78.2,
      crownJewel: 'Customer PII Database',
      recommendedAction: 'Restrict Zapier scopes & mandate Admin Approval',
      expectedReduction: '-26.2 pts',
      targetScore: '52.0',
      blastRadiusReduction: '65.0 → 40.0',
      finding: summary.top_findings.find(f => f.affected_application_name.includes('Zapier')) || summary.top_findings[1] || summary.top_findings[0],
    },
    {
      priority: 'P2',
      title: 'Canva Unapproved Dormant Marketing OAuth',
      app: 'Canva Marketing Team',
      currentRisk: 58.5,
      crownJewel: 'Brand Assets & Collateral',
      recommendedAction: 'Revoke dormant refresh token',
      expectedReduction: '-30.5 pts',
      targetScore: '28.0',
      blastRadiusReduction: '45.0 → 20.0',
      finding: summary.top_findings[2] || summary.top_findings[0],
    }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* Top Header & Posture Overview Card */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-bold text-slate-900">Third-Party Access Posture</h1>
            <span className="bg-blue-50 text-blue-700 border border-blue-200 text-[11px] px-2 py-0.5 rounded font-medium">
              Deterministic v1.5.0
            </span>
          </div>
          <p className="text-xs text-slate-500">
            {summary.organization_name} · Real-time OAuth permission graph, excess privilege detection & crown jewel exposure.
          </p>
        </div>

        {/* Posture Score Presentation */}
        <div className="flex items-center space-x-4 bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-lg">
          <div className="text-right">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Posture Score</div>
            <div className="flex items-baseline justify-end space-x-1.5">
              <span className="text-2xl font-bold text-slate-900">{summary.security_posture_score}</span>
              <span className="text-xs text-slate-400 font-medium">/ 100</span>
              <span className="ml-2 bg-amber-50 text-amber-700 border border-amber-200 text-[10px] px-1.5 py-0.2 rounded font-semibold uppercase">
                High Risk
              </span>
            </div>
          </div>

          <div className="h-8 w-px bg-slate-200" />

          <div>
            <button
              onClick={handleTriggerCompare}
              className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center space-x-1 transition-colors cursor-pointer"
            >
              <TrendingUp className="w-3.5 h-3.5 text-amber-600" />
              <span>+20.4 vs Baseline</span>
            </button>
            <span className="text-[10px] text-slate-400 block mt-0.5">Click to inspect diff</span>
          </div>
        </div>
      </div>

      {/* Compact Inline Metric Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-slate-500 text-xs font-medium flex items-center justify-between">
            <span>Applications</span>
            <Box className="w-3.5 h-3.5 text-slate-400" />
          </div>
          <div className="text-xl font-bold text-slate-900 mt-1">{summary.total_applications}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">{summary.active_applications} active integrations</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-slate-500 text-xs font-medium flex items-center justify-between">
            <span>Critical Findings</span>
            <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
          </div>
          <div className="text-xl font-bold text-red-600 mt-1">{summary.critical_findings_count}</div>
          <div className="text-[11px] text-red-600/80 mt-0.5">Immediate action required</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-slate-500 text-xs font-medium flex items-center justify-between">
            <span>High Findings</span>
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
          </div>
          <div className="text-xl font-bold text-amber-600 mt-1">{summary.high_findings_count}</div>
          <div className="text-[11px] text-amber-600/80 mt-0.5">Review within 7 days</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-slate-500 text-xs font-medium flex items-center justify-between">
            <span>Shadow SaaS</span>
            <Lock className="w-3.5 h-3.5 text-slate-500" />
          </div>
          <div className="text-xl font-bold text-slate-900 mt-1">{summary.shadow_applications}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Unapproved OAuth apps</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-slate-500 text-xs font-medium flex items-center justify-between">
            <span>Excess Scopes</span>
            <Key className="w-3.5 h-3.5 text-slate-500" />
          </div>
          <div className="text-xl font-bold text-slate-900 mt-1">{summary.total_excess_permissions}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Beyond purpose baseline</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-slate-500 text-xs font-medium flex items-center justify-between">
            <span>Crown Jewels</span>
            <Database className="w-3.5 h-3.5 text-slate-500" />
          </div>
          <div className="text-xl font-bold text-slate-900 mt-1">1</div>
          <div className="text-[11px] text-red-600 font-medium mt-0.5">Source Code exposed</div>
        </div>
      </div>

      {/* Central Priority Action Queue */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-blue-600" />
            <h2 className="font-bold text-slate-900 text-sm">Priority Remediation Queue</h2>
            <span className="text-xs text-slate-500 font-normal">· Minimum Effective Scope Reduction Model</span>
          </div>
          <span className="text-xs text-slate-400 font-medium">3 Actionable Recommendations</span>
        </div>

        <div className="overflow-x-auto">
          <table className="ag-table">
            <thead>
              <tr>
                <th className="w-16">Priority</th>
                <th>Finding & Application</th>
                <th>Exposed Asset</th>
                <th>Recommended Action</th>
                <th className="text-right">Risk Reduction</th>
                <th className="w-10"></th>
              </tr>
            </thead>
            <tbody>
              {priorityQueue.map((item, idx) => {
                const pStyle = PRIORITY_STYLES[item.priority] || PRIORITY_STYLES.P2;
                return (
                  <tr
                    key={idx}
                    onClick={() => item.finding && onSelectFinding(item.finding)}
                    className="hover:bg-slate-50 transition-colors cursor-pointer"
                  >
                    <td>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${pStyle.bg} ${pStyle.text} ${pStyle.border}`}>
                        {item.priority}
                      </span>
                    </td>
                    <td>
                      <div className="font-semibold text-slate-900 text-xs">{item.title}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">App: <span className="font-medium text-slate-700">{item.app}</span> · Current Risk: <span className="font-mono font-semibold text-red-600">{item.currentRisk}</span></div>
                    </td>
                    <td>
                      <span className="text-xs text-slate-700 font-medium">{item.crownJewel}</span>
                    </td>
                    <td>
                      <span className="text-xs text-emerald-700 font-medium">{item.recommendedAction}</span>
                    </td>
                    <td className="text-right">
                      <div className="text-xs font-bold text-emerald-700 font-mono">{item.expectedReduction}</div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">Target: {item.targetScore}</div>
                    </td>
                    <td className="text-right">
                      <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Main Grid: Active Findings & Monitored Applications */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Active Security Findings */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <h2 className="font-bold text-slate-900 text-sm">Security Findings ({filteredFindings.length})</h2>
            </div>
            <span className="text-xs text-slate-400 font-medium">Evidence Grounded</span>
          </div>

          <div className="divide-y divide-slate-100 flex-1">
            {filteredFindings.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                No security findings match the current query.
              </div>
            ) : (
              filteredFindings.map((f) => (
                <div
                  key={f.id}
                  onClick={() => onSelectFinding(f)}
                  className="p-3.5 hover:bg-slate-50/80 transition-colors cursor-pointer space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2.5">
                      <SeverityBadge severity={f.severity} showDot />
                      <span className="font-semibold text-slate-900 text-xs">{f.title}</span>
                    </div>
                    <span className="font-mono text-xs text-slate-500 font-medium">+{f.risk_score_contribution} pts</span>
                  </div>

                  <p className="text-slate-500 text-xs line-clamp-1">{f.description}</p>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                    <span>Application: <strong className="text-slate-700 font-medium">{f.affected_application_name}</strong></span>
                    <span className="text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-0.5">
                      <span>Simulate & Inspect</span>
                      <ArrowUpRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Monitored Third-Party Integrations */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center space-x-2">
              <Box className="w-4 h-4 text-blue-600" />
              <h2 className="font-bold text-slate-900 text-sm">Third-Party Integrations ({filteredApps.length})</h2>
            </div>
            <span className="text-xs text-slate-400 font-medium">Attack Path Linked</span>
          </div>

          <div className="divide-y divide-slate-100 flex-1">
            {filteredApps.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                No applications match the search query.
              </div>
            ) : (
              filteredApps.slice(0, 6).map((app) => (
                <div
                  key={app.id}
                  onClick={() => onSelectApplication(app)}
                  className="p-3.5 hover:bg-slate-50/80 transition-colors cursor-pointer flex items-center justify-between"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-slate-900 text-xs">{app.display_name}</span>
                      {app.is_shadow && (
                        <span className="bg-amber-50 text-amber-700 border border-amber-200 text-[10px] px-1.5 py-0.2 rounded font-medium">
                          Shadow
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Vendor: <span className="text-slate-700">{app.application.vendor?.name || 'Unknown'}</span> · Authorized: <span className="font-mono text-slate-600">{app.authorized_by_email}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <SeverityBadge severity={app.risk_severity} />
                    <div className="text-[11px] font-mono text-slate-600 font-medium mt-1">{app.risk_score} pts</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {/* Snapshot Comparison Drawer */}
      <SnapshotComparisonDrawer
        snapshotAId={selectedSnapshotA}
        snapshotBId={selectedSnapshotB}
        onClose={() => {
          setSelectedSnapshotA(null);
          setSelectedSnapshotB(null);
        }}
      />

    </div>
  );
};

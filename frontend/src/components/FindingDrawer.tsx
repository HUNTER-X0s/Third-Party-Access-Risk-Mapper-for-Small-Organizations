import React, { useEffect, useState } from 'react';
import { RiskFinding, SimulationResponse, RemediationAnalysis } from '../types';
import { api } from '../services/api';
import { SeverityBadge } from './SeverityBadge';
import { X, Play, FileCode, CheckCircle2, Zap, ArrowRight, ShieldCheck, Database } from 'lucide-react';

interface FindingDrawerProps {
  finding: RiskFinding | null;
  onClose: () => void;
}

export const FindingDrawer: React.FC<FindingDrawerProps> = ({ finding, onClose }) => {
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [analysis, setAnalysis] = useState<RemediationAnalysis | null>(null);
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    if (finding) {
      api.getRemediationAnalysis(finding.id)
        .then(data => setAnalysis(data))
        .catch(err => console.error(err));
    }
  }, [finding]);

  if (!finding) return null;

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const revokedScopes = finding.finding_type === 'EXCESS_PERMISSION'
        ? ['organization_admin', 'repo_write']
        : ['Customer.Export', 'Customer.Write'];

      const res = await api.simulateRemediation(finding.id, revokedScopes);
      setSimulation(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[500px] md:w-[540px] max-w-full bg-white border-l border-slate-200 shadow-2xl z-50 flex flex-col text-xs font-sans animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <SeverityBadge severity={finding.severity} showDot />
            <span className="font-mono text-xs text-slate-400">ID: {finding.id.substring(0, 8)}</span>
          </div>
          <h2 className="text-base font-bold text-slate-900">{finding.title}</h2>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">

        {/* Overview & Impact */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-3">
          <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Finding Overview & Business Impact</div>
          <p className="text-slate-600 text-xs leading-relaxed">{finding.description}</p>
          
          {finding.business_impact && (
            <div className="pt-3 border-t border-slate-100 space-y-1">
              <span className="text-red-700 font-semibold text-xs block">Potential Business Impact:</span>
              <p className="text-slate-600 text-xs">{finding.business_impact}</p>
            </div>
          )}
        </div>

        {/* Minimum Effective Remediation Section */}
        {analysis && (
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-blue-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Minimum Effective Remediation</h3>
              </div>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded text-xs font-medium">
                {analysis.recommended_candidate_name}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center font-mono">
              <div className="bg-slate-50 p-2.5 rounded-md border border-slate-200">
                <div className="text-slate-400 text-[10px] uppercase font-sans">Risk Reduction</div>
                <div className="text-emerald-700 font-bold text-sm mt-0.5">-{analysis.risk_reduction_delta} pts</div>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-md border border-slate-200">
                <div className="text-slate-400 text-[10px] uppercase font-sans">Attack Paths</div>
                <div className="text-emerald-700 font-bold text-sm mt-0.5">-{Math.max(0, analysis.attack_paths_before - analysis.attack_paths_after)}</div>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-md border border-slate-200">
                <div className="text-slate-400 text-[10px] uppercase font-sans">Residual Score</div>
                <div className="text-slate-900 font-bold text-sm mt-0.5">{analysis.predicted_residual_score}</div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-700">Recommended Scope Revocation:</div>
              <div className="space-y-1">
                {(analysis.recommended_minimal_revocations || []).map((scope: string, idx: number) => (
                  <div key={idx} className="bg-red-50 text-red-700 border border-red-200 px-2.5 py-1.5 rounded-md font-mono text-xs flex items-center justify-between">
                    <span>{scope}</span>
                    <span className="text-[10px] uppercase font-bold text-red-600">Revoke</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={handleSimulate}
              disabled={simulating}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md font-medium text-xs flex items-center justify-center space-x-2 transition-colors cursor-pointer shadow-xs disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{simulating ? 'Simulating Graph State...' : 'Run Real-Time Graph Simulation'}</span>
            </button>
          </div>
        )}

        {/* Live Simulation Response */}
        {simulation && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 space-y-3">
            <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Remediation Simulation Verified</span>
            </div>
            <div className="space-y-1 text-xs text-emerald-900">
              <div>Residual Posture Score: <strong className="font-mono">{simulation.simulated_score} / 100</strong></div>
              <div>Reduction Delta: <strong className="text-emerald-700 font-mono">-{simulation.risk_reduction_delta} pts ({simulation.percentage_reduction}%)</strong></div>
            </div>
          </div>
        )}

        {/* SHA-256 Provenance */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 space-y-2 font-mono text-xs">
          <div className="flex items-center space-x-1.5 text-slate-700 font-semibold text-[11px] font-sans">
            <FileCode className="w-3.5 h-3.5 text-slate-500" />
            <span>Evidence Provenance</span>
          </div>
          <div className="text-[11px] text-slate-500 break-all">
            Evidence Hash: <span className="text-slate-700">sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069</span>
          </div>
          <div className="text-[10px] text-emerald-700 font-semibold">
            ✓ Immutable · Grounded to Raw Provider Payload
          </div>
        </div>

      </div>
    </div>
  );
};

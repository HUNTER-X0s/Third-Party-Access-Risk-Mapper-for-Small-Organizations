import React, { useEffect, useState } from 'react';
import { SnapshotComparison } from '../types';
import { api } from '../services/api';
import { X, TrendingUp, TrendingDown, Minus, AlertTriangle, ShieldCheck, ArrowRight } from 'lucide-react';

interface SnapshotComparisonDrawerProps {
  snapshotAId: string | null;
  snapshotBId: string | null;
  onClose: () => void;
}

export const SnapshotComparisonDrawer: React.FC<SnapshotComparisonDrawerProps> = ({
  snapshotAId,
  snapshotBId,
  onClose
}) => {
  const [comparison, setComparison] = useState<SnapshotComparison | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (snapshotAId && snapshotBId) {
      setLoading(true);
      api.compareSnapshots(snapshotAId, snapshotBId)
        .then(data => {
          setComparison(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [snapshotAId, snapshotBId]);

  if (!snapshotAId || !snapshotBId) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[500px] md:w-[560px] max-w-full bg-white border-l border-slate-200 shadow-2xl z-50 flex flex-col text-xs font-sans animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-bold text-slate-900">Deterministic Risk Delta Analysis</h2>
            <span className="bg-blue-50 text-blue-700 border border-blue-200 text-[10px] px-2 py-0.5 rounded font-medium">
              Fact-Based Delta
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Comparing historical snapshot states across time
          </p>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Drawer Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {loading || !comparison ? (
          <div className="text-slate-400 text-xs p-8 text-center">Comparing snapshots...</div>
        ) : (
          <>
            {/* Score Delta Banner */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex items-center justify-between shadow-xs">
              <div>
                <div className="text-slate-400 text-[10px] uppercase font-semibold">Baseline Snapshot</div>
                <div className="text-xs font-bold text-slate-700 mt-0.5">{comparison.snapshot_a_label}</div>
                <div className="text-[11px] text-slate-400 font-mono mt-0.5">{new Date(comparison.date_a).toLocaleDateString()}</div>
              </div>

              <div className="flex items-center space-x-2 text-slate-400">
                <ArrowRight className="w-4 h-4" />
              </div>

              <div>
                <div className="text-slate-400 text-[10px] uppercase font-semibold">Target Snapshot</div>
                <div className="text-xs font-bold text-slate-900 mt-0.5">{comparison.snapshot_b_label}</div>
                <div className="text-[11px] text-slate-400 font-mono mt-0.5">{new Date(comparison.date_b).toLocaleDateString()}</div>
              </div>

              <div className="text-right border-l border-slate-200 pl-4">
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Score Delta</div>
                <div className={`text-base font-bold flex items-center justify-end space-x-1 font-mono mt-0.5 ${
                  comparison.direction === 'ESCALATED' ? 'text-amber-700' : (comparison.direction === 'IMPROVED' ? 'text-emerald-700' : 'text-slate-700')
                }`}>
                  {comparison.direction === 'ESCALATED' && <TrendingUp className="w-4 h-4 text-amber-600" />}
                  {comparison.direction === 'IMPROVED' && <TrendingDown className="w-4 h-4 text-emerald-600" />}
                  {comparison.direction === 'UNCHANGED' && <Minus className="w-4 h-4 text-slate-400" />}
                  <span>{comparison.score_a} → {comparison.score_b} ({comparison.score_delta > 0 ? `+${comparison.score_delta}` : comparison.score_delta})</span>
                </div>
              </div>
            </div>

            {/* Primary Causes Section */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Primary Root Causes & Escalations
              </h3>

              <div className="space-y-2">
                {(comparison.primary_causes || []).map((cause, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-900 text-xs">{cause.description}</span>
                      <span className="font-mono text-red-600 font-bold text-xs">+{cause.risk_score_delta} pts</span>
                    </div>
                    <div className="text-[11px] text-slate-400 pt-1 font-medium">
                      Category: <span className="text-slate-700">{cause.category}</span> · Action: <span className="font-mono">{cause.change_type}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Critical Findings Delta */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs space-y-1.5">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">New Critical Findings</div>
                <div className="space-y-1">
                  {(comparison.new_critical_findings || []).length > 0 ? (
                    comparison.new_critical_findings.map((f, idx) => (
                      <div key={idx} className="bg-red-50 text-red-700 border border-red-200 px-2 py-1 rounded text-xs font-mono font-medium">
                        + {f}
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-400 text-xs italic">None</div>
                  )}
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs space-y-1.5">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Resolved Findings</div>
                <div className="space-y-1">
                  {(comparison.resolved_critical_findings || []).length > 0 ? (
                    comparison.resolved_critical_findings.map((f, idx) => (
                      <div key={idx} className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-1 rounded text-xs font-medium">
                        ✓ {f}
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-400 text-xs italic">None</div>
                  )}
                </div>
              </div>
            </div>

            {/* Remediation guidance */}
            <div className="bg-blue-50/60 border border-blue-200 rounded-lg p-4 space-y-1.5">
              <div className="flex items-center space-x-1.5 text-blue-900 font-bold text-xs">
                <ShieldCheck className="w-4 h-4 text-blue-600" />
                <span>Deterministic Remediation Path</span>
              </div>
              <p className="text-blue-800 text-xs leading-relaxed">
                Revoking excessive admin scopes from highlighted applications will restore the organization posture score back to baseline ({comparison.score_a} pts).
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

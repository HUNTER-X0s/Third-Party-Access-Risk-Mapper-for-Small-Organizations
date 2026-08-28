import React, { useEffect, useState } from 'react';
import { ApplicationInstance, PermissionGrant, AccessRelationship, RiskFinding, ApplicationBlastRadius } from '../types';
import { api } from '../services/api';
import { SeverityBadge } from './SeverityBadge';
import { X, Key, Database, Zap, ChevronRight, Shield, AlertTriangle } from 'lucide-react';
import { STATUS_STYLES } from '../designTokens';

interface ApplicationDrawerProps {
  application: ApplicationInstance | null;
  onClose: () => void;
  onSelectFinding: (finding: RiskFinding) => void;
}

export const ApplicationDrawer: React.FC<ApplicationDrawerProps> = ({ application, onClose, onSelectFinding }) => {
  const [grants, setGrants] = useState<PermissionGrant[]>([]);
  const [accessRelationships, setAccessRelationships] = useState<AccessRelationship[]>([]);
  const [findings, setFindings] = useState<RiskFinding[]>([]);
  const [blastRadius, setBlastRadius] = useState<ApplicationBlastRadius | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (application) {
      setLoading(true);
      Promise.all([
        api.getApplicationPermissions(application.id),
        api.getApplicationDataAccess(application.id),
        api.getApplicationFindings(application.id),
        api.getApplicationBlastRadius(application.id).catch(() => null)
      ]).then(([p, d, f, b]) => {
        setGrants(p);
        setAccessRelationships(d);
        setFindings(f);
        setBlastRadius(b);
        setLoading(false);
      }).catch(err => {
        console.error(err);
        setLoading(false);
      });
    }
  }, [application]);

  if (!application) return null;

  const excessCount = grants.filter(g => g.is_excess).length;
  const statusStyle = STATUS_STYLES[application.status] || STATUS_STYLES.active;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[500px] md:w-[540px] max-w-full bg-white border-l border-slate-200 shadow-2xl z-50 flex flex-col text-xs font-sans animate-in slide-in-from-right duration-200">
      {/* Drawer Header */}
      <div className="p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-bold text-slate-900">{application.display_name}</h2>
            <SeverityBadge severity={application.risk_severity} showDot />
            {application.is_shadow && (
              <span className="bg-amber-50 text-amber-700 border border-amber-200 text-[10px] px-2 py-0.5 rounded font-medium">
                Shadow App
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500">
            Category: <span className="font-medium text-slate-700">{application.application.category}</span> · Vendor: <span className="font-medium text-slate-700">{application.application.vendor?.name || 'Unknown'}</span>
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
        
        {/* Risk Dimension Summary */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Deterministic Risk Score</span>
            <div className="flex items-baseline space-x-1">
              <span className="text-xl font-bold font-mono text-slate-900">{application.risk_score}</span>
              <span className="text-xs text-slate-400">/ 100</span>
            </div>
          </div>

          <div className="grid grid-cols-5 gap-2 pt-1 text-center font-mono">
            <div className="bg-slate-50 border border-slate-200 p-2 rounded-md">
              <div className="text-slate-400 text-[10px] uppercase font-sans">Technical</div>
              <div className="text-slate-900 font-bold text-xs mt-0.5">{application.technical_risk_score}</div>
            </div>
            <div className="bg-slate-50 border border-slate-200 p-2 rounded-md">
              <div className="text-slate-400 text-[10px] uppercase font-sans">Data Exp</div>
              <div className="text-slate-900 font-bold text-xs mt-0.5">{application.data_exposure_risk_score}</div>
            </div>
            <div className="bg-slate-50 border border-slate-200 p-2 rounded-md">
              <div className="text-slate-400 text-[10px] uppercase font-sans">Business</div>
              <div className="text-slate-900 font-bold text-xs mt-0.5">{application.business_impact_risk_score}</div>
            </div>
            <div className="bg-slate-50 border border-slate-200 p-2 rounded-md">
              <div className="text-slate-400 text-[10px] uppercase font-sans">Vendor</div>
              <div className="text-slate-900 font-bold text-xs mt-0.5">{application.vendor_risk_score}</div>
            </div>
            <div className="bg-slate-50 border border-slate-200 p-2 rounded-md">
              <div className="text-slate-400 text-[10px] uppercase font-sans">Attack Path</div>
              <div className="text-slate-900 font-bold text-xs mt-0.5">{application.attack_path_risk_score}</div>
            </div>
          </div>
        </div>

        {/* Blast Radius & Reachability */}
        {blastRadius && (
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-amber-600" />
                <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Blast Radius Exposure</h3>
              </div>
              <span className="font-mono text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded text-xs font-bold">
                {blastRadius.blast_radius_score} / 100
              </span>
            </div>

            <div className="grid grid-cols-4 gap-2 text-center font-mono">
              <div className="bg-slate-50 p-2 rounded border border-slate-200">
                <div className="text-slate-400 text-[10px] uppercase font-sans">Data Assets</div>
                <div className="text-slate-900 font-bold text-xs mt-0.5">{blastRadius.affected_data_assets_count}</div>
              </div>
              <div className="bg-red-50 p-2 rounded border border-red-200">
                <div className="text-red-600 text-[10px] uppercase font-sans font-medium">Crown Jewels</div>
                <div className="text-red-700 font-bold text-xs mt-0.5">{blastRadius.affected_crown_jewels_count}</div>
              </div>
              <div className="bg-slate-50 p-2 rounded border border-slate-200">
                <div className="text-slate-400 text-[10px] uppercase font-sans">Processes</div>
                <div className="text-slate-900 font-bold text-xs mt-0.5">{blastRadius.affected_business_processes_count}</div>
              </div>
              <div className="bg-slate-50 p-2 rounded border border-slate-200">
                <div className="text-slate-400 text-[10px] uppercase font-sans">Users</div>
                <div className="text-slate-900 font-bold text-xs mt-0.5">{blastRadius.affected_users_count}</div>
              </div>
            </div>

            {/* Blast Radius Factors */}
            <div className="pt-2 border-t border-slate-100 space-y-1.5 text-xs">
              <div className="text-slate-500 font-semibold text-[11px]">Deterministic Factors</div>
              {blastRadius.factors.map((f, idx) => (
                <div key={idx} className="flex items-center justify-between text-slate-700 py-0.5">
                  <span>· {f.name}</span>
                  <span className="font-mono text-amber-700 font-medium">+{f.delta} pts</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Security Findings */}
        {findings.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Associated Findings ({findings.length})</h3>
            </div>
            <div className="space-y-2">
              {findings.map((f) => (
                <div
                  key={f.id}
                  onClick={() => onSelectFinding(f)}
                  className="bg-white border border-slate-200 hover:border-slate-300 p-3 rounded-lg cursor-pointer transition-colors shadow-xs flex items-start justify-between"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <SeverityBadge severity={f.severity} showDot />
                      <span className="font-semibold text-slate-900 text-xs">{f.title}</span>
                    </div>
                    <p className="text-slate-500 text-[11px] line-clamp-1">{f.description}</p>
                  </div>
                  <span className="text-[11px] text-blue-600 font-medium flex items-center space-x-0.5 ml-2">
                    <span>Inspect</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Granted Scope Analysis */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
              <Key className="w-3.5 h-3.5 text-slate-500" />
              <span>Granted Permissions & Scope Analysis</span>
            </h3>
            {excessCount > 0 && (
              <span className="text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded text-[11px] font-medium">
                {excessCount} Excess Scopes
              </span>
            )}
          </div>

          <div className="bg-white border border-slate-200 rounded-lg divide-y divide-slate-100 shadow-xs overflow-hidden">
            {grants.map((g) => (
              <div key={g.id} className="p-3 space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-slate-800 font-semibold text-xs">{g.raw_scope}</span>
                    <SeverityBadge severity={g.permission.severity_level} />
                  </div>
                  {g.is_excess ? (
                    <span className="bg-red-50 text-red-700 border border-red-200 text-[10px] px-2 py-0.5 rounded font-medium">
                      Excess
                    </span>
                  ) : (
                    <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] px-2 py-0.5 rounded font-medium">
                      Justified
                    </span>
                  )}
                </div>
                <p className="text-slate-500 text-[11px]">{g.permission.description}</p>
                {g.excess_reason && (
                  <p className="text-red-600 text-[11px] pt-0.5 font-medium">⚠️ {g.excess_reason}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Reachable Data Assets */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
            <Database className="w-3.5 h-3.5 text-slate-500" />
            <span>Reachable Data Assets ({accessRelationships.length})</span>
          </h3>

          <div className="bg-white border border-slate-200 rounded-lg divide-y divide-slate-100 shadow-xs overflow-hidden">
            {accessRelationships.map((r) => (
              <div key={r.id} className="p-3 flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-slate-900 text-xs">{r.data_asset.name}</span>
                    {r.data_asset.is_crown_jewel && (
                      <span className="bg-red-50 text-red-700 border border-red-200 text-[10px] px-2 py-0.5 rounded font-medium">
                        Crown Jewel
                      </span>
                    )}
                  </div>
                  <p className="text-slate-500 text-[11px] mt-0.5">
                    System: <span className="font-mono text-slate-700">{r.data_asset.system_of_record}</span>
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-slate-800 font-semibold text-xs">{r.access_type}</div>
                  <div className="text-slate-400 text-[10px]">Level {r.data_asset.classification.sensitivity_level}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

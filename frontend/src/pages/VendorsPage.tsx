import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Building2, ShieldCheck, ShieldAlert, ShieldX, AlertTriangle,
  ChevronRight, RefreshCw, ExternalLink, Check, X, Clock, Minus,
  AlertCircle, Info, Globe, Server, Cpu, Zap, Lock, CheckCircle
} from 'lucide-react';
import { SEVERITY_STYLES, STATUS_STYLES, PRIORITY_STYLES } from '../designTokens';

// ─── Helpers ────────────────────────────────────────────────────────────────

const FOCI_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  ASSESSED_NO_CONCERN: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  POTENTIAL_CONCERN:   { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  UNKNOWN:             { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  NOT_ASSESSED:        { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
};

const PROV_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  ASSESSED: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  CLAIM:    { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  UNKNOWN:  { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
  DISPUTED: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
};

const RESILIENCE_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  CURRENT:  { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  ASSESSED: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  GAP:      { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  UNKNOWN:  { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
};

const CYBER_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  STRONG:  { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  PARTIAL: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  MINIMAL: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  UNKNOWN: { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
};

function BooleanBadge({ val }: { val?: boolean }) {
  return val
    ? <span className="inline-flex items-center gap-1 text-emerald-700 font-medium"><Check className="w-3.5 h-3.5" /> Yes</span>
    : <span className="inline-flex items-center gap-1 text-red-600 font-medium"><X className="w-3.5 h-3.5" /> No</span>;
}

function ScoreBar({ score, severity }: { score?: number; severity?: string }) {
  const num = typeof score === 'number' && !isNaN(score) ? score : 0;
  const sev = severity || (num >= 80 ? 'Critical' : num >= 60 ? 'High' : num >= 40 ? 'Medium' : 'Low');
  const color = sev === 'Critical' ? 'bg-red-500' : sev === 'High' ? 'bg-amber-500' : sev === 'Medium' ? 'bg-yellow-500' : 'bg-emerald-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(100, Math.max(0, num))}%` }} />
      </div>
      <span className="font-mono text-xs font-semibold text-slate-800 w-8 text-right">{num.toFixed(0)}</span>
    </div>
  );
}

// ─── Panel: Due Diligence Detail ─────────────────────────────────────────────

function DueDiligencePanel({ dd }: { dd: any }) {
  if (!dd) {
    return (
      <div className="text-slate-500 text-xs italic p-4 border border-slate-200 rounded-lg bg-slate-50">
        No due diligence assessment recorded for this supplier.
      </div>
    );
  }
  return (
    <div className="space-y-4">
      {/* FOCI */}
      <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-xs space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">FOCI — Foreign Ownership & Influence</span>
          <span className={`text-xs px-2 py-0.5 rounded font-medium border ${(FOCI_STYLES[dd.foci?.status] || FOCI_STYLES.NOT_ASSESSED).bg} ${(FOCI_STYLES[dd.foci?.status] || FOCI_STYLES.NOT_ASSESSED).text} ${(FOCI_STYLES[dd.foci?.status] || FOCI_STYLES.NOT_ASSESSED).border}`}>
            {dd.foci?.status?.replace(/_/g, ' ') || 'NOT ASSESSED'}
          </span>
        </div>
        {dd.foci?.details && <p className="text-slate-600 text-xs">{dd.foci.details}</p>}
        <div className="text-[11px] text-slate-400">Source: {dd.foci?.source || 'Automated Telemetry'} · Confidence: {dd.foci?.confidence || 'HIGH'}</div>
      </div>

      {/* Provenance */}
      <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-xs space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">Provenance & Hosting</span>
          <span className={`text-xs px-2 py-0.5 rounded font-medium border ${(PROV_STYLES[dd.provenance?.status] || PROV_STYLES.UNKNOWN).bg} ${(PROV_STYLES[dd.provenance?.status] || PROV_STYLES.UNKNOWN).text} ${(PROV_STYLES[dd.provenance?.status] || PROV_STYLES.UNKNOWN).border}`}>
            {dd.provenance?.status || 'UNKNOWN'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div><span className="text-slate-400">Service Origin:</span> <span className="text-slate-800 font-medium">{dd.provenance?.service_origin_country || 'United States'}</span></div>
          <div><span className="text-slate-400">Ownership:</span> <span className="text-slate-800 font-medium">{dd.provenance?.ownership_country || 'United States'}</span></div>
          <div className="col-span-2"><span className="text-slate-400">Hosting Provider:</span> <span className="text-slate-800 font-medium">{dd.provenance?.hosting_provider || 'AWS / US-East'}</span></div>
        </div>
      </div>

      {/* Resilience */}
      <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-xs space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">Resilience Evidence</span>
          <span className={`text-xs px-2 py-0.5 rounded font-medium border ${(RESILIENCE_STYLES[dd.resilience?.status] || RESILIENCE_STYLES.UNKNOWN).bg} ${(RESILIENCE_STYLES[dd.resilience?.status] || RESILIENCE_STYLES.UNKNOWN).text} ${(RESILIENCE_STYLES[dd.resilience?.status] || RESILIENCE_STYLES.UNKNOWN).border}`}>
            {dd.resilience?.status || 'UNKNOWN'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div><span className="text-slate-400">SLA:</span> <span className="text-slate-800 font-medium font-mono">{dd.resilience?.sla_availability_pct ?? 99.9}%</span></div>
          <div><span className="text-slate-400">BCP/DR:</span> <BooleanBadge val={dd.resilience?.bcp_dr_documented} /></div>
          <div><span className="text-slate-400">Backup Tested:</span> <BooleanBadge val={dd.resilience?.backup_recovery_tested} /></div>
        </div>
      </div>

      {/* Foundational Cyber Practices */}
      <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-xs space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">Foundational Cyber Practices</span>
          <span className={`text-xs px-2 py-0.5 rounded font-medium border ${(CYBER_STYLES[dd.cyber_practices?.status] || CYBER_STYLES.UNKNOWN).bg} ${(CYBER_STYLES[dd.cyber_practices?.status] || CYBER_STYLES.UNKNOWN).text} ${(CYBER_STYLES[dd.cyber_practices?.status] || CYBER_STYLES.UNKNOWN).border}`}>
            {dd.cyber_practices?.status || 'UNKNOWN'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div><span className="text-slate-400">MFA Enforced:</span> <BooleanBadge val={dd.cyber_practices?.mfa_enforced} /></div>
          <div><span className="text-slate-400">Vuln Mgmt:</span> <BooleanBadge val={dd.cyber_practices?.vuln_mgmt_documented} /></div>
          <div><span className="text-slate-400">IR Tested:</span> <BooleanBadge val={dd.cyber_practices?.incident_response_tested} /></div>
          <div><span className="text-slate-400">Encryption:</span> <BooleanBadge val={dd.cyber_practices?.encryption_in_transit_rest} /></div>
        </div>
      </div>

      {/* Assessment info */}
      <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono px-1">
        <span>Assessment v{dd.version || 1}</span>
        {dd.last_verified_at && <span>Verified: {new Date(dd.last_verified_at).toLocaleDateString()}</span>}
        {dd.reviewed_by && <span>By: {dd.reviewed_by}</span>}
      </div>
    </div>
  );
}

// ─── Supplier Detail Drawer ─────────────────────────────────────────────────

function SupplierDrawer({ supplier, onClose }: { supplier: any; onClose: () => void }) {
  const [detail, setDetail] = useState<any>(null);
  const [impact, setImpact] = useState<any>(null);
  const [explanation, setExplanation] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'due_diligence' | 'factors' | 'assets' | 'subprocessors' | 'impact' | 'history'>('due_diligence');
  const [loading, setLoading] = useState(true);

  const vendorId = supplier?.vendor_id || supplier?.id;

  useEffect(() => {
    if (!vendorId) return;
    setLoading(true);
    Promise.all([
      api.getSupplierDetails(vendorId).catch(() => null),
      api.getSupplierImpactAnalysis(vendorId).catch(() => null),
      api.explainSupplierRisk(vendorId).catch(() => null)
    ]).then(([d, i, exp]) => {
      setDetail(d);
      setImpact(i);
      setExplanation(exp);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [vendorId]);

  const supplierName = supplier.name || supplier.vendor_name || 'Supplier Details';
  const supplierStatus = supplier.status || detail?.profile?.status || 'APPROVED';
  const criticality = supplier.business_criticality || detail?.profile?.business_criticality || 'MEDIUM';

  return (
    <div className="fixed inset-y-0 right-0 w-[560px] max-w-full bg-white border-l border-slate-200 z-50 flex flex-col shadow-2xl text-xs font-sans">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Building2 className="w-4 h-4 text-blue-600" />
            <span className="font-bold text-slate-900 text-sm">{supplierName}</span>
            <span className={`text-[10px] px-2 py-0.5 rounded font-medium border ${STATUS_STYLES[supplierStatus]?.bg || 'bg-slate-100'} ${STATUS_STYLES[supplierStatus]?.text || 'text-slate-700'} ${STATUS_STYLES[supplierStatus]?.border || 'border-slate-200'}`}>
              {supplierStatus}
            </span>
          </div>
          <div className="text-[11px] text-slate-500">Criticality: <span className="font-semibold text-slate-700">{criticality}</span> · NIST SP 1326 Evaluated</div>
        </div>
        <button onClick={onClose} className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 cursor-pointer">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 px-5 flex gap-4 bg-slate-50/40 overflow-x-auto">
        {[
          { id: 'due_diligence', label: 'Due Diligence' },
          { id: 'factors', label: 'Risk Factors' },
          { id: 'assets', label: 'Data Assets' },
          { id: 'subprocessors', label: 'Subprocessors' },
          { id: 'impact', label: 'Failure Simulation' },
          { id: 'history', label: 'History' },
        ].map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as any)}
            className={`text-xs font-medium py-2.5 border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
              activeTab === t.id
                ? 'border-blue-600 text-blue-600 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
            <span>Loading supplier telemetry...</span>
          </div>
        ) : (
          <>
            {activeTab === 'due_diligence' && <DueDiligencePanel dd={detail?.due_diligence} />}

            {activeTab === 'factors' && (
              <div className="space-y-3">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Deterministic Risk Factors</div>
                <div className="space-y-2">
                  {(explanation?.contributing_factors || [
                    { factor: 'Access Exposure Impact', impact: 'High', details: 'Supplier connects active application instances with direct permissions.' },
                    { factor: 'Business Criticality', impact: criticality, details: `Classified as ${criticality} business dependency.` }
                  ]).map((f: any, idx: number) => (
                    <div key={idx} className="border border-slate-200 rounded-lg p-3.5 bg-white shadow-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-900 text-xs">{f.factor || f.name}</span>
                        <span className="font-mono text-amber-700 font-bold text-xs">{f.impact || f.delta || 'Active'}</span>
                      </div>
                      <p className="text-slate-600 text-xs">{f.details || f.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'assets' && (
              <div className="space-y-2">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Reachable Data Assets</div>
                {(detail?.accessible_data_assets || detail?.data_assets || []).length > 0 ? (
                  (detail?.accessible_data_assets || detail?.data_assets || []).map((a: any) => (
                    <div key={a.id} className="border border-slate-200 rounded-lg p-3.5 bg-white shadow-xs flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-slate-900 text-xs">{a.name}</div>
                        <div className="text-slate-400 text-[11px] mt-0.5">{a.system || a.system_of_record}</div>
                      </div>
                      {a.is_crown_jewel && (
                        <span className="bg-red-50 text-red-700 border border-red-200 text-[10px] px-2 py-0.5 rounded font-medium">
                          Crown Jewel
                        </span>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-slate-400 text-xs italic p-4 border border-slate-200 rounded-lg bg-slate-50">
                    No direct data assets exposed to this supplier.
                  </div>
                )}
              </div>
            )}

            {activeTab === 'subprocessors' && (
              <div className="space-y-3">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Subprocessor Supply Chain (Tier 2/3)</div>
                {(detail?.subprocessors || []).length > 0 ? (
                  (detail?.subprocessors || []).map((s: any) => (
                    <div key={s.id} className="border border-slate-200 rounded-lg p-3.5 bg-white shadow-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-900 text-xs">{s.name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-medium border ${s.verification_status === 'VERIFIED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-yellow-50 text-yellow-700 border-yellow-200'}`}>
                          {s.verification_status || 'DECLARED'}
                        </span>
                      </div>
                      <div className="text-slate-600 text-xs">{s.service}</div>
                      <div className="text-slate-400 text-[11px] font-mono">Tier {s.tier} · Region: {s.hosting_region || 'US'}</div>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-400 text-xs italic p-4 border border-slate-200 rounded-lg bg-slate-50">
                    No subprocessor dependencies recorded for this supplier.
                  </div>
                )}
              </div>
            )}

            {activeTab === 'impact' && (
              <div className="space-y-3">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Failure Impact Simulation — SIMULATION ONLY</div>
                {impact ? (
                  <>
                    <div className="border border-amber-200 rounded-lg p-4 bg-amber-50 space-y-1.5">
                      <div className="font-mono text-sm font-bold text-amber-900">Potential Impact Score: {impact.potential_impact_score?.toFixed(1) || '0.0'} / 100</div>
                      <div className="text-xs text-amber-800 leading-relaxed">{impact.resilience_recommendation || 'Continuous supplier monitoring active.'}</div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="border border-slate-200 rounded-lg p-3 bg-white">
                        <div className="text-[11px] font-medium text-slate-500 uppercase mb-1">Affected Applications</div>
                        {(impact.affected_applications || []).map((a: string) => <div key={a} className="text-xs font-medium text-slate-800">{a}</div>)}
                      </div>
                      <div className="border border-slate-200 rounded-lg p-3 bg-white">
                        <div className="text-[11px] font-medium text-slate-500 uppercase mb-1">Crown Jewels at Risk</div>
                        {(impact.affected_crown_jewels || []).length > 0
                          ? impact.affected_crown_jewels.map((c: string) => <div key={c} className="text-xs font-bold text-red-600">{c}</div>)
                          : <div className="text-xs text-slate-400">None</div>}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-slate-400 text-xs italic p-4 border border-slate-200 rounded-lg bg-slate-50">
                    Supplier impact simulation data not available.
                  </div>
                )}
              </div>
            )}

            {activeTab === 'history' && (
              <div className="space-y-2">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Assessment Version History</div>
                {(detail?.assessment_history || [
                  { id: '1', version: 1, change_summary: 'Initial C-SCRM due diligence seed record (synthetic demo).', reviewed_by: 'SecOps Analyst', created_at: detail?.due_diligence?.last_verified_at }
                ]).map((h: any) => (
                  <div key={h.id} className="border border-slate-200 rounded-lg p-3.5 bg-white shadow-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-900 text-xs">Version {h.version}</span>
                      <span className="text-slate-400 text-[11px]">{h.created_at ? new Date(h.created_at).toLocaleDateString() : '—'}</span>
                    </div>
                    <div className="text-slate-600 text-xs">{h.change_summary}</div>
                    <div className="text-slate-400 text-[11px]">Reviewed By: {h.reviewed_by}</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ─── Main VendorsPage ────────────────────────────────────────────────────────

export function VendorsPage() {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [priorityQueue, setPriorityQueue] = useState<any[]>([]);
  const [concentration, setConcentration] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSupplier, setSelectedSupplier] = useState<any>(null);
  const [activeView, setActiveView] = useState<'suppliers' | 'priority' | 'concentration'>('suppliers');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [critFilter, setCritFilter] = useState<string>('');

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      api.getSuppliers().catch(() => ({ suppliers: [] })),
      api.getSupplierPriorityQueue().catch(() => ({ queue: [] })),
      api.getSupplierConcentration().catch(() => ({ concentration_analysis: [] }))
    ]).then(([s, pq, conc]) => {
      setSuppliers(s?.suppliers || []);
      setPriorityQueue(pq?.queue || []);
      setConcentration(conc?.concentration_analysis || []);
      setLoading(false);
    }).catch(e => { setError(e.message); setLoading(false); });
  };

  useEffect(() => { load(); }, []);

  const filtered = suppliers.filter(s =>
    (!statusFilter || (s.status || '').toUpperCase() === statusFilter.toUpperCase()) &&
    (!critFilter || (s.business_criticality || '').toUpperCase() === critFilter.toUpperCase())
  );

  const stats = {
    total: suppliers.length,
    critical: suppliers.filter(s => s.business_criticality === 'CRITICAL').length,
    overdue: suppliers.filter(s => s.assessment_status === 'OVERDUE' || s.assessment_status === 'STALE').length,
    restricted: suppliers.filter(s => s.status === 'RESTRICTED' || s.status === 'SUSPENDED').length,
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto font-sans">
      {selectedSupplier && (
        <SupplierDrawer supplier={selectedSupplier} onClose={() => setSelectedSupplier(null)} />
      )}

      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-slate-900">Supplier & Vendor Risk Intelligence</h1>
            <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
              NIST SP 1326 Aligned
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Cyber Supply Chain Risk Management (C-SCRM): FOCI · Provenance · Resilience · Foundational Cyber Practices
          </p>
        </div>

        <button
          onClick={load}
          className="text-xs font-medium px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-md transition-colors shadow-xs flex items-center space-x-1.5 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span>Failed to load supplier risk data: {error}</span>
          </div>
          <button onClick={load} className="underline font-semibold cursor-pointer">Retry</button>
        </div>
      )}

      {/* Metric strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Total Suppliers</div>
          <div className="text-xl font-bold text-slate-900 mt-1">{stats.total}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Critical Dependencies</div>
          <div className="text-xl font-bold text-red-600 mt-1">{stats.critical}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Assessments Overdue</div>
          <div className="text-xl font-bold text-amber-600 mt-1">{stats.overdue}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <div className="text-xs font-medium text-slate-500">Restricted / Suspended</div>
          <div className="text-xl font-bold text-slate-900 mt-1">{stats.restricted}</div>
        </div>
      </div>

      {/* View Card */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
        <div className="border-b border-slate-200 px-5 flex items-center justify-between bg-slate-50/50">
          <div className="flex gap-6">
            {[
              { id: 'suppliers', label: `Suppliers Directory (${suppliers.length})` },
              { id: 'priority', label: `Priority Review Queue (${priorityQueue.length})` },
              { id: 'concentration', label: `Concentration Analysis (${concentration.length})` },
            ].map(v => (
              <button
                key={v.id}
                onClick={() => setActiveView(v.id as any)}
                className={`text-xs font-semibold py-3.5 border-b-2 transition-colors cursor-pointer ${
                  activeView === v.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                {v.label}
              </button>
            ))}
          </div>

          {activeView === 'suppliers' && (
            <div className="flex items-center gap-2 py-2">
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className="bg-white border border-slate-200 text-slate-700 text-xs rounded-md px-2.5 py-1 focus:outline-none focus:border-blue-500 cursor-pointer shadow-xs"
              >
                <option value="">All Statuses</option>
                <option value="APPROVED">Approved</option>
                <option value="ACTIVE">Active</option>
                <option value="UNDER_REVIEW">Under Review</option>
                <option value="RESTRICTED">Restricted</option>
              </select>
            </div>
          )}
        </div>

        <div className="p-5">
          {activeView === 'suppliers' && (
            <div className="border border-slate-200 rounded-lg overflow-hidden">
              <table className="ag-table">
                <thead>
                  <tr>
                    <th>Supplier</th>
                    <th>Criticality</th>
                    <th>Access Risk</th>
                    <th>Supplier Posture Risk</th>
                    <th>Crown Jewel Access</th>
                    <th>Status</th>
                    <th className="w-10"></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length > 0 ? (
                    filtered.map(s => (
                      <tr key={s.vendor_id || s.profile_id} onClick={() => setSelectedSupplier(s)} className="hover:bg-slate-50/80 transition-colors cursor-pointer">
                        <td>
                          <div className="font-semibold text-slate-900">{s.name}</div>
                          {s.website && <div className="text-[11px] text-slate-400">{s.website}</div>}
                        </td>
                        <td>
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${s.business_criticality === 'CRITICAL' ? 'bg-red-50 text-red-700 border-red-200' : s.business_criticality === 'HIGH' ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                            {s.business_criticality || 'MEDIUM'}
                          </span>
                        </td>
                        <td className="w-36">
                          <ScoreBar score={s.access_risk_score} />
                        </td>
                        <td className="w-36">
                          <ScoreBar score={s.supplier_risk_score} />
                        </td>
                        <td>
                          {s.has_crown_jewel_access ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded">
                              <AlertTriangle className="w-3 h-3 text-red-600" /> Crown Jewel
                            </span>
                          ) : (
                            <span className="text-[11px] text-slate-400">None</span>
                          )}
                        </td>
                        <td>
                          <span className={`text-[10px] font-medium px-2 py-0.5 rounded border ${STATUS_STYLES[s.status]?.bg || 'bg-slate-100'} ${STATUS_STYLES[s.status]?.text || 'text-slate-700'} ${STATUS_STYLES[s.status]?.border || 'border-slate-200'}`}>
                            {s.status || 'APPROVED'}
                          </span>
                        </td>
                        <td className="text-right">
                          <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="text-center py-8 text-slate-400 text-xs">
                        No suppliers match the selected filter criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeView === 'priority' && (
            <div className="border border-slate-200 rounded-lg overflow-hidden">
              <table className="ag-table">
                <thead>
                  <tr>
                    <th className="w-16">Priority</th>
                    <th>Supplier</th>
                    <th>Review Reason</th>
                    <th>Criticality</th>
                    <th>Access Risk</th>
                    <th className="w-10"></th>
                  </tr>
                </thead>
                <tbody>
                  {priorityQueue.length > 0 ? (
                    priorityQueue.map((item, idx) => (
                      <tr key={idx} onClick={() => setSelectedSupplier(item)} className="hover:bg-slate-50/80 transition-colors cursor-pointer">
                        <td>
                          <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${(item.priority || 'P0') === 'P0' ? 'bg-red-50 text-red-700 border-red-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
                            {item.priority || 'P0'}
                          </span>
                        </td>
                        <td className="font-semibold text-slate-900">{item.vendor_name || item.name}</td>
                        <td className="text-slate-700 text-xs">{item.priority_reason || 'Scheduled due diligence review.'}</td>
                        <td>
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${item.business_criticality === 'CRITICAL' ? 'bg-red-50 text-red-700 border-red-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                            {item.business_criticality || 'HIGH'}
                          </span>
                        </td>
                        <td className="w-32">
                          <ScoreBar score={item.access_risk_score} />
                        </td>
                        <td className="text-right">
                          <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-slate-400 text-xs">
                        No suppliers currently pending in the review queue.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeView === 'concentration' && (
            <div className="space-y-4">
              {concentration.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {concentration.map((c, idx) => (
                    <div key={idx} className="border border-slate-200 rounded-lg p-4 bg-white shadow-xs space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-bold text-slate-900 text-sm">{c.vendor_name}</h3>
                        <span className={`text-xs px-2 py-0.5 rounded font-bold border ${(c.concentration_level || 'MEDIUM') === 'CRITICAL' ? 'bg-red-50 text-red-700 border-red-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
                          {c.concentration_level || 'MEDIUM'} Concentration
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div><span className="text-slate-500">Connected Apps:</span> <strong className="text-slate-800">{c.application_count ?? 1}</strong></div>
                        <div><span className="text-slate-500">Crown Jewels Reachable:</span> <strong className="text-red-600">{c.crown_jewels_count ?? 0}</strong></div>
                      </div>
                      <div className="space-y-1">
                        {(c.concentration_reasons || []).map((reason: string, rIdx: number) => (
                          <p key={rIdx} className="text-slate-600 text-xs flex items-start gap-1.5">
                            <span className="text-blue-500 font-bold">•</span>
                            <span>{reason}</span>
                          </p>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400 text-xs border border-slate-200 rounded-lg bg-slate-50">
                  No concentration risk flags detected.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

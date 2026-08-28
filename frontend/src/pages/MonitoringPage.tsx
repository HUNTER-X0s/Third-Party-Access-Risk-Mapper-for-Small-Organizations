import React, { useEffect, useState, useCallback } from 'react';
import { api } from '../services/api';
import { Activity, Play, CheckCircle2, AlertTriangle, ArrowRight, Network, Bell, Clock, RefreshCw, X, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { SEVERITY_STYLES } from '../designTokens';

// ─── Types ─────────────────────────────────────────────────────────────────────
interface SecurityChange {
  id: string;
  change_type: string;
  object_type: string;
  object_id: string;
  object_name: string;
  timestamp: string;
  source: string;
  severity: string;
  confidence: string;
  evidence_refs: string[];
  impact_summary: string;
  status: string;
  snapshot_before_id: string | null;
  snapshot_after_id: string | null;
}

interface SecurityIncident {
  id: string;
  detected_at: string;
  source: string;
  severity: string;
  summary: string;
  change_count: number;
  risk_before: number;
  risk_after: number;
  risk_delta: number;
  status: string;
}

interface SecurityNotification {
  id: string;
  title: string;
  body: string;
  severity: string;
  notification_type: string;
  source_type: string;
  source_id: string | null;
  is_read: boolean;
  created_at: string;
}

interface MonitoringStatus {
  monitoring_enabled: boolean;
  demo_mode: boolean;
  status: string;
  interval_seconds: number;
  last_evaluation_at: string | null;
  next_evaluation_at: string | null;
  last_changes_detected: number;
  consecutive_failures: number;
}

const CHANGE_TYPE_LABELS: Record<string, string> = {
  PERMISSION_ESCALATED:            'Permission Escalated',
  PERMISSION_REDUCED:              'Permission Reduced',
  CROWN_JEWEL_REACHABILITY_CREATED:'Crown Jewel Reachability Created',
  CROWN_JEWEL_REACHABILITY_REMOVED:'Crown Jewel Reachability Removed',
  SHADOW_SAAS_DETECTED:            'Shadow SaaS Detected',
  APPLICATION_ADDED:               'Application Added',
  APPLICATION_REMOVED:             'Application Removed',
  RISK_INCREASED:                  'Risk Increased',
  RISK_DECREASED:                  'Risk Decreased',
  FINDING_CREATED:                 'Finding Created',
  FINDING_RESOLVED:                'Finding Resolved',
};

const INCIDENT_STATUS_OPTIONS = ['OPEN', 'INVESTIGATING', 'REMEDIATED', 'ACCEPTED', 'FALSE_POSITIVE'] as const;

function relativeTime(iso: string | null): string {
  if (!iso) return '—';
  try {
    const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  } catch {
    return iso;
  }
}

interface MonitoringPageProps {
  onNavigate: (tab: string, targetId?: string) => void;
}

// ─── Change Detail Drawer ────────────────────────────────────────────────────────
function ChangeDetailDrawer({
  change,
  onClose,
  onNavigate,
}: {
  change: SecurityChange;
  onClose: () => void;
  onNavigate: (tab: string, targetId?: string) => void;
}) {
  const sev = SEVERITY_STYLES[change.severity] || SEVERITY_STYLES.Info;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[500px] md:w-[540px] max-w-full bg-white border-l border-slate-200 shadow-2xl z-50 flex flex-col text-xs font-sans animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold border ${sev.bg} ${sev.text} ${sev.border}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${sev.dot}`} />
              {change.severity}
            </span>
            <span className="font-semibold text-slate-800 text-xs">
              {CHANGE_TYPE_LABELS[change.change_type] ?? change.change_type}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-mono">ID: {change.id.substring(0, 8)}</p>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Topology link */}
        {change.object_type === 'APPLICATION' && (
          <div className="bg-blue-50/60 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
            <div className="text-xs text-slate-700">
              <span className="text-blue-700 font-bold block text-[11px] uppercase tracking-wider">Access Graph Topology</span>
              <span>Inspect changes in the interactive topological map</span>
            </div>
            <button
              onClick={() => onNavigate('graph')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition-colors cursor-pointer shadow-xs"
            >
              <Network className="w-3.5 h-3.5" />
              <span>View in Graph</span>
            </button>
          </div>
        )}

        {/* Object */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-1">
          <p className="text-slate-400 text-[10px] uppercase font-semibold tracking-wider">Affected Object</p>
          <p className="text-slate-900 text-sm font-bold">{change.object_name || change.object_id}</p>
          <p className="text-slate-500 text-xs font-mono">{change.object_type} · ID: {change.object_id}</p>
        </div>

        {/* Impact */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-2">
          <p className="text-slate-400 text-[10px] uppercase font-semibold tracking-wider">Impact Summary</p>
          <p className="text-slate-700 text-xs leading-relaxed">{change.impact_summary}</p>
        </div>

        {/* Metadata grid */}
        <div className="grid grid-cols-2 gap-3">
          {[
            ['Detected', relativeTime(change.timestamp)],
            ['Source', change.source],
            ['Confidence', change.confidence],
            ['Status', change.status],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <p className="text-slate-400 text-[10px] uppercase font-medium">{label}</p>
              <p className="text-slate-900 text-xs font-bold font-mono mt-0.5">{value}</p>
            </div>
          ))}
        </div>

        {/* Evidence refs */}
        {change.evidence_refs?.length > 0 && (
          <div className="space-y-2">
            <p className="text-slate-400 text-[10px] uppercase font-semibold tracking-wider">Evidence References</p>
            <div className="flex flex-wrap gap-1.5">
              {change.evidence_refs.map((ref: string) => (
                <span key={ref} className="px-2 py-0.5 bg-slate-50 text-slate-700 text-xs rounded-md border border-slate-200 font-mono">
                  {ref}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Recommendation */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-1.5">
          <p className="text-amber-800 text-xs font-bold flex items-center space-x-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>Recommended Operational Action</span>
          </p>
          <p className="text-amber-900 text-xs leading-relaxed">
            {change.change_type === 'PERMISSION_ESCALATED'
              ? 'Review and reduce permissions to the minimum required for declared business purpose.'
              : change.change_type === 'SHADOW_SAAS_DETECTED'
              ? 'Initiate a security review. Approve, restrict, or initiate revocation if unauthorized.'
              : change.change_type === 'CROWN_JEWEL_REACHABILITY_CREATED'
              ? 'Immediately investigate the access path. Revoke or scope-limit access to the crown jewel.'
              : 'Review the change and update the application baseline as appropriate.'}
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Incident Row ─────────────────────────────────────────────────────────────────
function IncidentRow({ incident, onStatusChange }: { incident: SecurityIncident; onStatusChange: (id: string, status: string) => void }) {
  const sev = SEVERITY_STYLES[incident.severity] ?? SEVERITY_STYLES.Info;
  const [updating, setUpdating] = useState(false);
  const [localStatus, setLocalStatus] = useState(incident.status);

  const handleStatusChange = async (newStatus: string) => {
    setUpdating(true);
    try {
      await api.updateIncidentStatus(incident.id, newStatus);
      setLocalStatus(newStatus);
      onStatusChange(incident.id, newStatus);
    } catch { /* noop */ }
    finally { setUpdating(false); }
  };

  return (
    <tr className="hover:bg-slate-50/80 transition-colors">
      <td>
        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold border ${sev.bg} ${sev.text} ${sev.border}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${sev.dot}`} />
          {incident.severity}
        </span>
      </td>
      <td className="max-w-sm">
        <p className="text-slate-900 font-medium text-xs leading-snug">{incident.summary}</p>
        <p className="text-slate-400 text-[11px] mt-0.5">{relativeTime(incident.detected_at)} · {incident.change_count} change(s)</p>
      </td>
      <td className="text-center font-mono">
        <span className={`text-xs font-bold ${incident.risk_delta >= 0 ? 'text-red-600' : 'text-emerald-700'}`}>
          {incident.risk_delta >= 0 ? '+' : ''}{incident.risk_delta.toFixed(1)}
        </span>
        <p className="text-slate-400 text-[10px]">{incident.risk_before?.toFixed(0)} → {incident.risk_after?.toFixed(0)}</p>
      </td>
      <td>
        <select
          value={localStatus}
          onChange={(e) => handleStatusChange(e.target.value)}
          disabled={updating}
          className="text-xs bg-white border border-slate-200 text-slate-700 rounded-md px-2.5 py-1 focus:outline-none focus:border-blue-500 cursor-pointer shadow-xs"
        >
          {INCIDENT_STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </td>
    </tr>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────────
export default function MonitoringPage({ onNavigate }: MonitoringPageProps) {
  const { user } = useAuth();
  const [changes, setChanges] = useState<SecurityChange[]>([]);
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [notifications, setNotifications] = useState<SecurityNotification[]>([]);
  const [statusMeta, setStatusMeta] = useState<MonitoringStatus | null>(null);
  const [selectedChange, setSelectedChange] = useState<SecurityChange | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningCheck, setRunningCheck] = useState(false);
  const [activeTab, setActiveTab] = useState<'changes' | 'incidents' | 'notifications'>('changes');
  const [severityFilter, setSeverityFilter] = useState('');
  const [bannerMsg, setBannerMsg] = useState<string | null>(null);

  const isAuthorizedToRun = user?.role === 'SUPER_ADMIN' || user?.role === 'SECURITY_ADMIN' || user?.role === 'IT_ADMIN';

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [changesRes, incidentsRes, notifsRes, statusRes] = await Promise.all([
        api.getSecurityChanges(),
        api.getSecurityIncidents(),
        api.getNotifications(),
        api.getMonitoringStatus().catch(() => null)
      ]);
      setChanges(changesRes as SecurityChange[]);
      setIncidents(incidentsRes as SecurityIncident[]);
      setNotifications(notifsRes as SecurityNotification[]);
      if (statusRes) setStatusMeta(statusRes as MonitoringStatus);
    } catch { /* noop */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleRunCheckNow = async () => {
    if (runningCheck) return;
    setRunningCheck(true);
    try {
      const res = await api.triggerMonitoringRun();
      setBannerMsg(res.message || "Continuous monitoring cycle completed.");
      loadData();
      setTimeout(() => setBannerMsg(null), 5000);
    } catch (err: any) {
      alert("Failed to execute monitoring check: " + err.message);
    } finally {
      setRunningCheck(false);
    }
  };

  const filteredChanges = changes.filter(c => !severityFilter || c.severity === severityFilter);

  const criticalCount = changes.filter(c => c.severity === 'Critical').length;
  const highCount = changes.filter(c => c.severity === 'High').length;
  const openIncidents = incidents.filter(i => i.status === 'OPEN').length;
  const unreadNotifs = notifications.filter(n => !n.is_read).length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {selectedChange && (
        <ChangeDetailDrawer change={selectedChange} onClose={() => setSelectedChange(null)} onNavigate={onNavigate} />
      )}

      {/* Banner */}
      {bannerMsg && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-xs text-emerald-800 flex items-center justify-between shadow-xs">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{bannerMsg}</span>
          </div>
          <button onClick={() => setBannerMsg(null)} className="text-emerald-600 hover:text-emerald-800 cursor-pointer">✕</button>
        </div>
      )}

      {/* Page Header with Scheduler Status & Run Action */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-slate-900">Continuous Access Monitoring</h1>
            <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md border text-xs bg-slate-50 border-slate-200">
              <span className={`w-2 h-2 rounded-full ${
                statusMeta?.status === 'ACTIVE' ? 'bg-emerald-500' :
                statusMeta?.status === 'DEGRADED' ? 'bg-red-500' : 'bg-slate-400'
              }`} />
              <span className="text-slate-800 font-semibold uppercase text-[11px]">{statusMeta?.status || 'ACTIVE'}</span>
              {statusMeta?.demo_mode && <span className="text-slate-400 text-[10px]">(DEMO)</span>}
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Deterministic security diff engine · Last evaluation: <span className="font-medium text-slate-700">{relativeTime(statusMeta?.last_evaluation_at || '')}</span> · Next: <span className="font-medium text-slate-700">{statusMeta?.next_evaluation_at ? relativeTime(statusMeta.next_evaluation_at) : 'On demand'}</span>
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          {isAuthorizedToRun && (
            <button
              onClick={handleRunCheckNow}
              disabled={runningCheck}
              className="text-xs font-medium px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors flex items-center space-x-1.5 shadow-xs disabled:opacity-50 cursor-pointer"
              title="Trigger on-demand continuous monitoring evaluation"
            >
              <Play className={`w-3.5 h-3.5 ${runningCheck ? 'animate-spin' : ''}`} />
              <span>{runningCheck ? 'Evaluating...' : 'Run Check Now'}</span>
            </button>
          )}
          <button
            onClick={loadData}
            disabled={loading}
            className="text-xs font-medium px-3 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-md transition-colors disabled:opacity-50 flex items-center space-x-1.5 shadow-xs cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Metric Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <p className="text-slate-500 text-xs font-medium">Total Changes</p>
          <p className="text-xl font-bold text-slate-900 mt-1">{changes.length}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <p className="text-slate-500 text-xs font-medium">Critical Changes</p>
          <p className="text-xl font-bold text-red-600 mt-1">{criticalCount}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <p className="text-slate-500 text-xs font-medium">Open Incidents</p>
          <p className="text-xl font-bold text-amber-600 mt-1">{openIncidents}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs">
          <p className="text-slate-500 text-xs font-medium">Unread Alerts</p>
          <p className={`text-xl font-bold mt-1 ${unreadNotifs > 0 ? 'text-amber-600' : 'text-slate-900'}`}>{unreadNotifs}</p>
        </div>
      </div>

      {/* Main Table Card */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
        {/* Tabs */}
        <div className="border-b border-slate-200 px-3 sm:px-5 flex gap-4 sm:gap-6 bg-slate-50/50 overflow-x-auto whitespace-nowrap">
          {(['changes', 'incidents', 'notifications'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`text-xs font-semibold py-3.5 border-b-2 transition-colors cursor-pointer ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              {tab === 'changes' && `Detected Changes (${changes.length})`}
              {tab === 'incidents' && `Security Incidents (${incidents.length})`}
              {tab === 'notifications' && `Alerts (${notifications.length})`}
            </button>
          ))}
        </div>

        <div className="p-3 sm:p-5">
          {activeTab === 'changes' && (
            <div className="space-y-4">
              {/* Filter row */}
              <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                <span className="text-slate-500 text-xs font-medium mr-1">Filter:</span>
                {(['', 'Critical', 'High', 'Medium', 'Low', 'Info'] as const).map(sev => (
                  <button
                    key={sev}
                    onClick={() => setSeverityFilter(sev)}
                    className={`text-xs px-2.5 py-1 rounded-md border transition-colors cursor-pointer ${
                      severityFilter === sev
                        ? 'bg-blue-50 border-blue-200 text-blue-700 font-semibold'
                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    {sev || 'All'}
                  </button>
                ))}
              </div>

              {/* Changes table */}
              <div className="border border-slate-200 rounded-lg overflow-hidden overflow-x-auto">
                <table className="ag-table min-w-[600px]">
                  <thead>
                    <tr>
                      <th className="w-28">Severity</th>
                      <th>Change Type</th>
                      <th>Object</th>
                      <th>Detected</th>
                      <th>Confidence</th>
                      <th>Status</th>
                      <th className="w-10"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {loading ? (
                      <tr><td colSpan={7} className="p-8 text-center text-slate-400 text-xs">Loading security changes...</td></tr>
                    ) : filteredChanges.length === 0 ? (
                      <tr><td colSpan={7} className="p-8 text-center text-slate-400 text-xs">No security changes detected.</td></tr>
                    ) : filteredChanges.map(c => {
                      const sev = SEVERITY_STYLES[c.severity] ?? SEVERITY_STYLES.Info;
                      return (
                        <tr key={c.id} className="hover:bg-slate-50/80 transition-colors cursor-pointer" onClick={() => setSelectedChange(c)}>
                          <td>
                            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold border ${sev.bg} ${sev.text} ${sev.border}`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${sev.dot}`} />
                              {c.severity}
                            </span>
                          </td>
                          <td className="font-medium text-slate-800">{CHANGE_TYPE_LABELS[c.change_type] ?? c.change_type}</td>
                          <td className="text-slate-700 font-medium max-w-[200px] truncate" title={c.object_name}>{c.object_name || c.object_id}</td>
                          <td className="text-slate-500 font-mono text-xs">{relativeTime(c.timestamp)}</td>
                          <td>
                            <span className={`text-[10px] px-2 py-0.5 rounded border font-medium ${
                              c.confidence === 'VERIFIED' ? 'border-emerald-200 text-emerald-700 bg-emerald-50'
                              : 'border-slate-200 text-slate-600 bg-slate-50'
                            }`}>{c.confidence}</span>
                          </td>
                          <td className="text-slate-600 font-mono text-xs">{c.status}</td>
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
          )}

          {activeTab === 'incidents' && (
            <div className="border border-slate-200 rounded-lg overflow-hidden overflow-x-auto">
              <table className="ag-table min-w-[540px]">
                <thead>
                  <tr>
                    <th className="w-28">Severity</th>
                    <th>Incident Summary</th>
                    <th className="text-center">Risk Delta</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan={4} className="p-8 text-center text-slate-400 text-xs">Loading incidents...</td></tr>
                  ) : incidents.length === 0 ? (
                    <tr><td colSpan={4} className="p-8 text-center text-slate-400 text-xs">No correlated security incidents.</td></tr>
                  ) : incidents.map(inc => (
                    <IncidentRow
                      key={inc.id}
                      incident={inc}
                      onStatusChange={(id, status) => setIncidents(prev => prev.map(i => i.id === id ? {...i, status} : i))}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="border border-slate-200 rounded-lg overflow-hidden overflow-x-auto">
              <table className="ag-table min-w-[580px]">
                <thead>
                  <tr>
                    <th className="w-28">Severity</th>
                    <th>Notification Detail</th>
                    <th>Type</th>
                    <th>Detected</th>
                    <th>State</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan={5} className="p-8 text-center text-slate-400 text-xs">Loading notifications...</td></tr>
                  ) : notifications.length === 0 ? (
                    <tr><td colSpan={5} className="p-8 text-center text-slate-400 text-xs">No security notifications recorded.</td></tr>
                  ) : notifications.map(notif => {
                    const sev = SEVERITY_STYLES[notif.severity] ?? SEVERITY_STYLES.Info;
                    return (
                      <tr key={notif.id} className="hover:bg-slate-50/80 transition-colors">
                        <td>
                          <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold border ${sev.bg} ${sev.text} ${sev.border}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${sev.dot}`} />
                            {notif.severity}
                          </span>
                        </td>
                        <td className="max-w-md">
                          <p className="text-slate-900 font-semibold text-xs">{notif.title}</p>
                          <p className="text-slate-500 text-xs mt-0.5">{notif.body}</p>
                        </td>
                        <td className="text-slate-600 font-mono text-xs">{notif.notification_type}</td>
                        <td className="text-slate-500 font-mono text-xs">{relativeTime(notif.created_at)}</td>
                        <td>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                            notif.is_read
                              ? 'text-slate-500 bg-slate-100'
                              : 'text-amber-700 bg-amber-50 border border-amber-200 font-semibold'
                          }`}>
                            {notif.is_read ? 'Read' : 'Unread'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

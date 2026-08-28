import React, { useState, useEffect } from 'react';
import { ProviderConnector } from '../types';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Link2, RefreshCw, Unplug, Plus, ShieldAlert, CheckCircle2,
  AlertTriangle, Clock, Server, FileCode, ChevronRight, X, Info
} from 'lucide-react';

interface ConnectorsPageProps {
  onSelectApplication?: (appId: string) => void;
}

const RAW_TO_CANONICAL_DEMO_MAP = [
  { provider: 'GitHub', rawScope: 'contents:write', canonical: 'WRITE', severity: 'HIGH', impact: 'Modify repository code & history' },
  { provider: 'GitHub', rawScope: 'administration:write', canonical: 'ADMIN', severity: 'CRITICAL', impact: 'Full admin access to organization & repos' },
  { provider: 'GitHub', rawScope: 'metadata:read', canonical: 'READ', severity: 'INFO', impact: 'Read org metadata (always required)' },
  { provider: 'GitHub', rawScope: 'secrets:read', canonical: 'READ', severity: 'CRITICAL', impact: 'Access repository & org secrets' },
  { provider: 'GitHub', rawScope: 'organization_hooks:write', canonical: 'ADMIN', severity: 'CRITICAL', impact: 'Manage org webhooks — data routing' },
  { provider: 'GitHub', rawScope: 'future_unknown_permission', canonical: 'UNKNOWN', severity: 'HIGH', impact: 'Unmapped permission — surfaced for human review' },
];

export const ConnectorsPage: React.FC<ConnectorsPageProps> = () => {
  const { user } = useAuth();
  const [connectors, setConnectors] = useState<ProviderConnector[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncingId, setSyncingId] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form state for creating connector
  const [provider, setProvider] = useState('GITHUB');
  const [displayName, setDisplayName] = useState('GitHub Organization Access');
  const [mode, setMode] = useState<'LIVE' | 'DEMO'>('DEMO');

  const isAdmin = user && ['SUPER_ADMIN', 'SECURITY_ADMIN', 'IT_ADMIN'].includes(user.role);
  const isSuperAdmin = user && user.role === 'SUPER_ADMIN';

  const loadConnectors = async () => {
    try {
      setLoading(true);
      const data = await api.getConnectors();
      setConnectors(data);
    } catch (err: any) {
      console.error('Failed to load connectors:', err);
      setConnectors([
        {
          id: 'conn-github-demo',
          provider: 'GITHUB',
          display_name: 'GitHub App (Demo Seed)',
          mode: 'DEMO',
          status: 'HEALTHY',
          last_sync_at: new Date().toISOString(),
          apps_discovered: 3,
          permissions_discovered: 12,
          data_freshness_seconds: 120,
          config: { app_id: 'demo-app-101', api_version: '2022-11-28' },
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConnectors();
  }, []);

  const handleSyncNow = async (id: string) => {
    try {
      setSyncingId(id);
      setErrorMsg(null);
      await api.triggerConnectorSync(id);
      setSuccessMsg('Synchronization triggered in background.');
      setTimeout(() => setSuccessMsg(null), 4000);
      await loadConnectors();
    } catch (err: any) {
      setErrorMsg(err.message || 'Sync failed');
    } finally {
      setSyncingId(null);
    }
  };

  const handleDisconnect = async (id: string) => {
    if (!window.confirm('Disconnect this connector? AccessGuard configuration will be removed. No external provider permissions will be revoked.')) {
      return;
    }
    try {
      setErrorMsg(null);
      await api.disconnectConnector(id);
      setSuccessMsg('Connector disconnected.');
      setTimeout(() => setSuccessMsg(null), 4000);
      await loadConnectors();
    } catch (err: any) {
      setErrorMsg(err.message || 'Disconnect failed');
    }
  };

  const handleCreateConnector = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setErrorMsg(null);
      await api.createConnector({
        provider,
        display_name: displayName,
        mode,
        config: { app_id: 'configured-via-ui', api_version: '2022-11-28' }
      });
      setShowAddModal(false);
      setSuccessMsg(`Configured ${provider} connector (${mode} mode).`);
      setTimeout(() => setSuccessMsg(null), 4000);
      await loadConnectors();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create connector');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'HEALTHY':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200"><CheckCircle2 className="w-3 h-3 mr-1" /> Healthy</span>;
      case 'DEGRADED':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200"><AlertTriangle className="w-3 h-3 mr-1" /> Degraded</span>;
      case 'STALE':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-yellow-50 text-yellow-700 border border-yellow-200"><Clock className="w-3 h-3 mr-1" /> Stale</span>;
      case 'AUTH_FAILED':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-red-50 text-red-700 border border-red-200"><ShieldAlert className="w-3 h-3 mr-1" /> Auth Failed</span>;
      default:
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto font-sans">
      {/* Messages */}
      {errorMsg && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-xs flex items-center justify-between shadow-xs">
          <span>⚠️ {errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-red-500 hover:text-red-700 cursor-pointer">✕</button>
        </div>
      )}
      {successMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded-lg text-xs flex items-center justify-between shadow-xs">
          <span>✓ {successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-600 hover:text-emerald-800 cursor-pointer">✕</button>
        </div>
      )}

      {/* Header bar */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-50 text-blue-600 rounded-md">
            <Link2 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Provider Connectors & Integrations</h1>
            <p className="text-xs text-slate-500 mt-0.5">Read-only SaaS OAuth & application inventory connectors</p>
          </div>
        </div>

        <div>
          {isAdmin && (
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-2 rounded-md text-xs font-medium flex items-center space-x-1.5 transition-colors shadow-xs cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Configure Connector</span>
            </button>
          )}
        </div>
      </div>

      {/* Security Guarantee Box */}
      <div className="bg-blue-50/60 border border-blue-200 p-4 rounded-lg text-slate-800 flex items-start space-x-3 shadow-xs">
        <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
        <div className="space-y-1 text-xs">
          <p className="font-bold text-blue-900 uppercase tracking-wider text-[11px]">
            Read-Only Security Boundary & Architectural Guarantee
          </p>
          <p className="text-slate-600 leading-relaxed">
            All live connectors operate with strict <strong className="text-slate-900">READ=True, WRITE=False</strong> architectural guards. 
            Credentials (App JWTs, PEM private keys) remain backend-only in server environment variables and are never persisted in databases or sent to client browsers. 
            Imported provider scope strings are normalized through a provider-neutral translation pipeline into AccessGuard canonical permissions.
          </p>
        </div>
      </div>

      {/* Active Connectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {connectors.map((c) => (
          <div key={c.id} className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-4">
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <Server className="w-4 h-4 text-slate-500" />
                  <span className="font-bold text-slate-900 text-sm">{c.display_name}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                    c.mode === 'LIVE' 
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                      : 'bg-amber-50 text-amber-700 border-amber-200'
                  }`}>
                    {c.mode === 'LIVE' ? 'Live Connector' : 'Demo / Simulated'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Provider: <span className="font-medium text-slate-800">{c.provider}</span> · API Version: <span className="font-mono text-slate-600">{c.config?.api_version || '2022-11-28'}</span>
                </p>
              </div>

              <div>{getStatusBadge(c.status)}</div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-2 text-xs bg-slate-50 p-3 rounded-lg border border-slate-200">
              <div>
                <span className="text-slate-400 text-[10px] uppercase font-medium block">Discovered Apps</span>
                <span className="text-slate-900 font-bold text-sm mt-0.5 block">{c.apps_discovered}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] uppercase font-medium block">Permissions</span>
                <span className="text-slate-900 font-bold text-sm mt-0.5 block">{c.permissions_discovered}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] uppercase font-medium block">Data Freshness</span>
                <span className="text-slate-800 font-medium text-xs mt-0.5 block">
                  {c.data_freshness_seconds !== undefined && c.data_freshness_seconds !== null
                    ? `${Math.round(c.data_freshness_seconds / 60)} min ago`
                    : 'Just now'}
                </span>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-between pt-1">
              <span className="text-slate-400 text-[11px]">
                Last Sync: {c.last_sync_at ? new Date(c.last_sync_at).toLocaleString() : 'Never'}
              </span>

              <div className="flex items-center space-x-2">
                {isAdmin && (
                  <button
                    onClick={() => handleSyncNow(c.id)}
                    disabled={syncingId === c.id}
                    className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 shadow-xs disabled:opacity-50 cursor-pointer"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${syncingId === c.id ? 'animate-spin' : ''}`} />
                    <span>{syncingId === c.id ? 'Syncing...' : 'Sync Now'}</span>
                  </button>
                )}

                {isSuperAdmin && (
                  <button
                    onClick={() => handleDisconnect(c.id)}
                    className="bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1 transition-colors cursor-pointer"
                  >
                    <Unplug className="w-3.5 h-3.5" />
                    <span>Disconnect</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Roadmap Placeholder */}
        <div className="bg-white border border-slate-200 border-dashed rounded-lg p-5 space-y-3 flex flex-col justify-between shadow-xs">
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2">
              <Server className="w-4 h-4 text-slate-400" />
              <span className="font-bold text-slate-700 text-sm">Google Workspace & Microsoft 365</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">Roadmap</span>
            </div>
            <p className="text-slate-500 text-xs leading-relaxed">
              Provider-neutral connector architecture designed for multi-SaaS expansion. Next roadmap connectors ingest OAuth grants and directory permissions without changing the core deterministic risk engine.
            </p>
          </div>

          <div className="text-[11px] text-slate-400 border-t border-slate-100 pt-3">
            Status: Architecture Ready · Write Guard Enforced
          </div>
        </div>
      </div>

      {/* Permission Normalization Inspection Panel */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 space-y-4 shadow-xs">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <FileCode className="w-4 h-4 text-blue-600" />
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Provider Permission Normalization & Scope Provenance
          </h2>
        </div>

        <p className="text-slate-600 text-xs leading-relaxed">
          AccessGuard maps raw third-party scopes to canonical permissions (<code className="text-slate-800 font-mono font-semibold">READ</code>, <code className="text-slate-800 font-mono font-semibold">WRITE</code>, <code className="text-slate-800 font-mono font-semibold">ADMIN</code>, <code className="text-slate-800 font-mono font-semibold">UNKNOWN</code>). 
          Unrecognized scope keys produce an <strong className="text-amber-700">UNKNOWN</strong> status and are surfaced for review rather than silently downgraded.
        </p>

        <div className="border border-slate-200 rounded-lg overflow-hidden overflow-x-auto">
          <table className="ag-table min-w-[560px]">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Raw Scope</th>
                <th>Canonical</th>
                <th>Severity</th>
                <th>Impact & Provenance</th>
              </tr>
            </thead>
            <tbody>
              {RAW_TO_CANONICAL_DEMO_MAP.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                  <td className="font-semibold text-slate-900">{row.provider}</td>
                  <td className="font-mono text-slate-700">{row.rawScope}</td>
                  <td>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      row.canonical === 'ADMIN' ? 'bg-red-50 text-red-700 border-red-200' :
                      row.canonical === 'WRITE' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      row.canonical === 'UNKNOWN' ? 'bg-purple-50 text-purple-700 border-purple-200' :
                      'bg-slate-100 text-slate-700 border-slate-200'
                    }`}>
                      {row.canonical}
                    </span>
                  </td>
                  <td>
                    <span className={
                      row.severity === 'CRITICAL' ? 'text-red-700 font-bold' :
                      row.severity === 'HIGH' ? 'text-amber-700 font-semibold' : 'text-slate-600'
                    }>
                      {row.severity}
                    </span>
                  </td>
                  <td className="text-slate-600">{row.impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Connector Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-sm">Configure New Connector</h3>
              <button onClick={() => setShowAddModal(false)} className="p-1 rounded-md text-slate-400 hover:text-slate-600 cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateConnector} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-700 font-medium mb-1">Provider</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900 focus:outline-none focus:border-blue-600 cursor-pointer"
                >
                  <option value="GITHUB">GitHub (Read-Only App)</option>
                  <option value="GOOGLE_WORKSPACE" disabled>Google Workspace (Roadmap)</option>
                  <option value="MS365" disabled>Microsoft 365 (Roadmap)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-medium mb-1">Display Name</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  required
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900 focus:outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-medium mb-1">Connector Mode</label>
                <select
                  value={mode}
                  onChange={(e) => setMode(e.target.value as 'LIVE' | 'DEMO')}
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900 focus:outline-none focus:border-blue-600 cursor-pointer"
                >
                  <option value="DEMO">Demo / Simulated Data (Default)</option>
                  <option value="LIVE">Live Connector (Requires Env Credentials)</option>
                </select>
              </div>

              <div className="bg-slate-50 border border-slate-200 p-3 rounded-lg text-slate-600 text-[11px] space-y-1">
                <p className="font-semibold text-slate-900">🔒 Credential Security Note:</p>
                <p>
                  Sensitive credentials (<code className="text-slate-800 font-mono">GITHUB_APP_ID</code> and <code className="text-slate-800 font-mono">GITHUB_PRIVATE_KEY</code>) 
                  are loaded exclusively from server environment variables. Secrets are never typed here, logged, or sent to the browser.
                </p>
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="bg-white border border-slate-200 text-slate-700 px-3.5 py-1.5 rounded-md hover:bg-slate-50 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-md font-medium transition-colors shadow-xs cursor-pointer"
                >
                  Save Connector
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

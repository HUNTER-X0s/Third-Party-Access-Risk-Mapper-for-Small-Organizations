import {
  DashboardSummary,
  ApplicationInstance,
  PermissionGrant,
  AccessRelationship,
  RiskFinding,
  RawEvidence,
  SimulationResponse,
  AccessGraphData,
  PotentialAttackPath,
  ApplicationBlastRadius,
  SecuritySnapshot,
  SnapshotComparison,
  RemediationAnalysis,
  ProviderConnector,
  ConnectorHealth,
  SyncRunResponse
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // Anti-CSRF Custom Header
  };

  if (options?.headers) {
    Object.assign(headers, options.headers);
  }

  const response = await fetch(url, {
    credentials: 'include', // Include HttpOnly cookies for browser authentication
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error (${response.status}): ${errorText}`);
  }

  return response.json();
}

export const api = {
  // --- PHASE 4 & 4.1 & 4.2 AUTH & USER APIs ---
  login: (email: string, password: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  logout: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/auth/logout`, {
      method: 'POST',
    }),

  getMe: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/auth/me`),

  getUsers: (): Promise<any[]> => fetchJson<any[]>(`${API_BASE}/users`),

  createUser: (email: string, display_name: string, role: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/users`, {
      method: 'POST',
      body: JSON.stringify({ email, display_name, role }),
    }),

  updateUserRole: (id: string, role: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/users/${id}/role`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    }),

  updateUserStatus: (id: string, status: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/users/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // --- CORE SECOPS APIs ---
  getDashboard: (): Promise<DashboardSummary> => fetchJson<DashboardSummary>(`${API_BASE}/dashboard`),
  
  getApplications: (): Promise<ApplicationInstance[]> => fetchJson<ApplicationInstance[]>(`${API_BASE}/applications`),
  
  getApplication: (id: string): Promise<ApplicationInstance> => fetchJson<ApplicationInstance>(`${API_BASE}/applications/${id}`),
  
  getApplicationPermissions: (id: string): Promise<PermissionGrant[]> => fetchJson<PermissionGrant[]>(`${API_BASE}/applications/${id}/permissions`),
  
  getApplicationDataAccess: (id: string): Promise<AccessRelationship[]> => fetchJson<AccessRelationship[]>(`${API_BASE}/applications/${id}/data`),
  
  getApplicationFindings: (id: string): Promise<RiskFinding[]> => fetchJson<RiskFinding[]>(`${API_BASE}/applications/${id}/findings`),
  
  getFindings: (): Promise<RiskFinding[]> => fetchJson<RiskFinding[]>(`${API_BASE}/findings`),
  
  getFinding: (id: string): Promise<RiskFinding> => fetchJson<RiskFinding>(`${API_BASE}/findings/${id}`),
  
  simulateRemediation: (findingId: string, revokedScopes: string[]): Promise<SimulationResponse> =>
    fetchJson<SimulationResponse>(`${API_BASE}/findings/${findingId}/simulate-remediation`, {
      method: 'POST',
      body: JSON.stringify({ revoked_scopes: revokedScopes }),
    }),
    
  getEvidence: (id: string): Promise<RawEvidence> => fetchJson<RawEvidence>(`${API_BASE}/evidence/${id}`),
  
  getAccessGraph: (): Promise<AccessGraphData> => fetchJson<AccessGraphData>(`${API_BASE}/graph`),

  getPotentialAttackPaths: (): Promise<PotentialAttackPath[]> => fetchJson<PotentialAttackPath[]>(`${API_BASE}/graph/paths`),

  getApplicationBlastRadius: (id: string): Promise<ApplicationBlastRadius> => fetchJson<ApplicationBlastRadius>(`${API_BASE}/graph/blast-radius/${id}`),

  getCrownJewelReachability: (): Promise<any[]> => fetchJson<any[]>(`${API_BASE}/graph/reachability/crown-jewels`),

  getSnapshots: (): Promise<SecuritySnapshot[]> => fetchJson<SecuritySnapshot[]>(`${API_BASE}/snapshots`),

  createSnapshot: (label: string, reason: string = "MANUAL_SNAPSHOT"): Promise<SecuritySnapshot> =>
    fetchJson<SecuritySnapshot>(`${API_BASE}/snapshots`, {
      method: 'POST',
      body: JSON.stringify({ snapshot_label: label, trigger_reason: reason }),
    }),

  compareSnapshots: (idA: string, idB: string): Promise<SnapshotComparison> =>
    fetchJson<SnapshotComparison>(`${API_BASE}/snapshots/${idA}/compare/${idB}`),

  getRemediationAnalysis: (findingId: string): Promise<RemediationAnalysis> =>
    fetchJson<RemediationAnalysis>(`${API_BASE}/findings/${findingId}/remediation-analysis`),

  resetDemo: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/demo/reset`, { method: 'POST' }),

  getExecutiveReport: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/demo/report`),

  // --- PHASE 5 CONNECTOR APIs ---
  getConnectors: (): Promise<ProviderConnector[]> =>
    fetchJson<ProviderConnector[]>(`${API_BASE}/connectors`),

  getConnector: (id: string): Promise<ProviderConnector> =>
    fetchJson<ProviderConnector>(`${API_BASE}/connectors/${id}`),

  createConnector: (data: { provider: string; display_name: string; mode: string; config?: any }): Promise<ProviderConnector> =>
    fetchJson<ProviderConnector>(`${API_BASE}/connectors`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  triggerConnectorSync: (id: string): Promise<{ status: string; sync_run_id: string }> =>
    fetchJson<any>(`${API_BASE}/connectors/${id}/sync`, {
      method: 'POST',
    }),

  getConnectorHealth: (id: string): Promise<ConnectorHealth> =>
    fetchJson<ConnectorHealth>(`${API_BASE}/connectors/${id}/health`),

  disconnectConnector: (id: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/connectors/${id}/disconnect`, {
      method: 'POST',
    }),

  // ── Phase 7: Continuous Monitoring & Shadow SaaS ─────────────────────────
  getSecurityChanges: (params?: { severity?: string; change_type?: string }): Promise<any[]> => {
    const qs = new URLSearchParams();
    if (params?.severity) qs.set('severity', params.severity);
    if (params?.change_type) qs.set('change_type', params.change_type);
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return fetchJson<any[]>(`${API_BASE}/monitoring/changes${query}`);
  },

  getSecurityIncidents: (statusFilter?: string): Promise<any[]> => {
    const query = statusFilter ? `?status=${statusFilter}` : '';
    return fetchJson<any[]>(`${API_BASE}/monitoring/incidents${query}`);
  },

  updateIncidentStatus: (incidentId: string, status: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/incidents/${incidentId}/status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    }),

  getShadowSaasInventory: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/shadow-saas`),

  approveApplication: (appId: string, isApproved: boolean, approvalStatus: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/applications/${appId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ is_approved: isApproved, approval_status: approvalStatus }),
    }),

  getSecurityTimeline: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/timeline`),

  // ── Phase 7.1: Notifications, Scheduler & Graph Delta ────────────────────
  getNotifications: (params?: { is_read?: boolean; severity?: string; notification_type?: string }): Promise<any[]> => {
    const qs = new URLSearchParams();
    if (params?.is_read !== undefined) qs.set('is_read', String(params.is_read));
    if (params?.severity) qs.set('severity', params.severity);
    if (params?.notification_type) qs.set('notification_type', params.notification_type);
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return fetchJson<any[]>(`${API_BASE}/monitoring/notifications${query}`);
  },

  getUnreadNotificationCount: (): Promise<{ unread_count: number; critical_unread_count: number }> =>
    fetchJson<any>(`${API_BASE}/monitoring/notifications/count`),

  markNotificationRead: (id: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/notifications/${id}/read`, {
      method: 'POST',
    }),

  markAllNotificationsRead: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/notifications/read-all`, {
      method: 'POST',
    }),

  getMonitoringStatus: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/status`),

  triggerMonitoringRun: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/monitoring/run`, {
      method: 'POST',
    }),

  getAccessGraphDelta: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/graph/delta`),

  // Phase 8: Supplier / Vendor Risk Intelligence
  getSuppliers: (params?: { status?: string; criticality?: string }): Promise<any> => {
    const query = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
    return fetchJson<any>(`${API_BASE}/vendors${query}`);
  },

  getSupplierDetails: (vendorId: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/vendors/${vendorId}`),

  getSupplierPriorityQueue: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/vendors/priority-queue`),

  getSupplierConcentration: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/vendors/concentration`),

  getSupplierImpactAnalysis: (vendorId: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/vendors/${vendorId}/impact-analysis`),

  updateSupplierDueDiligence: (vendorId: string, body: Record<string, any>): Promise<any> =>
    fetchJson<any>(`${API_BASE}/vendors/${vendorId}/assess`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getSupplyChainGraph: (): Promise<any> =>
    fetchJson<any>(`${API_BASE}/graph/supply-chain`),

  explainSupplierRisk: (vendorId: string): Promise<any> =>
    fetchJson<any>(`${API_BASE}/vendors/${vendorId}/explain`),
};



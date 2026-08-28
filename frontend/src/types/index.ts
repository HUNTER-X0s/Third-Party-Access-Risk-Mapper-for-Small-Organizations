export type SeverityLevel = 'Critical' | 'High' | 'Medium' | 'Low' | 'Info';

export interface Vendor {
  id: string;
  name: string;
  website?: string;
  soc2_status: string;
  iso27001_certified: boolean;
  known_breach_history: boolean;
  trust_score: number;
}

export interface Application {
  id: string;
  canonical_name: string;
  category: string;
  provider_type: string;
  description?: string;
  vendor?: Vendor;
}

export interface ApplicationInstance {
  id: string;
  organization_id: string;
  display_name: string;
  status: 'active' | 'dormant' | 'shadow' | 'revoked';
  authorized_by_email: string;
  authorized_at: string;
  last_activity_at: string;
  is_shadow: boolean;
  approved_by_admin: boolean;
  risk_score: number;
  risk_severity: SeverityLevel;
  technical_risk_score: number;
  data_exposure_risk_score: number;
  business_impact_risk_score: number;
  vendor_risk_score: number;
  attack_path_risk_score: number;
  application: Application;
}

export interface Permission {
  id: string;
  canonical_name: string;
  display_name: string;
  description?: string;
  category: string;
  severity_level: SeverityLevel;
}

export interface ProviderConnector {
  id: string;
  provider: 'GITHUB' | 'GOOGLE_WORKSPACE' | 'MS365' | 'SLACK' | string;
  display_name: string;
  mode: 'LIVE' | 'DEMO';
  status: 'HEALTHY' | 'DEGRADED' | 'STALE' | 'AUTH_FAILED' | 'RATE_LIMITED' | 'UNAVAILABLE' | 'MISCONFIGURED';
  last_sync_at?: string;
  last_error?: string;
  apps_discovered: number;
  permissions_discovered: number;
  data_freshness_seconds?: number;
  config: Record<string, any>;
}

export interface ConnectorHealth {
  connector_id: string;
  provider: string;
  mode: string;
  status: string;
  last_sync_at?: string;
  last_attempted_sync_at?: string;
  last_error?: string;
  apps_discovered: number;
  permissions_discovered: number;
  data_freshness_seconds?: number;
  stale_threshold_seconds: number;
  is_stale: boolean;
}

export interface SyncRunResponse {
  id: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  records_collected: number;
  records_normalized: number;
  findings_created: number;
  snapshot_id?: string;
  error_message?: string;
}

export interface PermissionGrant {
  id: string;
  application_instance_id: string;
  raw_scope: string;
  granted_at: string;
  is_excess: boolean;
  excess_reason?: string;
  permission: Permission;
}

export interface DataClassification {
  id: string;
  name: string;
  display_name: string;
  sensitivity_level: number;
  color_code: string;
}

export interface DataAsset {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  system_of_record: string;
  is_crown_jewel: boolean;
  owner_email?: string;
  classification: DataClassification;
}

export interface AccessRelationship {
  id: string;
  application_instance_id: string;
  data_asset_id: string;
  access_type: string;
  is_direct: boolean;
  last_verified_at: string;
  data_asset: DataAsset;
}

export interface RiskFactor {
  id: string;
  name: string;
  category: string;
  weight: number;
  current_value: number;
  normalized_value: number;
  explanation: string;
}

export interface Remediation {
  id: string;
  finding_id: string;
  action_type: string;
  title: string;
  description: string;
  current_state: string;
  target_state: string;
  estimated_risk_reduction: number;
  simulated_target_score: number;
  priority: SeverityLevel;
  effort_level: string;
  is_simulation: boolean;
  status: string;
}

export interface RiskFinding {
  id: string;
  organization_id: string;
  application_instance_id: string;
  finding_type: string;
  title: string;
  description: string;
  severity: SeverityLevel;
  risk_score_contribution: number;
  risk_engine_version: string;
  lifecycle_state: string;
  confidence: string;
  affected_application_name: string;
  affected_data_name?: string;
  business_impact?: string;
  created_at: string;
  factors: RiskFactor[];
  remediations: Remediation[];
}

export interface DashboardSummary {
  organization_name: string;
  security_posture_score: number;
  total_applications: number;
  active_applications: number;
  shadow_applications: number;
  dormant_applications: number;
  critical_findings_count: number;
  high_findings_count: number;
  total_excess_permissions: number;
  sensitive_data_assets_count: number;
  data_freshness_status: string;
  risk_distribution: Record<string, number>;
  top_findings: RiskFinding[];
  applications: ApplicationInstance[];
}

export interface SimulationResponse {
  is_simulation: boolean;
  mode_label: string;
  current_score: number;
  current_severity: SeverityLevel;
  simulated_score: number;
  simulated_severity: SeverityLevel;
  risk_reduction_delta: number;
  percentage_reduction: number;
  revoked_scopes_count: number;
  simulated_result: any;
}

export interface RawEvidence {
  id: string;
  organization_id: string;
  payload_hash_sha256: string;
  raw_payload_json: any;
  collected_at: string;
  data_freshness_status: string;
}

export interface AccessGraphData {
  organization: string;
  nodes: any[];
  edges: any[];
}

// --- PHASE 2 TYPES ---

export interface PathNode {
  id: string;
  type: 'APP' | 'PERMISSION' | 'DATA_ASSET' | 'BUSINESS_PROCESS' | 'DEPARTMENT';
  name: string;
  severity?: SeverityLevel;
  is_excess?: boolean;
  is_crown_jewel?: boolean;
  sensitivity?: number;
  criticality?: number;
}

export interface PathContributor {
  name: string;
  delta: number;
}

export interface PotentialAttackPath {
  path_id: string;
  entry_application: string;
  entry_app_id: string;
  target_data_asset: string;
  target_data_id: string;
  is_crown_jewel_targeted: boolean;
  business_process_impacted: string;
  path_nodes: PathNode[];
  path_risk_score: number;
  contributors: PathContributor[];
  confidence_percentage: number;
  evidence_coverage: string;
  verification_state: 'VERIFIED' | 'PARTIALLY VERIFIED' | 'INFERRED';
}

export interface BlastRadiusFactor {
  name: string;
  delta: number;
}

export interface ApplicationBlastRadius {
  application_id: string;
  application_name: string;
  blast_radius_score: number;
  score_severity: SeverityLevel;
  affected_data_assets_count: number;
  affected_crown_jewels_count: number;
  affected_business_processes_count: number;
  affected_users_count: number;
  affected_departments_count: number;
  reachable_assets: any[];
  affected_processes: any[];
  factors: BlastRadiusFactor[];
}

export interface SecuritySnapshot {
  id: string;
  organization_id: string;
  created_at: string;
  snapshot_label: string;
  trigger_reason: string;
  security_posture_score: number;
  total_applications: number;
  critical_findings_count: number;
  high_findings_count: number;
  excess_permissions_count: number;
  crown_jewels_exposed_count: number;
  risk_engine_version: string;
}

export interface RiskChangeItem {
  category: string;
  change_type: 'ADDED' | 'REMOVED' | 'MODIFIED';
  description: string;
  risk_score_delta: number;
}

export interface SnapshotComparison {
  snapshot_a_id: string;
  snapshot_b_id: string;
  snapshot_a_label: string;
  snapshot_b_label: string;
  date_a: string;
  date_b: string;
  score_a: number;
  score_b: number;
  score_delta: number;
  direction: 'ESCALATED' | 'IMPROVED' | 'UNCHANGED';
  primary_causes: RiskChangeItem[];
  new_critical_findings: string[];
  resolved_critical_findings: string[];
  new_attack_paths_count: number;
  removed_attack_paths_count: number;
  crown_jewel_exposure_changed: boolean;
}

export interface RemediationAnalysis {
  finding_id: string;
  application_name: string;
  target_threshold_score: number;
  current_score: number;
  recommended_minimal_revocations: string[];
  recommended_candidate_name: string;
  predicted_residual_score: number;
  predicted_severity: SeverityLevel;
  risk_reduction_delta: number;
  attack_paths_before: number;
  attack_paths_after: number;
  blast_radius_before: number;
  blast_radius_after: number;
  is_simulation: boolean;
  simulation_warning: string;
  candidates_evaluated: any[];
}

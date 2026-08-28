from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    Organization, Vendor, Application, ApplicationInstance,
    Permission, ProviderScope, PermissionGrant,
    BusinessPurposeCatalog, BusinessPurposeRequirement, ApplicationInstancePurpose,
    DataClassification, DataAsset, AccessRelationship,
    EvidenceSource, RawEvidence, FindingEvidenceLink, SecurityFact,
    RiskFinding, RiskFactor, Remediation, AuditEvent,
    Department, BusinessProcess, SecuritySnapshot,
    User, OrganizationMembership
)
from app.models.vendor import SupplierProfile, SupplierDueDiligence, SupplierSubprocessor, SupplierAssessmentHistory
from app.services.scope_normalizer import normalize_scope
from app.services.evidence_engine import compute_payload_hash
from app.services.risk_engine import calculate_risk
from app.core.security import get_password_hash

def seed_database(db: Session) -> Organization:
    org = db.query(Organization).filter(Organization.domain == "anurag.tech").first()
    if not org:
        # 1. Organization
        org = Organization(
            name="Anurag Technologies",
            domain="anurag.tech",
            plan_tier="pro",
            security_posture_score=62.4
        )
        db.add(org)
        db.flush()

    # 1.0 Demo Users & Memberships
    if not db.query(User).filter(User.email == "admin@anurag.tech").first():
        default_pwd = get_password_hash("DemoPass123!")
        
        u_admin = User(organization_id=org.id, email="admin@anurag.tech", display_name="Pradyumna Biswal (SecOps)", password_hash=default_pwd, role="SECURITY_ADMIN", status="ACTIVE")
        u_audit = User(organization_id=org.id, email="auditor@anurag.tech", display_name="Simran Swain (Compliance)", password_hash=default_pwd, role="AUDITOR", status="ACTIVE")
        u_owner = User(organization_id=org.id, email="devops@anurag.tech", display_name="Anurag Swain (Engineering)", password_hash=default_pwd, role="APP_OWNER", status="ACTIVE")
        u_view = User(organization_id=org.id, email="viewer@anurag.tech", display_name="Subankar Swain (Auditor View)", password_hash=default_pwd, role="VIEWER", status="ACTIVE")
        u_super = User(organization_id=org.id, email="superadmin@anurag.tech", display_name="Jahanabi Dalai (Super Admin)", password_hash=default_pwd, role="SUPER_ADMIN", status="ACTIVE")

        db.add_all([u_admin, u_audit, u_owner, u_view, u_super])
        db.flush()

        # Memberships
        for u in [u_admin, u_audit, u_owner, u_view, u_super]:
            m = OrganizationMembership(user_id=u.id, organization_id=org.id, role=u.role, status="ACTIVE")
            db.add(m)
        db.flush()

    # 1.1 Departments & Business Processes
    if not db.query(Department).filter(Department.organization_id == org.id).first():
        dept_eng = Department(organization_id=org.id, name="Engineering", code="ENG", user_count=18, head_email="cto@anurag.tech")
        dept_ops = Department(organization_id=org.id, name="DevOps & Infrastructure", code="OPS", user_count=6, head_email="devops@anurag.tech")
        dept_fin = Department(organization_id=org.id, name="Finance & Ops", code="FIN", user_count=4, head_email="cfo@anurag.tech")
        db.add_all([dept_eng, dept_ops, dept_fin])
        db.flush()

    if not db.query(BusinessProcess).filter(BusinessProcess.organization_id == org.id).first():
        bp_delivery = BusinessProcess(organization_id=org.id, name="Software Delivery Process", code="PROC_DELIVERY", description="CI/CD deployment pipeline and source code deployment", criticality=5, owner_department="Engineering")
        bp_onboarding = BusinessProcess(organization_id=org.id, name="Customer Onboarding & Sync", code="PROC_ONBOARD", description="Customer registration and CRM lead integration", criticality=4, owner_department="Finance & Ops")
        bp_reporting = BusinessProcess(organization_id=org.id, name="Financial Reporting & Tax", code="PROC_FINANCE", description="Monthly payroll sync and tax filings", criticality=4, owner_department="Finance & Ops")
        db.add_all([bp_delivery, bp_onboarding, bp_reporting])
        db.flush()

    if db.query(PermissionGrant).join(ApplicationInstance).filter(ApplicationInstance.organization_id == org.id).count() > 0:
        db.commit()
        return org

    # 2. Vendors
    vendor_github = Vendor(name="GitHub Inc.", website="https://github.com", soc2_status="certified", iso27001_certified=True, trust_score=92.0)
    vendor_zapier = Vendor(name="Zapier Inc.", website="https://zapier.com", soc2_status="certified", iso27001_certified=True, trust_score=85.0)
    vendor_google = Vendor(name="Google LLC", website="https://workspace.google.com", soc2_status="certified", iso27001_certified=True, trust_score=98.0)
    vendor_slack = Vendor(name="Slack Technologies", website="https://slack.com", soc2_status="certified", iso27001_certified=True, trust_score=90.0)
    vendor_canva = Vendor(name="Canva Pty Ltd", website="https://canva.com", soc2_status="self_asserted", iso27001_certified=False, trust_score=72.0)
    db.add_all([vendor_github, vendor_zapier, vendor_google, vendor_slack, vendor_canva])
    db.flush()

    # 3. Catalog Applications
    app_gh = Application(canonical_name="github_cloud", category="Developer Tools", provider_type="github", vendor_id=vendor_github.id)
    app_zap = Application(canonical_name="zapier_automation", category="Workflow Automation", provider_type="zapier", vendor_id=vendor_zapier.id)
    app_gsuite = Application(canonical_name="google_workspace", category="Productivity & Email", provider_type="google", vendor_id=vendor_google.id)
    app_slack_c = Application(canonical_name="slack_workspace", category="Collaboration", provider_type="slack", vendor_id=vendor_slack.id)
    app_canva_c = Application(canonical_name="canva_design", category="Design", provider_type="canva", vendor_id=vendor_canva.id)
    db.add_all([app_gh, app_zap, app_gsuite, app_slack_c, app_canva_c])
    db.flush()

    # 4. Application Instances
    inst_gh = ApplicationInstance(
        organization_id=org.id, application_id=app_gh.id, display_name="GitHub Production Sync",
        status="active", authorized_by_email="devops@anurag.tech", is_shadow=False, approved_by_admin=True,
        risk_score=94.5, risk_severity="Critical", technical_risk_score=100.0, data_exposure_risk_score=100.0,
        business_impact_risk_score=90.0, vendor_risk_score=8.0, attack_path_risk_score=100.0
    )
    inst_zap = ApplicationInstance(
        organization_id=org.id, application_id=app_zap.id, display_name="Zapier Support Automation",
        status="active", authorized_by_email="intern@anurag.tech", is_shadow=True, approved_by_admin=False,
        risk_score=78.2, risk_severity="High", technical_risk_score=80.0, data_exposure_risk_score=85.0,
        business_impact_risk_score=75.0, vendor_risk_score=15.0, attack_path_risk_score=80.0
    )
    inst_gsuite = ApplicationInstance(
        organization_id=org.id, application_id=app_gsuite.id, display_name="Google Workspace Enterprise",
        status="active", authorized_by_email="admin@anurag.tech", is_shadow=False, approved_by_admin=True,
        risk_score=32.0, risk_severity="Low", technical_risk_score=30.0, data_exposure_risk_score=40.0,
        business_impact_risk_score=50.0, vendor_risk_score=2.0, attack_path_risk_score=10.0
    )
    inst_slack = ApplicationInstance(
        organization_id=org.id, application_id=app_slack_c.id, display_name="Slack HQ Workspace",
        status="active", authorized_by_email="hr@anurag.tech", is_shadow=False, approved_by_admin=True,
        risk_score=48.0, risk_severity="Medium", technical_risk_score=50.0, data_exposure_risk_score=45.0,
        business_impact_risk_score=50.0, vendor_risk_score=10.0, attack_path_risk_score=30.0
    )
    inst_canva = ApplicationInstance(
        organization_id=org.id, application_id=app_canva_c.id, display_name="Canva Marketing Team",
        status="dormant", authorized_by_email="marketing@anurag.tech", is_shadow=True, approved_by_admin=False,
        risk_score=58.5, risk_severity="Medium", technical_risk_score=60.0, data_exposure_risk_score=50.0,
        business_impact_risk_score=40.0, vendor_risk_score=28.0, attack_path_risk_score=40.0
    )
    inst_app6 = ApplicationInstance(organization_id=org.id, application_id=app_gh.id, display_name="GitHub Read-Only Mirror", status="active", authorized_by_email="lead@anurag.tech", is_shadow=False, approved_by_admin=True, risk_score=22.0, risk_severity="Low")
    inst_app7 = ApplicationInstance(organization_id=org.id, application_id=app_zap.id, display_name="Zapier Billing Sync", status="active", authorized_by_email="cfo@anurag.tech", is_shadow=False, approved_by_admin=True, risk_score=42.0, risk_severity="Medium")
    inst_app8 = ApplicationInstance(organization_id=org.id, application_id=app_slack_c.id, display_name="Slack Bot Notifications", status="active", authorized_by_email="devops@anurag.tech", is_shadow=False, approved_by_admin=True, risk_score=28.0, risk_severity="Low")
    
    db.add_all([inst_gh, inst_zap, inst_gsuite, inst_slack, inst_canva, inst_app6, inst_app7, inst_app8])
    db.flush()

    # 5. Permissions & Grants
    p_admin = Permission(canonical_name="ADMIN", display_name="Full Organization Admin", description="Complete administrative control over organization resources", category="Admin", severity_level="Critical")
    p_write = Permission(canonical_name="WRITE", display_name="Write & Modify Data", description="Modify and write system records", category="Data Access", severity_level="High")
    p_read = Permission(canonical_name="READ", display_name="Read-Only Access", description="Read system records", category="Data Access", severity_level="Low")
    p_export = Permission(canonical_name="EXPORT", display_name="Bulk Data Export", description="Export customer or sensitive records in bulk", category="Data Export", severity_level="High")
    db.add_all([p_admin, p_write, p_read, p_export])
    db.flush()

    g_gh_1 = PermissionGrant(application_instance_id=inst_gh.id, permission_id=p_read.id, raw_scope="repo_read", is_excess=False)
    g_gh_2 = PermissionGrant(application_instance_id=inst_gh.id, permission_id=p_write.id, raw_scope="repo_write", is_excess=True, excess_reason="Write access not required for CI read-only code scanning")
    g_gh_3 = PermissionGrant(application_instance_id=inst_gh.id, permission_id=p_admin.id, raw_scope="organization_admin", is_excess=True, excess_reason="Full organization admin scope is severely excessive for read-only CI sync")
    
    g_zap_1 = PermissionGrant(application_instance_id=inst_zap.id, permission_id=p_export.id, raw_scope="Customer.Export", is_excess=True, excess_reason="Unapproved shadow automation exporting customer PII database")
    g_zap_2 = PermissionGrant(application_instance_id=inst_zap.id, permission_id=p_write.id, raw_scope="Customer.Write", is_excess=True, excess_reason="Write scope beyond declared customer support purpose")
    db.add_all([g_gh_1, g_gh_2, g_gh_3, g_zap_1, g_zap_2])
    db.flush()

    # 6. Data Classification & Assets
    cls_cj = DataClassification(name="CROWN_JEWEL", display_name="Crown Jewel / Core IP", sensitivity_level=5, color_code="#ef4444")
    cls_pii = DataClassification(name="PII", display_name="Personally Identifiable Information", sensitivity_level=4, color_code="#f97316")
    cls_fin = DataClassification(name="FINANCIAL", display_name="Financial & Tax Records", sensitivity_level=5, color_code="#dc2626")
    cls_gen = DataClassification(name="GENERAL", display_name="General Internal Data", sensitivity_level=2, color_code="#3b82f6")
    db.add_all([cls_cj, cls_pii, cls_fin, cls_gen])
    db.flush()

    asset_source = DataAsset(organization_id=org.id, classification_id=cls_cj.id, name="Source Code & Prop Algorithms", system_of_record="GitHub", is_crown_jewel=True, owner_email="cto@anurag.tech")
    asset_pii = DataAsset(organization_id=org.id, classification_id=cls_pii.id, name="Customer PII Database", system_of_record="Google Drive / DB", is_crown_jewel=False, owner_email="dpo@anurag.tech")
    asset_payroll = DataAsset(organization_id=org.id, classification_id=cls_fin.id, name="Payroll & Tax Filings", system_of_record="Google Drive", is_crown_jewel=False, owner_email="cfo@anurag.tech")
    asset_design = DataAsset(organization_id=org.id, classification_id=cls_gen.id, name="Marketing Graphics & Collateral", system_of_record="Canva Cloud", is_crown_jewel=False, owner_email="marketing@anurag.tech")
    db.add_all([asset_source, asset_pii, asset_payroll, asset_design])
    db.flush()

    rel_gh = AccessRelationship(organization_id=org.id, application_instance_id=inst_gh.id, data_asset_id=asset_source.id, access_type="ADMIN", is_direct=True)
    rel_zap = AccessRelationship(organization_id=org.id, application_instance_id=inst_zap.id, data_asset_id=asset_pii.id, access_type="EXPORT", is_direct=True)
    rel_gsuite = AccessRelationship(organization_id=org.id, application_instance_id=inst_gsuite.id, data_asset_id=asset_payroll.id, access_type="READ", is_direct=True)
    db.add_all([rel_gh, rel_zap, rel_gsuite])
    db.flush()

    # 7. Evidence & Findings
    ev_src = EvidenceSource(organization_id=org.id, connector_type="DEMO_SEED", api_endpoint="https://admin.googleapis.com/admin/directory/v1/users", trust_level="HIGH")
    db.add(ev_src)
    db.flush()

    payload_gh = {"app": "GitHub Production Sync", "raw_scopes": ["organization_admin", "repo_write", "repo_read"], "authorized_by": "devops@anurag.tech"}
    h_gh = compute_payload_hash(payload_gh)
    raw_ev = RawEvidence(organization_id=org.id, evidence_source_id=ev_src.id, payload_hash_sha256=h_gh, raw_payload_json=payload_gh, data_freshness_status="CONFIRMED")
    db.add(raw_ev)
    db.flush()

    fact_gh = SecurityFact(organization_id=org.id, raw_evidence_id=raw_ev.id, fact_type="EXCESS_SCOPE_GRANTED", subject_entity="GitHub Production Sync", fact_details={"scope": "organization_admin", "severity": "Critical"})
    db.add(fact_gh)
    db.flush()

    finding_gh = RiskFinding(
        organization_id=org.id, application_instance_id=inst_gh.id, finding_type="EXCESS_PERMISSION",
        title="Excessive Organization Admin Privilege Granted to GitHub Sync",
        description="GitHub Production Sync has been granted 'organization_admin' scope which enables full administrative take-over of organization repositories and access to Crown Jewel Source Code.",
        severity="Critical", risk_score_contribution=45.0, risk_engine_version="v1.5.0", lifecycle_state="ACTIVE",
        affected_application_name="GitHub Production Sync", affected_data_name="Source Code & Prop Algorithms",
        business_impact="Critical vulnerability: A compromised GitHub OAuth token allows complete code exfiltration and supply chain tampering."
    )
    finding_zap = RiskFinding(
        organization_id=org.id, application_instance_id=inst_zap.id, finding_type="PURPOSE_MISMATCH",
        title="Unapproved Shadow Zapier Integration Exporting Customer PII",
        description="An unapproved Zapier integration authorized by an intern is actively exporting Customer PII database records without DPO approval.",
        severity="High", risk_score_contribution=35.0, risk_engine_version="v1.5.0", lifecycle_state="ACTIVE",
        affected_application_name="Zapier Support Automation", affected_data_name="Customer PII Database",
        business_impact="High privacy risk: Potential GDPR/DPDP violation from unauthorized external customer PII export."
    )
    db.add_all([finding_gh, finding_zap])
    db.flush()

    link_gh = FindingEvidenceLink(finding_id=finding_gh.id, raw_evidence_id=raw_ev.id, confidence_score=1.0)
    db.add(link_gh)

    f1 = RiskFactor(finding_id=finding_gh.id, name="Technical Risk & Scope Severity", category="Technical", weight=0.30, current_value=100.0, normalized_value=1.0, explanation="Critical scope 'organization_admin' grants full control")
    f2 = RiskFactor(finding_id=finding_gh.id, name="Data Exposure Sensitivity", category="Data", weight=0.25, current_value=100.0, normalized_value=1.0, explanation="Direct reachability to Crown Jewel Source Code")
    f3 = RiskFactor(finding_id=finding_gh.id, name="Attack Path Reachability", category="AttackPath", weight=0.15, current_value=100.0, normalized_value=1.0, explanation="External entry app directly connects to Crown Jewel")
    db.add_all([f1, f2, f3])

    rem_gh = Remediation(
        finding_id=finding_gh.id, action_type="REVOKE_EXCESS_SCOPE",
        title="Revoke 'organization_admin' and 'repo_write' Scopes",
        description="Downgrade GitHub Sync OAuth scopes to read-only 'repo_read' to eliminate full admin risk while preserving CI code scanning.",
        current_state="Granted: organization_admin, repo_write, repo_read", target_state="Granted: repo_read only",
        estimated_risk_reduction=46.4, simulated_target_score=53.6, priority="Critical", effort_level="Low", is_simulation=True
    )
    db.add(rem_gh)

    # Phase 7 Demo: Shadow SaaS application
    app_unknown_vendor = Vendor(name="AI Productivity Inc.", website="https://unknown-ai-tool.example", soc2_status="none", iso27001_certified=False, trust_score=15.0)
    db.add(app_unknown_vendor)
    db.flush()

    app_unknown = Application(
        canonical_name="unknown_ai_productivity_tool",
        category="AI Productivity",
        provider_type="oauth2",
        vendor_id=app_unknown_vendor.id,
        description="Unknown AI productivity tool discovered through connector observation."
    )
    db.add(app_unknown)
    db.flush()

    inst_shadow = ApplicationInstance(
        organization_id=org.id, application_id=app_unknown.id,
        display_name="Unknown AI Productivity Tool",
        status="active", authorized_by_email="unknown@anurag.tech",
        is_shadow=True, approved_by_admin=False,
        risk_score=78.0, risk_severity="High",
        technical_risk_score=80.0, data_exposure_risk_score=90.0,
        business_impact_risk_score=70.0, vendor_risk_score=85.0, attack_path_risk_score=60.0
    )
    db.add(inst_shadow)
    db.flush()

    g_shadow_export = PermissionGrant(
        application_instance_id=inst_shadow.id, permission_id=p_export.id,
        raw_scope="data_export_all", is_excess=True,
        excess_reason="Unknown app exporting all organizational data without approval"
    )
    db.add(g_shadow_export)
    db.flush()

    rel_shadow = AccessRelationship(
        organization_id=org.id, application_instance_id=inst_shadow.id,
        data_asset_id=asset_pii.id, access_type="EXPORT", is_direct=True
    )
    db.add(rel_shadow)
    db.flush()

    finding_shadow = RiskFinding(
        organization_id=org.id, application_instance_id=inst_shadow.id, finding_type="SHADOW_SAAS",
        title="SHADOW SaaS: Unapproved AI Tool Exporting Customer PII",
        description="An unapproved AI productivity tool was discovered accessing and exporting Customer PII data without security review or DPO approval.",
        severity="High", risk_score_contribution=40.0, risk_engine_version="v1.5.0", lifecycle_state="ACTIVE",
        affected_application_name="Unknown AI Productivity Tool", affected_data_name="Customer PII Database",
        business_impact="Unauthorized external data processor risk, potential GDPR violation."
    )
    db.add(finding_shadow)

    # 8. Phase 7: Application Baselines (Approved vs Observed)
    from app.models.monitoring import ApplicationBaseline, SecurityChange, SecurityIncident
    from datetime import timezone

    if not db.query(ApplicationBaseline).filter(ApplicationBaseline.organization_id == org.id).first():
        baseline_gh = ApplicationBaseline(
            organization_id=org.id, application_instance_id=inst_gh.id,
            approved_permissions=["READ"], approved_data_categories=["SOURCE_CODE"],
            is_approved=True, approval_status="APPROVED",
            first_seen_at=datetime.utcnow() - timedelta(days=90),
            last_seen_at=datetime.utcnow()
        )
        baseline_gsuite = ApplicationBaseline(
            organization_id=org.id, application_instance_id=inst_gsuite.id,
            approved_permissions=["READ", "WRITE"], approved_data_categories=["PAYROLL", "EMAIL"],
            is_approved=True, approval_status="APPROVED",
            first_seen_at=datetime.utcnow() - timedelta(days=60),
            last_seen_at=datetime.utcnow()
        )
        baseline_slack = ApplicationBaseline(
            organization_id=org.id, application_instance_id=inst_slack.id,
            approved_permissions=["READ", "WRITE"], approved_data_categories=["COMMUNICATIONS"],
            is_approved=True, approval_status="APPROVED",
            first_seen_at=datetime.utcnow() - timedelta(days=45),
            last_seen_at=datetime.utcnow()
        )
        # Unapproved apps — for Shadow SaaS detection
        baseline_zap = ApplicationBaseline(
            organization_id=org.id, application_instance_id=inst_zap.id,
            approved_permissions=[], approved_data_categories=[],
            is_approved=False, approval_status="REVIEW_REQUIRED",
            first_seen_at=datetime.utcnow() - timedelta(days=14),
            last_seen_at=datetime.utcnow()
        )
        baseline_shadow = ApplicationBaseline(
            organization_id=org.id, application_instance_id=inst_shadow.id,
            approved_permissions=[], approved_data_categories=[],
            is_approved=False, approval_status="REVIEW_REQUIRED",
            first_seen_at=datetime.utcnow() - timedelta(days=2),
            last_seen_at=datetime.utcnow()
        )
        db.add_all([baseline_gh, baseline_gsuite, baseline_slack, baseline_zap, baseline_shadow])
        db.flush()

    # 8.5 Phase 7: Historical Security Snapshots
    if not db.query(SecuritySnapshot).filter(SecuritySnapshot.organization_id == org.id).first():
        snap_baseline = SecuritySnapshot(
            organization_id=org.id,
            created_at=datetime.utcnow() - timedelta(days=30),
            snapshot_label="Baseline Initial Security Audit",
            trigger_reason="MONTHLY_AUDIT",
            security_posture_score=42.0,
            total_applications=6,
            critical_findings_count=0,
            high_findings_count=1,
            excess_permissions_count=1,
            crown_jewels_exposed_count=0,
            risk_engine_version="v1.5.0",
            state_manifest_json={"excess_scopes": ["Customer.Export"]}
        )
        snap_current = SecuritySnapshot(
            organization_id=org.id,
            created_at=datetime.utcnow(),
            snapshot_label="Current Posture (GitHub Admin Scope Added)",
            trigger_reason="ALERT_TRIGGERED",
            security_posture_score=62.4,
            total_applications=8,
            critical_findings_count=1,
            high_findings_count=1,
            excess_permissions_count=3,
            crown_jewels_exposed_count=1,
            risk_engine_version="v1.5.0",
            state_manifest_json={"excess_scopes": ["organization_admin", "repo_write", "Customer.Export"]}
        )
        db.add_all([snap_baseline, snap_current])
        db.flush()

    # 9. Phase 7: Demo Security Changes (Continuous Monitoring Scenario)
    if not db.query(SecurityChange).filter(SecurityChange.organization_id == org.id).first():
        snap_baseline_obj = db.query(SecuritySnapshot).filter(
            SecuritySnapshot.organization_id == org.id,
            SecuritySnapshot.snapshot_label == "Baseline Initial Security Audit"
        ).first()
        snap_current_obj = db.query(SecuritySnapshot).filter(
            SecuritySnapshot.organization_id == org.id,
            SecuritySnapshot.snapshot_label == "Current Posture (GitHub Admin Scope Added)"
        ).first()

        before_id = snap_baseline_obj.id if snap_baseline_obj else None
        after_id = snap_current_obj.id if snap_current_obj else None

        if after_id:
            chg1 = SecurityChange(
                organization_id=org.id,
                snapshot_before_id=before_id, snapshot_after_id=after_id,
                change_type="PERMISSION_ESCALATED", object_type="PERMISSION",
                object_id="organization_admin", object_name="organization_admin",
                source="CONNECTOR_SYNC", severity="Critical", confidence="VERIFIED",
                evidence_refs=["EV-101", "EV-217"],
                impact_summary="GitHub's access escalated from repo_read to include organization_admin. This creates a new potential path to the Source Code Crown Jewel and increases application risk from 42 to 94.5.",
                status="NEW",
                timestamp=datetime.utcnow() - timedelta(hours=3)
            )
            chg2 = SecurityChange(
                organization_id=org.id,
                snapshot_before_id=before_id, snapshot_after_id=after_id,
                change_type="CROWN_JEWEL_REACHABILITY_CREATED", object_type="DATA_ASSET",
                object_id="source_code_crown_jewel", object_name="Source Code & Prop Algorithms",
                source="CONNECTOR_SYNC", severity="Critical", confidence="VERIFIED",
                evidence_refs=["EV-217"],
                impact_summary="GitHub Production Sync gained direct administrative access to Source Code Crown Jewel via organization_admin scope.",
                status="NEW",
                timestamp=datetime.utcnow() - timedelta(hours=3)
            )
            chg3 = SecurityChange(
                organization_id=org.id,
                snapshot_before_id=before_id, snapshot_after_id=after_id,
                change_type="RISK_INCREASED", object_type="ORGANIZATION",
                object_id=org.id, object_name="Anurag Technologies",
                source="CONNECTOR_SYNC", severity="Critical", confidence="VERIFIED",
                evidence_refs=[],
                impact_summary="Organization risk score increased from 42.0 to 94.5 (+52.5). Primary causes: permission escalation +22, crown-jewel exposure +11, new attack path +7.",
                status="NEW",
                timestamp=datetime.utcnow() - timedelta(hours=3)
            )
            chg4 = SecurityChange(
                organization_id=org.id,
                snapshot_before_id=None, snapshot_after_id=after_id,
                change_type="SHADOW_SAAS_DETECTED", object_type="APPLICATION",
                object_id=inst_shadow.id, object_name="Unknown AI Productivity Tool",
                source="CONNECTOR_SYNC", severity="High", confidence="VERIFIED",
                evidence_refs=[],
                impact_summary="Unknown unapproved application 'Unknown AI Productivity Tool' detected accessing Customer PII data with EXPORT permission. Review required.",
                status="NEW",
                timestamp=datetime.utcnow() - timedelta(hours=1)
            )
            chg5 = SecurityChange(
                organization_id=org.id,
                snapshot_before_id=before_id, snapshot_after_id=after_id,
                change_type="PERMISSION_ESCALATED", object_type="PERMISSION",
                object_id="repo_write", object_name="repo_write",
                source="CONNECTOR_SYNC", severity="High", confidence="VERIFIED",
                evidence_refs=["EV-101", "EV-217"],
                impact_summary="GitHub access now includes repo_write permission which was not part of the approved READ-only baseline.",
                status="NEW",
                timestamp=datetime.utcnow() - timedelta(hours=3)
            )
            db.add_all([chg1, chg2, chg3, chg4, chg5])
            db.flush()

            # 10. Phase 7: Demo Security Incident (Correlated)
            if after_id and not db.query(SecurityIncident).filter(SecurityIncident.organization_id == org.id).first():
                incident = SecurityIncident(
                    organization_id=org.id,
                    detected_at=datetime.utcnow() - timedelta(hours=3),
                    source="CONNECTOR_SYNC",
                    severity="Critical",
                    summary="Critical permission escalation: GitHub gained organization-level admin access, creating a new potential attack path to the Source Code Crown Jewel. Risk increased from 42.0 to 94.5 (+52.5).",
                    change_ids=[chg1.id, chg2.id, chg3.id, chg5.id],
                    risk_before=42.0, risk_after=94.5, risk_delta=52.5,
                    blast_radius_before=42.0, blast_radius_after=75.0,
                    attack_paths_before=["GitHub → Source Code"],
                    attack_paths_after=["GitHub → ADMIN → Source Code Crown Jewel", "GitHub → All Repositories"],
                    status="OPEN",
                    evidence_refs=["EV-101", "EV-217"]
                )
                db.add(incident)
                db.flush()

            # 11. Phase 7.1: Demo Security Notifications
            from app.models.monitoring import SecurityNotification
            from app.services.notification_engine import generate_notification_fingerprint

            if not db.query(SecurityNotification).filter(SecurityNotification.organization_id == org.id).first():
                fp1 = generate_notification_fingerprint(org.id, "CRITICAL_PERMISSION_ESCALATION", chg1.id)
                fp2 = generate_notification_fingerprint(org.id, "NEW_CROWN_JEWEL_REACHABILITY", chg2.id)
                fp3 = generate_notification_fingerprint(org.id, "HIGH_SHADOW_SAAS", chg4.id)

                n1 = SecurityNotification(
                    organization_id=org.id,
                    title="Critical Alert: Permission Escalated",
                    body="GitHub access escalated from repo_read to include organization_admin. High privilege elevation.",
                    severity="Critical",
                    notification_type="CRITICAL_PERMISSION_ESCALATION",
                    source_type="CHANGE",
                    source_id=chg1.id,
                    fingerprint=fp1,
                    is_read=False,
                    created_at=datetime.utcnow() - timedelta(hours=3)
                )
                n2 = SecurityNotification(
                    organization_id=org.id,
                    title="Critical Alert: Crown Jewel Reachability Created",
                    body="GitHub Production Sync gained direct administrative reachability to Source Code Crown Jewel.",
                    severity="Critical",
                    notification_type="NEW_CROWN_JEWEL_REACHABILITY",
                    source_type="CHANGE",
                    source_id=chg2.id,
                    fingerprint=fp2,
                    is_read=False,
                    created_at=datetime.utcnow() - timedelta(hours=3)
                )
                n3 = SecurityNotification(
                    organization_id=org.id,
                    title="High Alert: Shadow SaaS Detected",
                    body="Unknown unapproved application 'Unknown AI Productivity Tool' detected exporting Customer PII.",
                    severity="High",
                    notification_type="HIGH_SHADOW_SAAS",
                    source_type="CHANGE",
                    source_id=chg4.id,
                    fingerprint=fp3,
                    is_read=False,
                    created_at=datetime.utcnow() - timedelta(hours=1)
                )
                db.add_all([n1, n2, n3])

    # ---------------------------------------------------------------
    # PHASE 8: Supplier / Vendor Risk Profiles (NIST SP 1326 C-SCRM)
    # SYNTHETIC DEMO DATA — Clearly labeled per AGENTS.md Rule 13
    # ---------------------------------------------------------------
    _seed_supplier_profiles(db, org)

    db.commit()
    print("Database successfully seeded with Anurag Technologies Phase 8 demo dataset.")
    return org


def _seed_supplier_profiles(db: Session, org: Organization) -> None:
    """Seeds NIST SP 1326-aligned supplier profiles for the demo organization."""
    already_seeded = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org.id
    ).count()
    if already_seeded > 0:
        return

    vendors = db.query(Vendor).all()
    vendor_map = {v.name: v for v in vendors}

    SUPPLIER_CONFIGS = [
        {
            "vendor_name_contains": "GitHub",
            "criticality": "CRITICAL",
            "status": "APPROVED",
            "tier": 1,
            "supplier_risk_score": 20.0,
            "supplier_risk_severity": "Low",
            "assessment_status": "CURRENT",
            "owner": "ciso@anurag.tech",
            "reviewed_days_ago": 15,
            "next_review_days": 350,
            "foci_status": "ASSESSED_NO_CONCERN",
            "foci_details": "Microsoft subsidiary; US-domiciled; no foreign ownership concern identified.",
            "provenance_status": "ASSESSED",
            "origin_country": "United States",
            "ownership_country": "United States",
            "hosting": "Azure / US-East",
            "resilience_status": "CURRENT",
            "sla_pct": 99.9,
            "backup_tested": True,
            "bcp_dr": True,
            "cyber_status": "STRONG",
            "mfa": True,
            "vuln_mgmt": True,
            "ir_tested": True,
            "encryption": True,
            "security_email": "security@github.com",
            "evidence_refs": ["EV-SG-001", "EV-SG-002", "EV-SOC2-GH-2024"],
            "notes": "SOC 2 Type II current. Enterprise contract in place.",
            "subprocessors": [
                {"name": "Microsoft Azure", "service": "Cloud Hosting & CDN", "data_shared": ["Repository Data", "CI/CD Telemetry"], "region": "US", "verification": "VERIFIED", "tier": 2},
                {"name": "Fastly", "service": "Edge CDN", "data_shared": ["Static Assets"], "region": "Global", "verification": "DECLARED", "tier": 3}
            ]
        },
        {
            "vendor_name_contains": "Google",
            "criticality": "CRITICAL",
            "status": "APPROVED",
            "tier": 1,
            "supplier_risk_score": 18.0,
            "supplier_risk_severity": "Low",
            "assessment_status": "CURRENT",
            "owner": "ciso@anurag.tech",
            "reviewed_days_ago": 30,
            "next_review_days": 335,
            "foci_status": "ASSESSED_NO_CONCERN",
            "foci_details": "US-domiciled publicly traded entity. No FOCI concern.",
            "provenance_status": "ASSESSED",
            "origin_country": "United States",
            "ownership_country": "United States",
            "hosting": "Google Cloud / US-Central",
            "resilience_status": "CURRENT",
            "sla_pct": 99.95,
            "backup_tested": True,
            "bcp_dr": True,
            "cyber_status": "STRONG",
            "mfa": True,
            "vuln_mgmt": True,
            "ir_tested": True,
            "encryption": True,
            "security_email": "security@google.com",
            "evidence_refs": ["EV-SG-003", "EV-ISO27001-GWS-2024"],
            "notes": "ISO 27001 certified. DPA executed.",
            "subprocessors": [
                {"name": "Google Cloud Platform", "service": "Infrastructure", "data_shared": ["User Data", "Email Content"], "region": "US", "verification": "VERIFIED", "tier": 2}
            ]
        },
        {
            "vendor_name_contains": "Slack",
            "criticality": "HIGH",
            "status": "APPROVED",
            "tier": 1,
            "supplier_risk_score": 38.0,
            "supplier_risk_severity": "Medium",
            "assessment_status": "DUE_SOON",
            "owner": "it-admin@anurag.tech",
            "reviewed_days_ago": 320,
            "next_review_days": 45,
            "foci_status": "ASSESSED_NO_CONCERN",
            "foci_details": "Salesforce subsidiary since 2021. US-domiciled.",
            "provenance_status": "CLAIM",
            "origin_country": "United States",
            "ownership_country": "United States",
            "hosting": "AWS / US-East (Self-Declared)",
            "resilience_status": "ASSESSED",
            "sla_pct": 99.99,
            "backup_tested": False,
            "bcp_dr": True,
            "cyber_status": "PARTIAL",
            "mfa": True,
            "vuln_mgmt": False,
            "ir_tested": False,
            "encryption": True,
            "security_email": "security@slack.com",
            "evidence_refs": ["EV-SG-004"],
            "notes": "Pending refresh; SOC 2 renewal not yet received for 2024.",
            "subprocessors": [
                {"name": "Amazon Web Services", "service": "Cloud Hosting", "data_shared": ["Chat Messages", "File Attachments"], "region": "US", "verification": "DECLARED", "tier": 2},
                {"name": "Twilio", "service": "SMS/2FA Notifications", "data_shared": ["Phone Numbers"], "region": "US", "verification": "DECLARED", "tier": 3}
            ]
        },
        {
            "vendor_name_contains": "Zapier",
            "criticality": "HIGH",
            "status": "UNDER_REVIEW",
            "tier": 1,
            "supplier_risk_score": 62.0,
            "supplier_risk_severity": "High",
            "assessment_status": "OVERDUE",
            "owner": "it-admin@anurag.tech",
            "reviewed_days_ago": 420,
            "next_review_days": -55,
            "foci_status": "UNKNOWN",
            "foci_details": None,
            "provenance_status": "UNKNOWN",
            "origin_country": "United States",
            "ownership_country": "United States",
            "hosting": "Unknown Cloud Provider",
            "resilience_status": "UNKNOWN",
            "sla_pct": 99.5,
            "backup_tested": False,
            "bcp_dr": False,
            "cyber_status": "UNKNOWN",
            "mfa": False,
            "vuln_mgmt": False,
            "ir_tested": False,
            "encryption": True,
            "security_email": None,
            "evidence_refs": [],
            "notes": "Assessment overdue. Integration accesses multiple SaaS data streams. Priority P0 review required.",
            "subprocessors": []
        },
        {
            "vendor_name_contains": "AI Productivity",
            "criticality": "HIGH",
            "status": "RESTRICTED",
            "tier": 1,
            "supplier_risk_score": 85.0,
            "supplier_risk_severity": "Critical",
            "assessment_status": "STALE",
            "owner": "ciso@anurag.tech",
            "reviewed_days_ago": 550,
            "next_review_days": -185,
            "foci_status": "POTENTIAL_CONCERN",
            "foci_details": "Partial foreign ownership structure. Investment trail includes entity from high-risk jurisdiction. Requires legal counsel review.",
            "provenance_status": "DISPUTED",
            "origin_country": "Cayman Islands",
            "ownership_country": "Multiple / Disputed",
            "hosting": "Unknown / Unverified",
            "resilience_status": "GAP",
            "sla_pct": 95.0,
            "backup_tested": False,
            "bcp_dr": False,
            "cyber_status": "MINIMAL",
            "mfa": False,
            "vuln_mgmt": False,
            "ir_tested": False,
            "encryption": False,
            "security_email": None,
            "evidence_refs": ["EV-SHADOW-001"],
            "notes": "SHADOW SAAS — ACCESS RESTRICTED. FOCI POTENTIAL CONCERN. Investigation ongoing. Do not approve new integrations.",
            "subprocessors": []
        }
    ]

    for config in SUPPLIER_CONFIGS:
        # Find matching vendor by name fragment
        matched_vendor = None
        for vname, v in vendor_map.items():
            if config["vendor_name_contains"].lower() in vname.lower():
                matched_vendor = v
                break
        if not matched_vendor:
            continue

        now = datetime.utcnow()
        reviewed_at = now - timedelta(days=config["reviewed_days_ago"])
        next_review = now + timedelta(days=config["next_review_days"])

        profile = SupplierProfile(
            organization_id=org.id,
            vendor_id=matched_vendor.id,
            status=config["status"],
            business_criticality=config["criticality"],
            service_category="SaaS Platform",
            primary_business_owner=config["owner"],
            security_owner="ciso@anurag.tech",
            supplier_risk_score=config["supplier_risk_score"],
            supplier_risk_severity=config["supplier_risk_severity"],
            supply_chain_tier=config["tier"],
            assessment_status=config["assessment_status"],
            last_reviewed_at=reviewed_at,
            next_review_due=next_review,
            first_seen_at=now - timedelta(days=730)
        )
        db.add(profile)
        db.flush()

        dd = SupplierDueDiligence(
            supplier_profile_id=profile.id,
            foci_status=config["foci_status"],
            foci_details=config["foci_details"],
            provenance_status=config["provenance_status"],
            service_origin_country=config["origin_country"],
            ownership_country=config["ownership_country"],
            hosting_provider=config["hosting"],
            resilience_status=config["resilience_status"],
            sla_availability_pct=config["sla_pct"],
            backup_recovery_tested=config["backup_tested"],
            bcp_dr_documented=config["bcp_dr"],
            cyber_practices_status=config["cyber_status"],
            mfa_enforced=config["mfa"],
            vuln_mgmt_documented=config["vuln_mgmt"],
            incident_response_tested=config["ir_tested"],
            encryption_in_transit_rest=config["encryption"],
            security_contact_email=config["security_email"],
            evidence_refs=config["evidence_refs"],
            notes=config["notes"],
            supply_chain_tier=config["tier"],
            version=1,
            is_synthetic_demo=True,
            last_verified_at=reviewed_at,
            reviewed_by="SEED:demo-analyst@anurag.tech"
        )
        db.add(dd)

        # Seed initial assessment history record
        hist = SupplierAssessmentHistory(
            supplier_profile_id=profile.id,
            version=1,
            assessment_snapshot_json={
                "foci_status": config["foci_status"],
                "provenance_status": config["provenance_status"],
                "resilience_status": config["resilience_status"],
                "cyber_practices_status": config["cyber_status"],
                "supplier_risk_score": config["supplier_risk_score"]
            },
            change_summary="Initial C-SCRM due diligence seed record (synthetic demo).",
            reviewed_by="SEED:demo-analyst@anurag.tech"
        )
        db.add(hist)

        # Seed subprocessors
        for sub in config.get("subprocessors", []):
            sp = SupplierSubprocessor(
                supplier_profile_id=profile.id,
                subprocessor_name=sub["name"],
                service_provided=sub["service"],
                data_shared_categories=sub["data_shared"],
                hosting_region=sub["region"],
                verification_status=sub["verification"],
                tier=sub["tier"],
                evidence_refs=[]
            )
            db.add(sp)

    db.flush()
    db.commit()
    print(f"Phase 8 C-SCRM supplier profiles seeded for org {org.name} (SYNTHETIC DEMO).")
    return org

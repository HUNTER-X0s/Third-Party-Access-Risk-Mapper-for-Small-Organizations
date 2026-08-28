import React, { useEffect, useState, lazy, Suspense } from 'react';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { LoginPage } from '../pages/LoginPage';
import { Navbar } from '../components/Navbar';
import { Sidebar, TabType } from '../components/Sidebar';
import { DashboardPage } from '../pages/DashboardPage';
import { ApplicationsPage } from '../pages/ApplicationsPage';
import { FindingsPage } from '../pages/FindingsPage';
import { ApplicationDrawer } from '../components/ApplicationDrawer';
import { FindingDrawer } from '../components/FindingDrawer';
import { ExecutiveReportModal } from '../components/ExecutiveReportModal';
import { UserManagementModal } from '../components/UserManagementModal';
import { AIAnalystDrawer } from '../components/AIAnalystDrawer';
import { api } from '../services/api';
import { DashboardSummary, ApplicationInstance, RiskFinding } from '../types';
import { Database, ShieldCheck, Check, Loader2 } from 'lucide-react';

// Heavy pages — lazy loaded so initial bundle stays small
const AccessGraphView = lazy(() =>
  import('../components/AccessGraphView').then(m => ({ default: m.AccessGraphView }))
);
const MonitoringPage = lazy(() => import('../pages/MonitoringPage'));
const VendorsPage = lazy(() =>
  import('../pages/VendorsPage').then(m => ({ default: m.VendorsPage }))
);
const ConnectorsPage = lazy(() =>
  import('../pages/ConnectorsPage').then(m => ({ default: m.ConnectorsPage }))
);

// Lightweight inline loading skeleton for lazy-loaded pages
const PageLoader: React.FC = () => (
  <div className="flex items-center justify-center h-64 text-slate-400">
    <Loader2 className="w-5 h-5 animate-spin mr-2" />
    <span className="text-xs font-medium">Loading...</span>
  </div>
);

const MainLayout: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [selectedApp, setSelectedApp] = useState<ApplicationInstance | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<RiskFinding | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [reportData, setReportData] = useState<any | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [aiAnalystConfig, setAiAnalystConfig] = useState<{
    isOpen: boolean;
    question?: string;
    contextType?: string;
    entityId?: string;
    entityName?: string;
  }>({ isOpen: false });
  const [resetNotification, setResetNotification] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    api.getDashboard().then(data => {
      setSummary(data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  };

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  if (authLoading) {
    return (
      <div className="h-screen w-screen bg-[#F8F9FB] flex items-center justify-center text-xs text-slate-500 font-medium">
        Verifying Security Session...
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  const handleResetDemo = async () => {
    if (window.confirm("Reset AccessGuard demo database to canonical Anurag Technologies dataset?")) {
      try {
        const res = await api.resetDemo();
        setResetNotification(res.message || "Demo dataset successfully reset!");
        loadData();
        setTimeout(() => setResetNotification(null), 4000);
      } catch (err: any) {
        alert("Failed to reset demo: " + err.message);
      }
    }
  };

  const handleExportReport = async () => {
    try {
      const data = await api.getExecutiveReport();
      setReportData(data);
    } catch (err: any) {
      alert("Failed to generate report: " + err.message);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#F8F9FB] text-slate-900 overflow-hidden font-sans relative">
      {/* Toast Notification */}
      {resetNotification && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-emerald-50 text-emerald-800 border border-emerald-200 px-4 py-2.5 rounded-lg shadow-lg text-xs z-50 flex items-center space-x-2 font-medium">
          <Check className="w-4 h-4 text-emerald-600" />
          <span>{resetNotification}</span>
        </div>
      )}

      <Navbar
        organizationName={summary?.organization_name || user.organization_name || 'Anurag Technologies'}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onResetDemo={handleResetDemo}
        onExportReport={handleExportReport}
        onOpenUserManagement={() => setShowUserModal(true)}
        onOpenAIAnalyst={() => setAiAnalystConfig({ isOpen: true, contextType: 'GENERAL' })}
        onNavigate={(tab) => setActiveTab(tab as TabType)}
        onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        isMobileMenuOpen={isMobileMenuOpen}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          appsCount={summary?.total_applications || 8}
          findingsCount={summary?.top_findings.length || 2}
          mobileOpen={isMobileMenuOpen}
          onCloseMobile={() => setIsMobileMenuOpen(false)}
        />

        <main className={`flex-1 overflow-y-auto bg-[#F8F9FB] ${activeTab === 'graph' ? 'p-0 flex flex-col' : 'p-3 sm:p-4 md:p-6'}`}>
          {activeTab === 'dashboard' && (
            <DashboardPage
              summary={summary}
              searchQuery={searchQuery}
              onSelectApplication={(app) => setSelectedApp(app)}
              onSelectFinding={(f) => setSelectedFinding(f)}
            />
          )}

          {activeTab === 'applications' && (
            <ApplicationsPage
              applications={(summary?.applications || []).filter(a =>
                !searchQuery || a.display_name.toLowerCase().includes(searchQuery.toLowerCase()) || (a.application.vendor?.name || '').toLowerCase().includes(searchQuery.toLowerCase())
              )}
              onSelectApplication={(app) => setSelectedApp(app)}
            />
          )}

          {activeTab === 'graph' && (
            <div className="flex-1 h-full min-h-0 p-3 sm:p-4">
              <Suspense fallback={<PageLoader />}>
                <AccessGraphView />
              </Suspense>
            </div>
          )}

          {activeTab === 'findings' && (
            <FindingsPage
              findings={(summary?.top_findings || []).filter(f =>
                !searchQuery || f.title.toLowerCase().includes(searchQuery.toLowerCase()) || f.affected_application_name.toLowerCase().includes(searchQuery.toLowerCase())
              )}
              onSelectFinding={(f) => setSelectedFinding(f)}
            />
          )}

          {activeTab === 'connectors' && (
            <Suspense fallback={<PageLoader />}>
              <ConnectorsPage />
            </Suspense>
          )}

          {activeTab === 'monitoring' && (
            <Suspense fallback={<PageLoader />}>
              <MonitoringPage onNavigate={(tab) => setActiveTab(tab as TabType)} />
            </Suspense>
          )}

          {activeTab === 'vendors' && (
            <Suspense fallback={<PageLoader />}>
              <VendorsPage />
            </Suspense>
          )}

          {activeTab === 'data' && (
            <div className="max-w-4xl mx-auto space-y-5 sm:space-y-6">
              <div>
                <h1 className="text-xl font-bold text-slate-900">Organizational Data Assets</h1>
                <p className="text-xs text-slate-500 mt-1">Classified systems of record tracked for third-party OAuth scope reachability and crown jewel exposure.</p>
              </div>

              <div className="bg-white border border-slate-200 rounded-lg shadow-sm divide-y divide-slate-100 overflow-hidden">
                <div className="p-3.5 sm:p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-slate-50/50 transition-colors">
                  <div className="flex items-center space-x-3 sm:space-x-3.5">
                    <div className="w-9 h-9 rounded-lg bg-red-50 border border-red-100 flex items-center justify-center text-red-600 font-bold flex-shrink-0">
                      👑
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 text-sm">Source Code & Proprietary Algorithms</div>
                      <div className="text-xs text-slate-500 mt-0.5">System of Record: GitHub Organization | Owner: <span className="font-mono text-slate-600">cto@anurag.tech</span></div>
                    </div>
                  </div>
                  <span className="self-start sm:self-auto bg-red-50 text-red-700 border border-red-200 text-xs px-2.5 py-1 rounded-md font-medium">
                    Crown Jewel · Level 5
                  </span>
                </div>

                <div className="p-3.5 sm:p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-slate-50/50 transition-colors">
                  <div className="flex items-center space-x-3 sm:space-x-3.5">
                    <div className="w-9 h-9 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">
                      <Database className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 text-sm">Customer PII Database</div>
                      <div className="text-xs text-slate-500 mt-0.5">System of Record: Google Drive / PostgreSQL | Owner: <span className="font-mono text-slate-600">dpo@anurag.tech</span></div>
                    </div>
                  </div>
                  <span className="self-start sm:self-auto bg-amber-50 text-amber-700 border border-amber-200 text-xs px-2.5 py-1 rounded-md font-medium">
                    Confidential PII · Level 4
                  </span>
                </div>

                <div className="p-3.5 sm:p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-slate-50/50 transition-colors">
                  <div className="flex items-center space-x-3 sm:space-x-3.5">
                    <div className="w-9 h-9 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">
                      <ShieldCheck className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 text-sm">Payroll & Tax Filings</div>
                      <div className="text-xs text-slate-500 mt-0.5">System of Record: Google Drive Finance Folder | Owner: <span className="font-mono text-slate-600">cfo@anurag.tech</span></div>
                    </div>
                  </div>
                  <span className="self-start sm:self-auto bg-amber-50 text-amber-700 border border-amber-200 text-xs px-2.5 py-1 rounded-md font-medium">
                    Financial · Level 5
                  </span>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Split-Pane Drawers */}
      <ApplicationDrawer
        application={selectedApp}
        onClose={() => setSelectedApp(null)}
        onSelectFinding={(f) => {
          setSelectedApp(null);
          setSelectedFinding(f);
        }}
      />

      <FindingDrawer
        finding={selectedFinding}
        onClose={() => setSelectedFinding(null)}
      />

      {/* Executive Report Modal */}
      {reportData && (
        <ExecutiveReportModal
          reportData={reportData}
          onClose={() => setReportData(null)}
        />
      )}

      {/* User Management Modal */}
      {showUserModal && (
        <UserManagementModal
          onClose={() => setShowUserModal(false)}
        />
      )}

      {/* AI Security Analyst Drawer */}
      <AIAnalystDrawer
        isOpen={aiAnalystConfig.isOpen}
        onClose={() => setAiAnalystConfig({ isOpen: false })}
        initialQuestion={aiAnalystConfig.question}
        contextType={aiAnalystConfig.contextType}
        entityId={aiAnalystConfig.entityId}
        entityName={aiAnalystConfig.entityName}
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
};

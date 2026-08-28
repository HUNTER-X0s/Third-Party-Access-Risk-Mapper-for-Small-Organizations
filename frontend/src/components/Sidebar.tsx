import React from 'react';
import { LayoutDashboard, Box, Network, AlertTriangle, Database, Link2, Activity, Building2, X } from 'lucide-react';

export type TabType = 'dashboard' | 'applications' | 'graph' | 'findings' | 'data' | 'connectors' | 'monitoring' | 'vendors';

interface SidebarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  appsCount: number;
  findingsCount: number;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  appsCount,
  findingsCount,
  mobileOpen = false,
  onCloseMobile
}) => {
  const groups = [
    {
      title: 'SECURITY',
      items: [
        { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
        { id: 'applications', label: 'Applications', icon: Box, count: appsCount },
        { id: 'findings', label: 'Findings', icon: AlertTriangle, count: findingsCount, alert: findingsCount > 0 },
      ],
    },
    {
      title: 'INTELLIGENCE',
      items: [
        { id: 'graph', label: 'Access Map', icon: Network },
        { id: 'monitoring', label: 'Monitoring', icon: Activity },
        { id: 'vendors', label: 'Suppliers & C-SCRM', icon: Building2 },
      ],
    },
    {
      title: 'GOVERNANCE',
      items: [
        { id: 'data', label: 'Data Assets', icon: Database },
        { id: 'connectors', label: 'Connectors', icon: Link2 },
      ],
    },
  ];

  const handleTabClick = (tabId: TabType) => {
    setActiveTab(tabId);
    if (onCloseMobile) {
      onCloseMobile();
    }
  };

  const navContent = (
    <div className="flex flex-col h-full justify-between py-4 px-3 text-xs select-none">
      <div className="space-y-5 flex-1">
        {mobileOpen && (
          <div className="flex items-center justify-between pb-2 border-b border-slate-100 md:hidden">
            <span className="font-bold text-slate-900 text-sm">Navigation Menu</span>
            <button
              onClick={onCloseMobile}
              className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {groups.map((group) => (
          <div key={group.title} className="space-y-1">
            <div className="text-[10px] font-semibold text-slate-400 uppercase px-2.5 mb-1.5 tracking-wider">
              {group.title}
            </div>
            <nav className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleTabClick(item.id as TabType)}
                    className={`w-full flex items-center justify-between px-2.5 py-2 rounded-md text-left transition-colors cursor-pointer text-[13px] ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 font-semibold'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-normal'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.count !== undefined && (
                      <span
                        className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${
                          item.alert
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {item.count}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      <div className="mt-auto border-t border-slate-100 pt-3.5 px-2 text-[11px] text-slate-400 space-y-1">
        <div className="flex justify-between">
          <span>Risk Engine</span>
          <span className="font-mono text-slate-600 font-medium">v1.5.0</span>
        </div>
        <div className="flex justify-between">
          <span>Tenant Scope</span>
          <span className="text-emerald-700 font-medium">Isolated</span>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden md:flex w-56 lg:w-60 bg-white border-r border-slate-200 flex-col min-h-[calc(100vh-3.5rem)] flex-shrink-0">
        {navContent}
      </aside>

      {/* Mobile Slide-Over Drawer & Backdrop */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
            onClick={onCloseMobile}
          />
          <div className="relative w-64 max-w-[80vw] bg-white h-full shadow-2xl flex flex-col z-10 animate-in slide-in-from-left duration-200">
            {navContent}
          </div>
        </div>
      )}
    </>
  );
};

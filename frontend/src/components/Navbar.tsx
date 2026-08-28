import React, { useState } from 'react';
import { Shield, Search, Building2, CheckCircle2, RotateCcw, FileText, Activity, User, LogOut, Users, Bot, Menu, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { NotificationCenter } from './NotificationCenter';

interface NavbarProps {
  organizationName: string;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onResetDemo: () => void;
  onExportReport: () => void;
  onOpenUserManagement: () => void;
  onOpenAIAnalyst?: () => void;
  onNavigate?: (tab: string, targetId?: string) => void;
  onToggleMobileMenu?: () => void;
  isMobileMenuOpen?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  organizationName,
  searchQuery,
  onSearchChange,
  onResetDemo,
  onExportReport,
  onOpenUserManagement,
  onOpenAIAnalyst,
  onNavigate,
  onToggleMobileMenu,
  isMobileMenuOpen,
}) => {
  const { user, logout } = useAuth();
  const [showHealthModal, setShowHealthModal] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const isUserAdmin = user?.role === 'SUPER_ADMIN' || user?.role === 'SECURITY_ADMIN';

  return (
    <header className="h-14 bg-white border-b border-slate-200 px-3 sm:px-5 flex items-center justify-between text-xs select-none sticky top-0 z-30 font-sans shadow-xs">
      
      {/* Left: Mobile Toggle & Brand Logo */}
      <div className="flex items-center space-x-2 sm:space-x-3.5">
        {/* Mobile Hamburger Toggle */}
        <button
          onClick={onToggleMobileMenu}
          className="p-1.5 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 md:hidden cursor-pointer"
          aria-label="Toggle navigation menu"
        >
          {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        <div className="flex items-center space-x-2 text-slate-900 font-semibold tracking-tight">
          <div className="bg-blue-600 text-white p-1.5 rounded-md shadow-xs flex-shrink-0">
            <Shield className="w-4 h-4" />
          </div>
          <span className="text-sm font-bold tracking-tight text-slate-900 hidden xs:inline sm:inline">
            Access<span className="text-blue-600 font-semibold">Guard</span>
          </span>
        </div>

        <div className="h-4 w-px bg-slate-200 hidden sm:block" />

        <div className="hidden lg:flex items-center space-x-1.5 text-slate-700 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200 text-[12px]">
          <Building2 className="w-3.5 h-3.5 text-slate-500" />
          <span className="font-medium max-w-[140px] truncate">{user?.organization_name || organizationName}</span>
        </div>
      </div>

      {/* Center: Responsive Search */}
      <div className="flex items-center space-x-2 sm:space-x-3 flex-1 max-w-xs sm:max-w-md mx-2 sm:mx-4">
        <div className="relative w-full">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search apps, scopes..."
            className="w-full bg-slate-50/80 border border-slate-200 rounded-md pl-8 pr-7 sm:pl-9 sm:pr-8 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600 text-[11px]"
            >
              ✕
            </button>
          )}
        </div>

        {/* System Health Status Indicator */}
        <button
          onClick={() => setShowHealthModal(!showHealthModal)}
          className="hidden md:flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100/70 px-2.5 py-1.5 rounded-md border border-emerald-200 text-[11px] font-medium transition-colors cursor-pointer flex-shrink-0"
          title="Click to view SecOps Engine Health"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="hidden lg:inline">System Healthy</span>
        </button>
      </div>

      {/* Right: Actions & User Menu */}
      <div className="flex items-center space-x-1.5 sm:space-x-2.5 flex-shrink-0">
        
        {/* In-App Notification Center */}
        <NotificationCenter onNavigate={onNavigate} />

        {onOpenAIAnalyst && (
          <button
            onClick={onOpenAIAnalyst}
            className="bg-blue-50 hover:bg-blue-100/80 text-blue-700 border border-blue-200 px-2 sm:px-2.5 py-1.5 rounded-md text-[12px] font-medium flex items-center space-x-1.5 transition-colors cursor-pointer"
            title="Open AI Security Analyst"
          >
            <Bot className="w-3.5 h-3.5 text-blue-600" />
            <span className="hidden sm:inline">Ask Analyst</span>
          </button>
        )}

        <button
          onClick={onExportReport}
          className="hidden sm:flex bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-2.5 py-1.5 rounded-md text-[12px] font-medium items-center space-x-1.5 transition-colors cursor-pointer shadow-xs"
          title="Generate Executive Report"
        >
          <FileText className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden md:inline">Report</span>
        </button>

        {isUserAdmin && (
          <button
            onClick={onOpenUserManagement}
            className="hidden md:flex bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-2.5 py-1.5 rounded-md text-[12px] font-medium items-center space-x-1.5 transition-colors cursor-pointer shadow-xs"
            title="User & RBAC Access Control Management"
          >
            <Users className="w-3.5 h-3.5 text-slate-500" />
            <span>Users</span>
          </button>
        )}

        <button
          onClick={onResetDemo}
          className="hidden lg:flex bg-white hover:bg-slate-50 text-slate-500 hover:text-slate-800 border border-slate-200 px-2 py-1.5 rounded-md text-[11px] items-center space-x-1 transition-colors cursor-pointer"
          title="Reset Demo Dataset"
        >
          <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
          <span>Reset</span>
        </button>

        <div className="h-4 w-px bg-slate-200 hidden sm:block" />

        {/* User Account Profile Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-1.5 sm:space-x-2 bg-slate-50 hover:bg-slate-100 p-1 sm:px-2.5 sm:py-1.5 rounded-md border border-slate-200 transition-colors cursor-pointer"
          >
            <div className="w-6 h-6 sm:w-5 sm:h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs sm:text-[10px]">
              {user?.display_name ? user.display_name.charAt(0) : 'A'}
            </div>
            <div className="text-left text-[11px] hidden sm:block">
              <div className="font-semibold text-slate-800 leading-tight max-w-[100px] truncate">{user?.display_name || 'Anurag Swain'}</div>
              <div className="text-slate-500 text-[10px] font-medium">{user?.role || 'SECURITY_ADMIN'}</div>
            </div>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-1.5 w-60 bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-50 text-xs animate-in fade-in zoom-in-95 duration-100">
              <div className="px-3.5 py-2.5 border-b border-slate-100">
                <div className="font-semibold text-slate-900">{user?.display_name}</div>
                <div className="text-slate-500 text-[11px] font-mono">{user?.email}</div>
                <div className="mt-1 flex items-center gap-1.5">
                  <span className="text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 px-1.5 py-0.2 rounded">
                    {user?.role}
                  </span>
                  <span className="text-[10px] text-slate-400 truncate">
                    {user?.organization_name || organizationName}
                  </span>
                </div>
              </div>

              {/* Mobile Quick Action Items */}
              <div className="sm:hidden border-b border-slate-100 py-1">
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onExportReport();
                  }}
                  className="w-full px-3.5 py-2 text-left hover:bg-slate-50 flex items-center space-x-2 text-slate-700"
                >
                  <FileText className="w-3.5 h-3.5 text-slate-500" />
                  <span>Executive Report</span>
                </button>

                {isUserAdmin && (
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onOpenUserManagement();
                    }}
                    className="w-full px-3.5 py-2 text-left hover:bg-slate-50 flex items-center space-x-2 text-slate-700"
                  >
                    <Users className="w-3.5 h-3.5 text-slate-500" />
                    <span>Manage Users & RBAC</span>
                  </button>
                )}

                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onResetDemo();
                  }}
                  className="w-full px-3.5 py-2 text-left hover:bg-slate-50 flex items-center space-x-2 text-slate-700"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
                  <span>Reset Demo Dataset</span>
                </button>
              </div>

              <div className="py-1">
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    logout();
                  }}
                  className="w-full px-3.5 py-2 text-left hover:bg-red-50 text-red-600 flex items-center space-x-2 transition-colors cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>

      </div>

    </header>
  );
};

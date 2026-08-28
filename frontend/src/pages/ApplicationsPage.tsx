import React, { useState } from 'react';
import { ApplicationInstance } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { Box, Filter, Search, ChevronRight } from 'lucide-react';
import { STATUS_STYLES } from '../designTokens';

interface ApplicationsPageProps {
  applications: ApplicationInstance[];
  onSelectApplication: (app: ApplicationInstance) => void;
}

export const ApplicationsPage: React.FC<ApplicationsPageProps> = ({ applications, onSelectApplication }) => {
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const filteredApps = applications.filter((app) => {
    const matchesSearch = app.display_name.toLowerCase().includes(search.toLowerCase()) ||
                          app.application.canonical_name.toLowerCase().includes(search.toLowerCase());
    const matchesSeverity = severityFilter === 'ALL' || app.risk_severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto font-sans">
      {/* Header & Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Application Inventory</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {filteredApps.length} authorized & shadow third-party integrations tracked across the organization.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3">
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by app or vendor..."
              className="w-full bg-white border border-slate-200 rounded-md pl-9 pr-3 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-xs"
            />
          </div>

          <div className="flex items-center space-x-1.5">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full sm:w-auto bg-white border border-slate-200 rounded-md px-3 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 shadow-xs cursor-pointer"
            >
              <option value="ALL">All Severities</option>
              <option value="Critical">Critical Only</option>
              <option value="High">High Only</option>
              <option value="Medium">Medium Only</option>
              <option value="Low">Low Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Premium Light Enterprise Table View */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden overflow-x-auto">
        <table className="ag-table min-w-[640px]">
          <thead>
            <tr>
              <th>Application Name</th>
              <th>Vendor</th>
              <th>Status</th>
              <th>Authorized By</th>
              <th>Risk Severity</th>
              <th className="text-right">Risk Score</th>
              <th className="w-10"></th>
            </tr>
          </thead>
          <tbody>
            {filteredApps.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-slate-400 text-xs">
                  No applications match the search or filter criteria.
                </td>
              </tr>
            ) : (
              filteredApps.map((app) => {
                const statusStyle = STATUS_STYLES[app.status] || STATUS_STYLES.active;
                return (
                  <tr
                    key={app.id}
                    onClick={() => onSelectApplication(app)}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                  >
                    <td className="font-semibold text-slate-900">
                      <div className="flex items-center space-x-2">
                        <span>{app.display_name}</span>
                        {app.is_shadow && (
                          <span className="bg-amber-50 text-amber-700 border border-amber-200 text-[10px] px-1.5 py-0.2 rounded font-medium">
                            Shadow
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="text-slate-600">{app.application.vendor?.name || 'Unknown Vendor'}</td>
                    <td>
                      <span className={`inline-flex px-2 py-0.5 rounded text-[11px] font-medium border ${statusStyle.bg} ${statusStyle.text} ${statusStyle.border}`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="text-slate-500 font-mono text-[11px]">{app.authorized_by_email}</td>
                    <td>
                      <SeverityBadge severity={app.risk_severity} showDot />
                    </td>
                    <td className="text-right font-mono font-bold text-slate-900 text-xs">
                      {app.risk_score}
                    </td>
                    <td className="text-right">
                      <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

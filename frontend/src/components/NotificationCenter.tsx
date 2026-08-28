import React, { useState, useEffect, useRef } from 'react';
import { Bell, Check, CheckCheck, Filter, X } from 'lucide-react';
import { api } from '../services/api';

interface NotificationItem {
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

const SEVERITY_DOT: Record<string, string> = {
  Critical: 'bg-red-500',
  High: 'bg-amber-500',
  Medium: 'bg-yellow-500',
  Low: 'bg-emerald-500',
  Info: 'bg-slate-400'
};

function formatRelativeTime(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

interface NotificationCenterProps {
  onNavigate?: (tab: string, targetId?: string) => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ onNavigate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [criticalCount, setCriticalCount] = useState(0);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'UNREAD' | 'CRITICAL' | 'HIGH' | 'MONITORING' | 'CONNECTOR'>('ALL');
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const loadCounts = () => {
    api.getUnreadNotificationCount()
      .then(res => {
        setUnreadCount(res.unread_count || 0);
        setCriticalCount(res.critical_unread_count || 0);
      })
      .catch(() => {});
  };

  const loadNotifications = () => {
    setLoading(true);
    let params: any = {};
    if (activeFilter === 'UNREAD') params.is_read = false;
    if (activeFilter === 'CRITICAL') params.severity = 'Critical';
    if (activeFilter === 'HIGH') params.severity = 'High';

    api.getNotifications(params)
      .then(data => {
        let items = data as NotificationItem[];
        if (activeFilter === 'MONITORING') {
          items = items.filter(n => n.source_type === 'CHANGE' || n.source_type === 'INCIDENT');
        } else if (activeFilter === 'CONNECTOR') {
          items = items.filter(n => n.source_type === 'CONNECTOR');
        }
        setNotifications(items);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    loadCounts();
    const timer = setInterval(loadCounts, 15000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, activeFilter]);

  // Click outside to close
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleMarkRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.markNotificationRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch {}
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
      setCriticalCount(0);
    } catch {}
  };

  const handleItemClick = (notif: NotificationItem) => {
    if (!notif.is_read) {
      api.markNotificationRead(notif.id).catch(() => {});
      setNotifications(prev => prev.map(n => n.id === notif.id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
    setIsOpen(false);
    if (onNavigate) {
      if (notif.source_type === 'INCIDENT' || notif.source_type === 'CHANGE') {
        onNavigate('monitoring', notif.source_id || undefined);
      } else if (notif.source_type === 'CONNECTOR') {
        onNavigate('connectors', notif.source_id || undefined);
      } else {
        onNavigate('monitoring');
      }
    }
  };

  return (
    <div className="relative font-sans" ref={dropdownRef}>
      {/* Bell Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
        title="Security Notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className={`absolute top-1 right-1 px-1.5 py-0.2 text-[9px] font-bold rounded-full text-white ${
            criticalCount > 0 ? 'bg-red-600' : 'bg-amber-600'
          }`}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Dropdown Panel */}
      {isOpen && (
        <div className="fixed sm:absolute right-2 sm:right-0 top-14 sm:top-auto mt-2 w-[calc(100vw-1rem)] sm:w-96 max-w-sm sm:max-w-none bg-white border border-slate-200 rounded-lg shadow-xl z-50 flex flex-col overflow-hidden text-xs">
          {/* Header */}
          <div className="p-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-900 text-xs uppercase tracking-wide">Security Alerts</span>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 bg-red-50 text-red-700 border border-red-200 text-[10px] font-semibold rounded">
                  {unreadCount} unread
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllRead}
                  className="text-[11px] text-slate-500 hover:text-slate-800 flex items-center space-x-1 cursor-pointer font-medium"
                >
                  <CheckCheck className="w-3.5 h-3.5" />
                  <span>Mark read</span>
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Filter Pills */}
          <div className="px-3 py-2 border-b border-slate-100 flex items-center gap-1.5 overflow-x-auto bg-slate-50/40">
            <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            {(['ALL', 'UNREAD', 'CRITICAL', 'HIGH', 'MONITORING', 'CONNECTOR'] as const).map(f => (
              <button
                key={f}
                onClick={() => setActiveFilter(f)}
                className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors cursor-pointer ${
                  activeFilter === f
                    ? 'bg-blue-50 text-blue-700 border border-blue-200 font-semibold'
                    : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Notification List */}
          <div className="max-h-80 overflow-y-auto divide-y divide-slate-100">
            {loading ? (
              <div className="p-6 text-center text-slate-400 text-xs">Loading alerts...</div>
            ) : notifications.length === 0 ? (
              <div className="p-6 text-center text-slate-400 text-xs">No notifications recorded</div>
            ) : (
              notifications.map(item => {
                const dotClass = SEVERITY_DOT[item.severity] || SEVERITY_DOT.Info;
                return (
                  <div
                    key={item.id}
                    onClick={() => handleItemClick(item)}
                    className={`p-3.5 transition-colors cursor-pointer flex items-start space-x-3 ${
                      item.is_read
                        ? 'bg-white hover:bg-slate-50 text-slate-600'
                        : 'bg-blue-50/30 hover:bg-blue-50/60 text-slate-900 font-medium'
                    }`}
                  >
                    <span className={`w-2 h-2 rounded-full shrink-0 mt-1 ${dotClass}`} />
                    <div className="flex-1 min-w-0 space-y-0.5">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-xs text-slate-900 truncate">{item.title}</span>
                        <span className="text-[10px] text-slate-400 shrink-0 ml-2 font-mono">
                          {formatRelativeTime(item.created_at)}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed font-normal">
                        {item.body}
                      </p>
                    </div>
                    {!item.is_read && (
                      <button
                        onClick={(e) => handleMarkRead(item.id, e)}
                        className="text-slate-400 hover:text-blue-600 p-1 rounded transition-colors shrink-0"
                        title="Mark as read"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

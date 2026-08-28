/**
 * AccessGuard Light Enterprise Design System Tokens
 * Human-designed / Professional Cybersecurity Product System
 */

export const SEVERITY_STYLES: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  Critical: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    dot: 'bg-red-500',
  },
  High: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    dot: 'bg-amber-500',
  },
  Medium: {
    bg: 'bg-yellow-50',
    text: 'text-yellow-700',
    border: 'border-yellow-200',
    dot: 'bg-yellow-500',
  },
  Low: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    dot: 'bg-emerald-500',
  },
  Info: {
    bg: 'bg-slate-50',
    text: 'text-slate-600',
    border: 'border-slate-200',
    dot: 'bg-slate-400',
  },
};

export const STATUS_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  active: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  ACTIVE: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  dormant: { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
  DORMANT: { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
  shadow: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  SHADOW: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  revoked: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  REVOKED: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  APPROVED: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  PENDING_REVIEW: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  RESTRICTED: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
};

export const PRIORITY_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  P0: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  P1: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  P2: { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200' },
};

export const SURFACE = {
  canvas: 'bg-[#F8F9FB]',
  card: 'bg-white border border-slate-200 rounded-lg shadow-sm',
  cardFlat: 'bg-white border border-slate-200 rounded-lg',
  header: 'bg-white border-b border-slate-200',
  sidebar: 'bg-white border-r border-slate-200',
  input: 'bg-white border border-slate-300 text-slate-900 rounded-md focus:border-blue-600 focus:ring-1 focus:ring-blue-600 text-xs px-3 py-1.5',
};

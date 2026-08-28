import React from 'react';
import { SeverityLevel } from '../types';
import { SEVERITY_STYLES } from '../designTokens';

interface SeverityBadgeProps {
  severity: SeverityLevel;
  className?: string;
  showDot?: boolean;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, className = '', showDot = false }) => {
  const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.Info;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium border ${style.bg} ${style.text} ${style.border} ${className}`}
    >
      {showDot && <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />}
      {severity}
    </span>
  );
};

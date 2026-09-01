/**
 * Badge component for SIH26093 Frontend
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { getRiskLevelColor, getSeverityColor, getPriorityColor, getStatusColor } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'risk' | 'severity' | 'priority' | 'status';
  value?: string;
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', value, children, ...props }, ref) => {
    let colorClass = 'bg-gray-100 text-gray-800';
    
    if (variant === 'risk' && value) {
      const riskColor = getRiskLevelColor(value);
      colorClass = `${riskColor.replace('risk-', 'bg-')}/10 text-${riskColor.replace('risk-', '')}-700`;
    } else if (variant === 'severity' && value) {
      colorClass = getSeverityColor(value);
    } else if (variant === 'priority' && value) {
      colorClass = getPriorityColor(value);
    } else if (variant === 'status' && value) {
      colorClass = getStatusColor(value);
    }
    
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
          colorClass,
          className
        )}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

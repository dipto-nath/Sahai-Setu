/**
 * Progress Steps component for SIH26093 Frontend
 */

import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressStep {
  label: string;
  completed?: boolean;
  active?: boolean;
}

interface ProgressStepsProps {
  steps: ProgressStep[];
  className?: string;
}

export function ProgressSteps({ steps, className }: ProgressStepsProps) {
  return (
    <div className={cn('space-y-4', className)} role="list" aria-label="Processing steps">
      {steps.map((step, index) => (
        <div key={index} className="flex items-start gap-3" role="listitem">
          <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full border-2 text-sm font-medium transition-colors"
            style={{
              borderColor: step.completed ? '#22c55e' : step.active ? '#0ea5e9' : '#e5e7eb',
              backgroundColor: step.completed ? '#22c55e' : step.active ? '#0ea5e9' : 'transparent',
              color: step.completed || step.active ? 'white' : '#9ca3af',
            }}
          >
            {step.completed ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              index + 1
            )}
          </div>
          <div className="flex-1 min-w-0 pt-1">
            <p className={cn(
              'text-sm font-medium transition-colors',
              step.active ? 'text-primary-700' : step.completed ? 'text-gray-900' : 'text-gray-500'
            )}>
              {step.label}
            </p>
            {step.active && (
              <div className="mt-1 h-1.5 bg-primary-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary-600 animate-pulse" style={{ width: '60%' }} />
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

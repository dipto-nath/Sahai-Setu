/**
 * Utility functions for SIH26093 Frontend
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(dateString);
}

export function getRiskLevelColor(riskLevel: string): string {
  switch (riskLevel) {
    case 'LOW':
      return 'risk-low';
    case 'MODERATE':
      return 'risk-moderate';
    case 'HIGH':
      return 'risk-high';
    case 'CRITICAL':
      return 'risk-critical';
    case 'INCONCLUSIVE':
      return 'gray';
    default:
      return 'gray';
  }
}

export function getRiskLevelLabel(riskLevel: string): string {
  switch (riskLevel) {
    case 'LOW':
      return 'Low';
    case 'MODERATE':
      return 'Moderate';
    case 'HIGH':
      return 'High';
    case 'CRITICAL':
      return 'Critical';
    case 'INCONCLUSIVE':
      return 'Inconclusive';
    default:
      return riskLevel;
  }
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'low':
      return 'text-green-600 bg-green-100';
    case 'moderate':
      return 'text-yellow-700 bg-yellow-100';
    case 'high':
      return 'text-red-600 bg-red-100';
    case 'severe':
      return 'text-red-800 bg-red-200';
    default:
      return 'text-gray-600 bg-gray-100';
  }
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'ROUTINE':
      return 'text-blue-600 bg-blue-100';
    case 'ELEVATED':
      return 'text-yellow-700 bg-yellow-100';
    case 'URGENT':
      return 'text-orange-600 bg-orange-100';
    case 'IMMEDIATE':
      return 'text-red-700 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'PENDING':
      return 'text-yellow-700 bg-yellow-100';
    case 'ASSESSED':
      return 'text-blue-600 bg-blue-100';
    case 'PENDING_REVIEW':
      return 'text-orange-600 bg-orange-100';
    case 'REVIEWED':
      return 'text-green-600 bg-green-100';
    case 'CLOSED':
      return 'text-gray-600 bg-gray-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function generateCaseId(): string {
  return `CASE-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
}

/**
 * All Cases Page - Officer Dashboard
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Card, CardContent, CardHeader, CardTitle 
} from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Table } from '@/components/ui/Table';
import { apiService } from '@/services/api';
import { ExternalLink, FileText, Search, Filter } from 'lucide-react';
import type { Case, RiskLevel } from '@/types';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';

const RISK_COLORS = {
  LOW: '#22c55e',
  MODERATE: '#f59e0b',
  HIGH: '#ef4444',
  CRITICAL: '#7f1d1d',
  INCONCLUSIVE: '#9ca3af',
};

export default function AllCasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    const fetchCases = async () => {
      try {
        setIsLoading(true);
        const data = await apiService.getCases(0, 100);
        setCases(data);
      } catch (err) {
        console.error('Failed to fetch cases:', err);
        setError('Unable to load cases. Please ensure the backend is running.');
        setCases([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCases();
  }, []);

  const filteredCases = cases.filter(c => {
    const matchesSearch = !search || 
      c.anonymous_case_id.toLowerCase().includes(search.toLowerCase()) ||
      c.language.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = !riskFilter || c.risk_level === riskFilter;
    const matchesStatus = !statusFilter || c.status === statusFilter;
    return matchesSearch && matchesRisk && matchesStatus;
  });

  const getRiskBadge = (risk: RiskLevel) => {
    return <Badge variant="risk" value={risk}>{risk}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    return <Badge variant="status" value={status}>{status.replace('_', ' ')}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-6 h-6 text-primary-600" />
            All Cases
          </h1>
          <p className="text-gray-600 mt-1">Comprehensive list of citizen triage interactions</p>
        </div>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <Input
                label="Search"
                placeholder="Search by Case ID or language..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                icon={<Search className="w-4 h-4" />}
              />
            </div>
            <div>
              <Select
                label="Filter by Risk"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Risk Levels' },
                  { value: 'CRITICAL', label: 'Critical' },
                  { value: 'HIGH', label: 'High' },
                  { value: 'MODERATE', label: 'Moderate' },
                  { value: 'LOW', label: 'Low' },
                ]}
              />
            </div>
            <div>
              <Select
                label="Filter by Status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Statuses' },
                  { value: 'PENDING_REVIEW', label: 'Pending Review' },
                  { value: 'ASSESSED', label: 'Assessed' },
                  { value: 'IN_PROGRESS', label: 'In Progress' },
                  { value: 'CLOSED', label: 'Closed' },
                ]}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Case Directory ({filteredCases.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : filteredCases.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No cases match your filters.
            </div>
          ) : (
            <Table
              headers={['Case ID', 'Language', 'Risk Level', 'SVI Score', 'Confidence', 'Status', 'Date', 'Action']}
              rows={filteredCases.map(c => [
                <span key="id" className="font-mono text-xs font-semibold">{c.anonymous_case_id}</span>,
                <span key="lang" className="uppercase font-medium text-xs">{c.language}</span>,
                getRiskBadge(c.risk_level),
                <div key="svi" className="flex items-center gap-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${c.svi}%`,
                        backgroundColor: RISK_COLORS[c.risk_level as RiskLevel] || '#9ca3af',
                      }}
                    />
                  </div>
                  <span className="text-xs font-medium">{c.svi}/100</span>
                </div>,
                <span key="conf" className="text-xs">{Math.round((c.confidence || 0) * 100)}%</span>,
                getStatusBadge(c.status),
                <span key="date" className="text-xs text-gray-500">
                  {new Date(c.created_at).toLocaleDateString()}
                </span>,
                <Link
                  key="action"
                  href={`/officer/cases/${c.id}`}
                  className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-800 font-medium"
                >
                  View Details
                  <ExternalLink className="w-3 h-3" />
                </Link>
              ])}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

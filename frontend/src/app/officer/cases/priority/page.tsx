/**
 * Priority Cases Page - Officer Dashboard
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
import { ExternalLink, Flag, Search, Filter } from 'lucide-react';
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

export default function PriorityCasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('');

  useEffect(() => {
    const fetchCases = async () => {
      try {
        setIsLoading(true);
        const data = await apiService.getPriorityCases(100);
        setCases(data);
      } catch (err) {
        console.error('Failed to fetch priority cases:', err);
        setError('Unable to load priority cases. Please try again later.');
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
    return matchesSearch && matchesRisk;
  });

  const sortCases = (a: Case, b: Case) => {
    const riskOrder = { CRITICAL: 4, HIGH: 3, MODERATE: 2, LOW: 1, INCONCLUSIVE: 0 };
    const riskDiff = riskOrder[b.risk_level as RiskLevel] - riskOrder[a.risk_level as RiskLevel];
    if (riskDiff !== 0) return riskDiff;
    return b.svi - a.svi;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Flag className="w-6 h-6 text-red-600" />
            Priority Cases
          </h1>
          <p className="text-gray-600 mt-1">High and Critical risk cases requiring attention</p>
        </div>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                label="Search"
                placeholder="Search by Case ID or language..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                icon={<Search className="w-4 h-4" />}
              />
            </div>
            <div className="w-full sm:w-48">
              <Select
                label="Risk Level"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Risk Levels' },
                  { value: 'CRITICAL', label: 'Critical' },
                  { value: 'HIGH', label: 'High' },
                ]}
                icon={<Filter className="w-4 h-4" />}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Priority Cases ({filteredCases.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : filteredCases.length > 0 ? (
            <Table
              columns={[
                { key: 'anonymous_case_id', header: 'Case ID' },
                { key: 'created_at', header: 'Date/Time', render: (row) => new Date(row.created_at).toLocaleString() },
                { key: 'language', header: 'Language', render: (row) => row.language.toUpperCase() },
                { key: 'risk_level', header: 'Risk Level', render: (row) => (
                  <Badge variant="risk" value={row.risk_level} className="capitalize">{row.risk_level}</Badge>
                ) },
                { key: 'svi', header: 'SVI', render: (row) => `${row.svi}/100` },
                { key: 'confidence', header: 'Confidence', render: (row) => `${(row.confidence * 100).toFixed(0)}%` },
                { key: 'status', header: 'Status', render: (row) => (
                  <Badge variant="status" value={row.status}>{row.status.replace('_', ' ')}</Badge>
                ) },
                { key: 'assigned_user_id', header: 'Assigned', render: (row) => row.assigned_user_id ? `Officer #${row.assigned_user_id}` : 'Unassigned' },
              ]}
              data={filteredCases.sort(sortCases)}
              keyExtractor={(row) => row.id.toString()}
              onRowClick={(row) => window.location.href = `/officer/cases/${row.id}`}
            />
          ) : (
            <div className="text-center py-8 text-gray-500">No priority cases found.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

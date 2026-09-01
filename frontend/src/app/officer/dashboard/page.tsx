/**
 * Officer Dashboard Main Page
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Card, CardContent, CardHeader, CardTitle 
} from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table } from '@/components/ui/Table';
import { apiService } from '@/services/api';
import { cn } from '@/lib/utils';
import { 
  Users, AlertTriangle, Clock, TrendingUp, 
  Flag, FileText, ExternalLink
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend
} from 'recharts';
import type { DashboardData, Case, RiskLevel } from '@/types';

const RISK_COLORS = {
  LOW: '#22c55e',
  MODERATE: '#f59e0b',
  HIGH: '#ef4444',
  CRITICAL: '#7f1d1d',
  INCONCLUSIVE: '#9ca3af',
};

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [priorityCases, setPriorityCases] = useState<Case[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [dashboard, priority] = await Promise.all([
          apiService.getDashboard(),
          apiService.getPriorityCases(10),
        ]);
        setDashboardData(dashboard);
        setPriorityCases(priority);
      } catch (err: any) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Unable to load dashboard data. Please ensure the backend is running.');
        setDashboardData(null);
        setPriorityCases([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  const summary = dashboardData?.summary || { total_cases: 0, low: 0, moderate: 0, high: 0, critical: 0, pending_human_review: 0 };

  const statCards = [
    { label: 'Total Cases', value: summary.total_cases, icon: FileText, color: 'text-blue-600', bg: 'bg-blue-100' },
    { label: 'Low Risk', value: summary.low, icon: Flag, color: 'text-green-600', bg: 'bg-green-100' },
    { label: 'Moderate', value: summary.moderate, icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-100' },
    { label: 'High Risk', value: summary.high, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100' },
    { label: 'Critical', value: summary.critical, icon: AlertTriangle, color: 'text-red-800', bg: 'bg-red-200' },
    { label: 'Pending Review', value: summary.pending_human_review, icon: Clock, color: 'text-purple-600', bg: 'bg-purple-100' },
  ];

  const riskDistributionData = dashboardData?.risk_distribution || [];
  const languageData = dashboardData?.language_distribution || [];
  const casesOverTimeData = dashboardData?.cases_over_time || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Overview of case assessments and risk indicators</p>
        </div>
        <div className="flex gap-2">
          <Link href="/officer/cases/priority">
            <Button variant="outline"><Flag className="w-4 h-4 mr-2" />Priority Cases</Button>
          </Link>
          <Link href="/officer/cases">
            <Button><FileText className="w-4 h-4 mr-2" />All Cases</Button>
          </Link>
        </div>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm" role="alert">
          {error}
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {statCards.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center', stat.bg)}>
                  <stat.icon className={cn('w-6 h-6', stat.color)} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Level Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riskDistributionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="risk_level" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: number) => [value, 'Cases']} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {riskDistributionData.map((entry, index) => (
                      <Cell key={index} fill={RISK_COLORS[entry.risk_level as RiskLevel] || '#9ca3af'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Language Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Cases by Language</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={languageData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="count"
                    nameKey="language"
                    label={({ language, count, percent }) => `${language.toUpperCase()}: ${count} (${(percent * 100).toFixed(0)}%)`}
                    labelLine={false}
                  >
                    {languageData.map((entry, index) => (
                      <Cell key={index} fill={Object.values(RISK_COLORS)[index % Object.values(RISK_COLORS).length]} />
                    ))}
                  </Pie>
                  <Legend />
                  <Tooltip formatter={(value: number) => [value, 'Cases']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Cases Over Time */}
      <Card>
        <CardHeader>
          <CardTitle>Cases Over Time (Last 30 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={casesOverTimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number) => [value, 'Cases']} />
                <Bar dataKey="count" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Priority Cases Table */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <CardTitle>Priority Cases (High & Critical)</CardTitle>
          <Link href="/officer/cases/priority">
            <Button variant="ghost" size="sm"><ExternalLink className="w-4 h-4 mr-1" />View All</Button>
          </Link>
        </CardHeader>
        <CardContent>
          {priorityCases.length > 0 ? (
            <Table
              columns={[
                { key: 'anonymous_case_id', header: 'Case ID' },
                { key: 'created_at', header: 'Date/Time', render: (row) => new Date(row.created_at).toLocaleString() },
                { key: 'language', header: 'Language', render: (row) => row.language.toUpperCase() },
                { key: 'risk_level', header: 'Risk Level', render: (row) => (
                  <Badge variant="risk" value={row.risk_level}>{row.risk_level}</Badge>
                ) },
                { key: 'svi', header: 'SVI', render: (row) => `${row.svi}/100` },
                { key: 'confidence', header: 'Confidence', render: (row) => `${(row.confidence * 100).toFixed(0)}%` },
                { key: 'status', header: 'Status', render: (row) => (
                  <Badge variant="status" value={row.status}>{row.status.replace('_', ' ')}</Badge>
                ) },
              ]}
              data={priorityCases}
              keyExtractor={(row) => row.id.toString()}
              onRowClick={(row) => window.location.href = `/officer/cases/${row.id}`}
            />
          ) : (
            <div className="text-center py-8 text-gray-500">No priority cases at this time.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Case Details Page
 *
 * Shows full case details for a single case, including the AI-generated
 * Tactical AI Guidance (summary / care / action) parsed safely from the
 * backend's `assessments.explanation_json` column.
 *
 * Bug 2 fix: the Tactical AI Guidance card was missing for textual
 * complaints because:
 *   (a) the backend `case_service.get_case_details()` was not whitelisting
 *       `explanation_json` in the returned assessment dict, and
 *   (b) the frontend had no safe parser for the JSON-encoded string.
 *
 * Both are now fixed upstream; this page renders the parsed fields.
 */

'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  Card, CardContent, CardHeader, CardTitle, CardDescription,
} from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { apiService } from '@/services/api';
import { parseExplanation } from '@/types';
import {
  ArrowLeft, AlertTriangle, Brain, MessageSquare,
  Sparkles, Heart, ListChecks, AlertCircle,
} from 'lucide-react';

const RISK_COLORS: Record<string, string> = {
  LOW: 'risk-low',
  MODERATE: 'risk-moderate',
  HIGH: 'risk-high',
  CRITICAL: 'risk-critical',
  INCONCLUSIVE: 'risk-gray',
};

export default function CaseDetailsPage() {
  const params = useParams();
  const caseId = params?.id as string | undefined;

  const [caseData, setCaseData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) return;
    const fetchCase = async () => {
      try {
        setIsLoading(true);
        // Use the typed helper; fall back to the untyped getCase() on
        // older builds of apiService for forward compatibility.
        const fetcher =
          (apiService as any).getCaseDetails?.bind(apiService) ??
          (apiService as any).getCase?.bind(apiService);
        if (!fetcher) {
          throw new Error('No case-detail endpoint available on apiService.');
        }
        const data = await fetcher(parseInt(caseId, 10));
        setCaseData(data);
        setError(null);
      } catch (err: any) {
        console.error('Failed to fetch case:', err);
        setError(
          err?.response?.data?.detail ||
          err?.message ||
          'Failed to load case details.',
        );
        setCaseData(null);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCase();
  }, [caseId]);

  // Safe parse of the backend's JSON-encoded explanation column.
  // Returns { summary, care, action } with empty strings when missing.
  const guidance = useMemo(() => {
    if (!caseData?.assessment) {
      return { summary: '', care: '', action: '', hasAny: false };
    }
    const parsed = parseExplanation(caseData.assessment.explanation_json);
    const summary = parsed.summary?.trim() ?? '';
    const care = parsed.care?.trim() ?? '';
    const action = parsed.action?.trim() ?? '';
    return {
      summary,
      care,
      action,
      hasAny: Boolean(summary || care || action),
    };
  }, [caseData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (error && !caseData) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <Link href="/cases" className="mt-4 text-primary-600 hover:underline">
          Back to Cases
        </Link>
      </div>
    );
  }

  if (!caseData) return null;

  const c = caseData.case;
  const assessment = caseData.assessment;
  const indicators = caseData.indicators || [];
  const interactions = caseData.interactions || [];

  const formatDate = (dateString?: string) =>
    dateString ? new Date(dateString).toLocaleString() : '—';

  // Victim's submitted text (from the most recent TEXT / MULTIMODAL interaction).
  const victimText = (interactions as any[])
    .filter(
      (i) => i?.input_type === 'TEXT' || i?.input_type === 'MULTIMODAL',
    )
    .map((i) => i?.text_content)
    .filter((t: string | undefined) => t && t.trim().length > 0)
    .join('\n\n');

  return (
    <div className="space-y-6 p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/cases" className="p-2 rounded-lg hover:bg-gray-100">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">
            {c?.anonymous_case_id ?? `Case #${caseId}`}
          </h1>
          <p className="text-gray-600">Case Details &amp; Assessment</p>
        </div>
        <Badge variant="status" value={c?.status} className="text-sm">
          {String(c?.status ?? '').replace('_', ' ')}
        </Badge>
      </div>

      {/* Top metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-gray-500">Risk Level</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="risk" value={c?.risk_level} className="text-base px-3 py-1">
                {c?.risk_level ?? 'N/A'}
              </Badge>
              <span className="text-sm text-gray-500">
                SVI: {c?.svi ?? '—'}/100
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-gray-500">Confidence</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              {assessment?.confidence != null
                ? `${Math.round(Number(assessment.confidence) * 100)}%`
                : 'N/A'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-gray-500">Language</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              {String(c?.language ?? 'en').toUpperCase()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-gray-500">Created</p>
            <p className="text-base font-medium text-gray-900 mt-2">
              {formatDate(c?.created_at)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Victim's original complaint (text only) */}
      {victimText && (
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              Victim&apos;s Complaint (Text)
            </CardTitle>
            <CardDescription>
              The original text submitted by the victim.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">
                {victimText}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ============================================================ */}
      {/* TACTICAL AI GUIDANCE — Bug 2 fix                               */}
      {/* ============================================================ */}
      <Card
        className="border-l-4 border-l-purple-500"
        data-testid="tactical-ai-guidance"
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="w-5 h-5 text-purple-600" />
            Tactical AI Guidance
          </CardTitle>
          <CardDescription>
            Gemini-generated summary, care, and action plan for this case.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {guidance.hasAny ? (
            <>
              {guidance.summary && (
                <div className="flex items-start gap-3 rounded-lg bg-purple-50 border border-purple-200 p-4">
                  <Brain className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-purple-700">
                      Summary
                    </p>
                    <p className="text-gray-900 mt-1 leading-relaxed">
                      {guidance.summary}
                    </p>
                  </div>
                </div>
              )}

              {guidance.care && (
                <div className="flex items-start gap-3 rounded-lg bg-pink-50 border border-pink-200 p-4">
                  <Heart className="w-5 h-5 text-pink-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-pink-700">
                      Care
                    </p>
                    <p className="text-gray-900 mt-1 leading-relaxed">
                      {guidance.care}
                    </p>
                  </div>
                </div>
              )}

              {guidance.action && (
                <div className="flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 p-4">
                  <ListChecks className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-amber-700">
                      Action
                    </p>
                    <p className="text-gray-900 mt-1 leading-relaxed">
                      {guidance.action}
                    </p>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-start gap-3 rounded-lg bg-gray-50 border border-gray-200 p-4">
              <AlertCircle className="w-5 h-5 text-gray-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-gray-700">
                  No AI guidance is available for this case yet. This usually
                  means the case has not been analyzed, or the backend is not
                  returning{' '}
                  <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                    explanation_json
                  </code>{' '}
                  for this assessment.
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Debug:&nbsp;
                  <code className="bg-gray-100 px-1 py-0.5 rounded">
                    assessment.explanation_json ={' '}
                    {JSON.stringify(assessment?.explanation_json ?? null)}
                  </code>
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Indicators */}
      {indicators.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              Detected Indicators
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {indicators.map((ind: any, idx: number) => (
                <Badge
                  key={idx}
                  variant="severity"
                  value={ind?.severity}
                  className="text-sm"
                >
                  {ind?.name} · {ind?.severity}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
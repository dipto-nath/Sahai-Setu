/**
 * Case Details Page - Officer Dashboard
 */

'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  Card, CardContent, CardHeader, CardTitle, CardDescription
} from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { apiService } from '@/services/api';
import {
  ArrowLeft, Flag, Calendar, Globe, Shield,
  AlertTriangle, Brain, Mic, FileText,
  Edit, Plus, ExternalLink, MessageSquare, User
} from 'lucide-react';
import type { Case, AssessmentResult, IndicatorResult, RecommendationResult } from '@/types';
import { Modal } from '@/components/ui/Modal';
import { Select } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Input';
import { cn } from '@/lib/utils';

const RISK_COLORS = {
  LOW: 'risk-low',
  MODERATE: 'risk-moderate',
  HIGH: 'risk-high',
  CRITICAL: 'risk-critical',
  INCONCLUSIVE: 'risk-gray',
};

export default function CaseDetailsPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [caseData, setCaseData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewData, setReviewData] = useState<{
    human_risk: string;
    decision: string;
    notes: string;
  }>({
    human_risk: '',
    decision: '',
    notes: '',
  });

  useEffect(() => {
    const fetchCase = async () => {
      try {
        setIsLoading(true);
        const data = await apiService.getCase(parseInt(caseId));
        setCaseData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch case:', err);
        setError('Failed to load case details.');
        // Fallback mock data
        setCaseData(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCase();
  }, [caseId]);

  const handleReviewSubmit = async () => {
    try {
      if (!reviewData.human_risk || !reviewData.decision) {
        alert('Please select both risk level and decision');
        return;
      }
      await apiService.addReview(parseInt(caseId), {
        human_risk: reviewData.human_risk as any,
        decision: reviewData.decision as any,
        notes: reviewData.notes,
      });
      setShowReviewModal(false);
      const data = await apiService.getCase(parseInt(caseId));
      setCaseData(data);
    } catch (err) {
      console.error('Failed to submit review:', err);
      alert('Failed to submit review. Please try again.');
    }
  };

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
        <Link href="/officer/cases/priority" className="mt-4 text-primary-600 hover:underline">Back to Priority Cases</Link>
      </div>
    );
  }

  if (!caseData) return null;

  const c = caseData.case;
  const assessment = caseData.assessment;
  const indicators = caseData.indicators || [];
  const recommendations = caseData.recommendations || [];
  const reviews = caseData.reviews || [];
  const interactions = caseData.interactions || [];

  const formatDate = (dateString: string) => new Date(dateString).toLocaleString();
  const getRiskColor = (level: string) => RISK_COLORS[level as keyof typeof RISK_COLORS] || 'risk-gray';

  // Get the victim's text content from the most recent text interaction
  const victimText = interactions
    .filter((i: any) => i.input_type === 'TEXT' || i.input_type === 'MULTIMODAL')
    .map((i: any) => i.text_content)
    .filter((t: string) => t && t.trim().length > 0)
    .join('\n\n');

  // Get audio interactions
  const audioInteractions = interactions.filter((i: any) => 
    (i.input_type === 'AUDIO' || i.input_type === 'MULTIMODAL') && i.audio_storage_ref
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/officer/cases/priority" className="p-2 rounded-lg hover:bg-gray-100">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{c.anonymous_case_id}</h1>
          <p className="text-gray-600">Case Details & Assessment</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Risk Level</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="risk" value={c.risk_level} className="text-base px-3 py-1">
                    {c.risk_level}
                  </Badge>
                  <span className="text-sm text-gray-500">SVI: {c.svi}/100</span>
                </div>
              </div>
              <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center', `bg-${getRiskColor(c.risk_level)}/10`)}>
                <Flag className={cn('w-6 h-6', `text-${getRiskColor(c.risk_level).replace('risk-', '')}-600`)} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-gray-500">Confidence</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{assessment ? (assessment.confidence * 100).toFixed(0) + '%' : 'N/A'}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-gray-500">Language</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{c.language.toUpperCase()}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-gray-500">Status</p>
            <Badge variant="status" value={c.status} className="text-base">{c.status.replace('_', ' ')}</Badge>
          </CardContent>
        </Card>
      </div>

      {/* VICTIM'S DESCRIPTION SECTION - Main content showing what the victim wrote */}
      {victimText && (
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <User className="w-5 h-5 text-blue-600" />
              Victim&apos;s Description (Original Complaint)
            </CardTitle>
            <CardDescription>
              The original text submitted by the victim through the helpline interface
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <MessageSquare className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">{victimText}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* If has audio interactions, show playback */}
      {audioInteractions.length > 0 && (
        <Card className="border-l-4 border-l-purple-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Mic className="w-5 h-5 text-purple-600" />
              Victim&apos;s Audio Recording ({audioInteractions.length})
            </CardTitle>
            <CardDescription>
              Listen to the victim&apos;s voice recording(s)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {audioInteractions.map((ai: any, idx: number) => (
              <div key={idx} className="bg-purple-50 border border-purple-200 rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-purple-800">🎙️ Recording #{idx + 1}</p>
                  <span className="text-xs text-gray-500">{formatDate(ai.created_at)}</span>
                </div>
                {ai.audio_storage_ref?.startsWith('/uploads/') ? (
                  <audio 
                    controls 
                    className="w-full" 
                    src={`${process.env.NEXT_PUBLIC_API_URL || ''}${ai.audio_storage_ref}`} 
                    onError={(e) => {
                      const target = e.target as HTMLAudioElement;
                      target.style.display = 'none';
                      const p = document.createElement('p');
                      p.className = 'text-sm text-red-500 italic';
                      p.textContent = 'Audio file not found or expired.';
                      target.parentNode?.appendChild(p);
                    }}
                  />
                ) : (
                  <p className="text-sm text-gray-500 italic">Audio recording unavailable (demo data)</p>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* If nothing - demo mode message */}
      {!victimText && audioInteractions.length === 0 && (
        <Card className="border-l-4 border-l-gray-400">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="w-5 h-5 text-gray-600" />
              No Description Available
            </CardTitle>
            <CardDescription>
              No victim interaction text or audio was submitted for this case
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Shield className="w-5 h-5" />Case Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><p className="text-sm text-gray-500">Case ID</p><p className="font-mono text-sm">{c.anonymous_case_id}</p></div>
                <div><p className="text-sm text-gray-500">Created</p><p className="text-sm">{formatDate(c.created_at)}</p></div>
                <div><p className="text-sm text-gray-500">Updated</p><p className="text-sm">{formatDate(c.updated_at)}</p></div>
                <div><p className="text-sm text-gray-500">Assigned Officer</p><p className="text-sm">{c.assigned_user_id ? `#${c.assigned_user_id}` : 'Unassigned'}</p></div>
              </div>
            </CardContent>
          </Card>

          {assessment && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Brain className="w-5 h-5" />AI Assessment</CardTitle>
                <CardDescription>DEMO RULE-BASED ANALYSIS - Not a clinical diagnosis</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Final SVI</p><p className="text-2xl font-bold text-gray-900">{assessment.final_svi}/100</p></div>
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Text Score</p><p className="text-xl font-bold text-gray-900">{assessment.text_score}</p></div>
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Audio Score</p><p className="text-xl font-bold text-gray-900">{assessment.audio_score}</p></div>
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Context Score</p><p className="text-xl font-bold text-gray-900">{assessment.context_score}</p></div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Threat Score</p><p className="text-xl font-bold text-red-600">{assessment.threat_score}</p></div>
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Distress Score</p><p className="text-xl font-bold text-orange-600">{assessment.distress_score}</p></div>
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Assessment Status</p><Badge variant="status" value={assessment.assessment_status}>{assessment.assessment_status.replace('_', ' ')}</Badge></div>
                  <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Assessed</p><p className="text-sm">{formatDate(assessment.created_at)}</p></div>
                </div>
              </CardContent>
            </Card>
          )}

          {indicators.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><AlertTriangle className="w-5 h-5" />Detected Indicators ({indicators.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {indicators.map((ind: IndicatorResult, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div>
                        <p className="text-sm font-medium text-gray-900 capitalize">{ind.name.replace('_', ' ')}</p>
                        <p className="text-xs text-gray-500">confidence: {(ind.confidence * 100).toFixed(0)}%</p>
                      </div>
                      <Badge variant="severity" value={ind.severity}>{ind.severity}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><FileText className="w-5 h-5" />AI Recommendations ({recommendations.length})</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {recommendations.map((rec: RecommendationResult, idx: number) => (
                  <div key={idx} className="p-4 bg-gray-50 rounded-lg border-l-4 border-primary-500">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span className="font-medium">{rec.title || rec.type.replace('_', ' ')}</span>
                          <Badge variant="priority" value={rec.priority}>{rec.priority}</Badge>
                        </div>
                        <p className="text-sm text-gray-600">{rec.description || rec.reasoning}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Edit className="w-5 h-5" />Human Review</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button className="w-full" onClick={() => setShowReviewModal(true)}>
                <Plus className="w-4 h-4 mr-2" />Add Review
              </Button>
              {reviews.length > 0 && (
                <div className="space-y-3">
                  {reviews.map((review: any, idx: number) => (
                    <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="risk" value={review.human_risk}>{review.human_risk}</Badge>
                        <Badge variant="default" value={review.decision}>{review.decision.replace('_', ' ')}</Badge>
                      </div>
                      <p className="text-sm text-gray-600">{review.notes}</p>
                      <p className="text-xs text-gray-400">By Officer #{review.reviewer_id} • {formatDate(review.created_at)}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Interaction History - Showing ALL interactions */}
          {interactions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mic className="w-5 h-5" />
                  All Interactions ({interactions.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {interactions.map((interaction: any, idx: number) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" value={interaction.input_type.toLowerCase()}>{interaction.input_type}</Badge>
                        <Badge variant="default" value={interaction.language}>{interaction.language.toUpperCase()}</Badge>
                      </div>
                      <span className="text-xs text-gray-500">{formatDate(interaction.created_at)}</span>
                    </div>
                    {interaction.text_content && (
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{interaction.text_content}</p>
                    )}
                    {interaction.audio_storage_ref && (
                      <div className="mt-2">
                        {interaction.audio_storage_ref.startsWith('/uploads/') ? (
                          <audio 
                            controls 
                            className="w-full" 
                            src={`${process.env.NEXT_PUBLIC_API_URL || ''}${interaction.audio_storage_ref}`}
                            onError={(e) => {
                              const target = e.target as HTMLAudioElement;
                              target.style.display = 'none';
                              const p = document.createElement('p');
                              p.className = 'text-xs text-red-500 italic';
                              p.textContent = '🎙️ Audio file not found or expired.';
                              target.parentNode?.appendChild(p);
                            }}
                          />
                        ) : (
                          <p className="text-xs text-gray-500 italic">🎙️ Audio: {interaction.audio_storage_ref} (unavailable)</p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <Modal
        isOpen={showReviewModal}
        onClose={() => setShowReviewModal(false)}
        title="Add Human Review"
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Human Risk Assessment"
              value={reviewData.human_risk}
              onChange={(e) => setReviewData({...reviewData, human_risk: e.target.value})}
              options={[
                { value: 'LOW', label: 'Low' },
                { value: 'MODERATE', label: 'Moderate' },
                { value: 'HIGH', label: 'High' },
                { value: 'CRITICAL', label: 'Critical' },
                { value: 'INCONCLUSIVE', label: 'Inconclusive' },
              ]}
              required
            />
            <Select
              label="Decision"
              value={reviewData.decision}
              onChange={(e) => setReviewData({...reviewData, decision: e.target.value})}
              options={[
                { value: 'CONFIRMED', label: 'Confirmed AI Risk' },
                { value: 'MODIFIED', label: 'Modified Risk Level' },
                { value: 'FALSE_POSITIVE', label: 'False Positive' },
                { value: 'FALSE_NEGATIVE', label: 'False Negative' },
                { value: 'REASSESS_REQUESTED', label: 'Request Reassessment' },
                { value: 'ESCALATED', label: 'Escalated' },
              ]}
              required
            />
          </div>
          <Textarea
            label="Notes"
            value={reviewData.notes}
            onChange={(e) => setReviewData({...reviewData, notes: e.target.value})}
            placeholder="Optional notes about your review decision..."
            rows={3}
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setShowReviewModal(false)}>Cancel</Button>
            <Button onClick={handleReviewSubmit}>Submit Review</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

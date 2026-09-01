/**
 * Result Page - Victim Interface
 */

'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Shield, CheckCircle, Info, ArrowLeft, FileText } from 'lucide-react';

export default function ResultPage() {
  const [submissionData, setSubmissionData] = useState<any>(null);

  useEffect(() => {
    const data = sessionStorage.getItem('submissionData');
    if (!data) {
      window.location.href = '/victim/interaction';
      return;
    }
    try {
      setSubmissionData(JSON.parse(data));
    } catch {
      window.location.href = '/victim/interaction';
    }
  }, []);

  const handleNewSubmission = () => {
    sessionStorage.removeItem('submissionData');
    window.location.href = '/victim/interaction';
  };

  if (!submissionData) {
    return null; // Loading or redirecting
  }

  const { anonymousCaseId, result } = submissionData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <Image src="/logo.png" alt="SahaiSetu Logo" width={40} height={40} className="object-contain" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">SahaiSetu</h1>
              <p className="text-xs text-gray-500">Atrocity Support AI</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Success State */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your interaction has been received</h2>
          <p className="text-gray-600 max-w-xl mx-auto">
            Thank you for sharing your experience. Your submission has been recorded and will be reviewed.
          </p>
        </div>

        {/* Case Reference Card */}
        {anonymousCaseId && (
          <Card className="mb-6 border-primary-200 bg-primary-50">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary-600" />
                Your Case Reference
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 bg-white rounded-lg border">
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Case ID</p>
                    <p className="text-lg font-mono font-semibold text-gray-900">{anonymousCaseId}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-500">Save this reference for follow-up</p>
              </div>
            </CardContent>
          </Card>
        )}



        {/* Information Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Info className="w-5 h-5 text-primary-600" />
              What happens next
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm text-gray-600">
              <li className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-xs font-medium text-primary-600">1</span>
                </span>
                <span>Your interaction has been securely received and logged in our system.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-xs font-medium text-primary-600">2</span>
                </span>
                <span>If additional support is appropriate, an authorized representative may follow up with you.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-xs font-medium text-primary-600">3</span>
                </span>
                <span>For immediate emergencies, please contact 112 (Emergency) or 100 (Police).</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        {/* Important Notice */}
        <Card className="mb-6 border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-medium">Important Reminder</p>
                <p className="mt-1">This system provides AI-assisted triage indicators only. It does NOT provide medical or psychiatric diagnosis. All assessments are reviewed by authorized human professionals.</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Demo Mode Notice */}
        <Card className="mb-6 border-amber-200 bg-amber-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-amber-800 text-sm">
              <span className="font-medium">DEMONSTRATION DATA</span>
              <span>— This is a prototype demonstration with fictional/synthetic cases.</span>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button variant="secondary" onClick={handleNewSubmission} className="w-full sm:w-auto">
            <ArrowLeft className="w-4 h-4 mr-2" />
            New Submission
          </Button>
          <Button variant="outline" href="/victim/welcome" className="w-full sm:w-auto">
            Back to Welcome
          </Button>
        </div>

        {/* Footer */}
        <div className="mt-10 text-center text-xs text-gray-400">
          <p>Prototype for SIH26093 | National Helpline Against Atrocities: 14566</p>
        </div>
      </main>
    </div>
  );
}

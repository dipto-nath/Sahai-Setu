/**
 * Processing Page - Victim Interface
 */

'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { ProgressSteps } from '@/components/ui/ProgressSteps';
import { CheckCircle, Loader2, Shield } from 'lucide-react';

const PROCESSING_STEPS = [
  'Processing input',
  'Detecting language',
  'Processing speech',
  'Analyzing textual indicators',
  'Analyzing audio features',
  'Calculating vulnerability indicators',
  'Preparing assessment',
];

export default function ProcessingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const submissionData = sessionStorage.getItem('submissionData');
    if (!submissionData) {
      router.push('/victim/interaction');
      return;
    }

    // Simulate processing steps
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= PROCESSING_STEPS.length - 1) {
          clearInterval(interval);
          setCompleted(true);
          // Navigate to result after a brief pause
          setTimeout(() => {
            router.push('/victim/result');
          }, 1000);
          return prev;
        }
        return prev + 1;
      });
    }, 200);

    return () => clearInterval(interval);
  }, [router]);

  const stepsWithStatus = PROCESSING_STEPS.map((step, index) => ({
    label: step,
    completed: index < currentStep,
    active: index === currentStep && !completed,
  }));

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 mb-4">
            <Shield className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Analyzing your interaction...</h1>
          <p className="text-gray-600">Please wait while we process your submission.</p>
        </div>

        {/* Progress Steps */}
        <Card>
          <CardContent className="p-6">
            <ProgressSteps steps={stepsWithStatus} />
          </CardContent>
        </Card>

        {/* Status */}
        <div className="mt-6 text-center">
          {completed ? (
            <div className="flex items-center justify-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              <span className="font-medium">Analysis complete. Redirecting...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2 text-primary-600">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="font-medium">
                {PROCESSING_STEPS[currentStep] || 'Processing...'}
              </span>
            </div>
          )}
        </div>

        {/* Demo Mode Notice */}
        <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg text-center text-sm text-amber-800">
          <strong>DEMO MODE</strong> - This is a prototype demonstration with simulated processing.
        </div>
      </div>
    </div>
  );
}

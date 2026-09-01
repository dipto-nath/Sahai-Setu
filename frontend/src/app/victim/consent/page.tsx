/**
 * Consent Page - Victim Interface
 */

'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Shield, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export default function ConsentPage() {
  const router = useRouter();
  const [accepted, setAccepted] = useState(false);

  const consentItems = [
    {
      icon: Shield,
      title: 'AI-Assisted Analysis',
      description: 'Your text and/or voice input may be processed by AI systems to detect indicators of distress, fear, trauma, and vulnerability.',
    },
    {
      icon: AlertCircle,
      title: 'Not a Medical Diagnosis',
      description: 'This system provides triage indicators only. It does NOT provide medical or psychiatric diagnosis. Human professionals review all assessments.',
    },
    {
      icon: CheckCircle,
      title: 'Human Review Available',
      description: 'All high-risk cases are flagged for review by authorized human professionals. You can request human follow-up.',
    },
    {
      icon: XCircle,
      title: 'Privacy & Data Handling',
      description: 'Information is handled according to applicable privacy policies. Data minimization principles are followed. You can withdraw consent where permitted.',
    },
  ];

  const handleContinue = () => {
    if (accepted) {
      router.push('/victim/language');
    }
  };

  const handleCancel = () => {
    router.push('/victim/welcome');
  };

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
        <div className="text-center mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Consent for AI Analysis</h2>
          <p className="text-gray-600">Please read the following information carefully before proceeding.</p>
        </div>

        {/* Consent Items */}
        <div className="space-y-4 mb-8">
          {consentItems.map((item, index) => (
            <Card key={index} className="border-gray-200">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary-100">
                    <item.icon className="w-5 h-5 text-primary-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{item.title}</h3>
                    <p className="mt-1 text-sm text-gray-600">{item.description}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Consent Checkbox */}
        <div className="mb-8">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={accepted}
              onChange={(e) => setAccepted(e.target.checked)}
              className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              aria-describedby="consent-description"
            />
            <div id="consent-description" className="text-sm text-gray-600">
              I have read and understand the above information. I consent to AI-assisted analysis of my interaction.
            </div>
          </label>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            variant="secondary"
            size="lg"
            className="w-full sm:w-auto min-w-[140px]"
            onClick={handleCancel}
          >
            Cancel
          </Button>
          <Button
            size="lg"
            className="w-full sm:w-auto min-w-[140px]"
            onClick={handleContinue}
            disabled={!accepted}
          >
            Continue
          </Button>
        </div>

        {/* Footer */}
        <div className="mt-10 text-center text-xs text-gray-400">
          <p>Prototype for SIH26093 | Not a medical diagnosis tool</p>
        </div>
      </main>
    </div>
  );
}

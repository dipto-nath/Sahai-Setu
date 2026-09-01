/**
 * Welcome Page - Victim Interface
 */

import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Shield, Info, AlertCircle } from 'lucide-react';

const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
];

export default function WelcomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image src="/logo.png" alt="SahaiSetu Logo" width={40} height={40} className="object-contain" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">SahaiSetu</h1>
                <p className="text-xs text-gray-500">Atrocity Support AI</p>
              </div>
            </div>
            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">Prototype for SIH26093</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Welcome to SahaiSetu
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            An AI-enabled system to help assess stress and trauma indicators for victims and complainants 
            approaching the National Helpline Against Atrocities (14566).
          </p>
        </div>

        {/* Privacy Notice */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Privacy & Confidentiality</h3>
                <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                  <li>Your interaction is processed securely and used only for assessment purposes</li>
                  <li>No personal identifying information is stored unnecessarily</li>
                  <li>Data is handled according to applicable privacy policies</li>
                  <li>You can choose to continue or cancel at any time</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Important Notices */}
        <Card className="mb-8 border-amber-200 bg-amber-50">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-medium text-amber-900 mb-2">Important Information</h3>
                <ul className="text-sm text-amber-800 space-y-1 list-disc list-inside">
                  <li><strong>This is not a medical diagnosis.</strong> The system provides AI-assisted triage indicators only.</li>
                  <li>Human professionals review all high-risk cases.</li>
                  <li>If you are in immediate danger, please contact emergency services (112) or police (100).</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Language Selection Preview */}
        <div className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4 text-center">Available Languages</h3>
          <div className="flex justify-center gap-4 flex-wrap">
            {SUPPORTED_LANGUAGES.map((lang) => (
              <span key={lang.code} className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700">
                {lang.name} ({lang.nativeName})
              </span>
            ))}
          </div>
        </div>

        {/* Continue Button */}
        <div className="text-center">
          <Link href="/victim/consent">
            <Button size="lg" className="w-full sm:w-auto min-w-[200px]" aria-label="Continue to consent page">
              Continue
            </Button>
          </Link>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-xs text-gray-400">
          <p>Prototype for Smart India Hackathon 2024 - SIH26093</p>
          <p>National Helpline Against Atrocities: 14566</p>
        </div>
      </main>
    </div>
  );
}

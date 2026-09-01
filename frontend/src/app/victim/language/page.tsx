/**
 * Language Selection Page - Victim Interface
 */

'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Shield, Globe, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ' },
  { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو' },
];

export default function LanguagePage() {
  const router = useRouter();
  const [selectedLanguage, setSelectedLanguage] = useState('en');

  const handleContinue = () => {
    sessionStorage.setItem('selectedLanguage', selectedLanguage);
    router.push('/victim/interaction');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <Image src="/logo.png" alt="SahaiSetu Logo" width={40} height={40} className="object-contain" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">SahaiSetu</h1>
              <p className="text-xs text-gray-500">Language Selection</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-100 mb-3 text-primary-600">
            <Globe className="w-6 h-6" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Select Your Preferred Language</h2>
          <p className="text-gray-600">Choose the language in which you would like to describe your experience.</p>
        </div>

        {/* Language Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
          {LANGUAGES.map((lang) => {
            const isSelected = selectedLanguage === lang.code;
            return (
              <button
                key={lang.code}
                type="button"
                onClick={() => setSelectedLanguage(lang.code)}
                className={cn(
                  'p-4 rounded-xl border text-left transition-all flex items-center justify-between',
                  isSelected
                    ? 'border-primary-600 bg-primary-50 ring-2 ring-primary-500 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                )}
              >
                <div>
                  <div className="font-semibold text-gray-900">{lang.name}</div>
                  <div className="text-sm text-gray-500">{lang.nativeName}</div>
                </div>
                {isSelected && (
                  <div className="w-6 h-6 rounded-full bg-primary-600 flex items-center justify-center text-white">
                    <Check className="w-4 h-4" />
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            variant="secondary"
            size="lg"
            className="w-full sm:w-auto min-w-[140px]"
            onClick={() => router.push('/victim/consent')}
          >
            Back
          </Button>
          <Button
            size="lg"
            className="w-full sm:w-auto min-w-[140px]"
            onClick={handleContinue}
          >
            Continue
          </Button>
        </div>
      </main>
    </div>
  );
}

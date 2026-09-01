/**
 * Interaction Page - Victim Interface
 * Supports both text and voice recording submissions
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Textarea } from '@/components/ui/Textarea';
import { Shield, MessageSquare, Mic, MicOff, AlertCircle, Square, Play, Trash2 } from 'lucide-react';
import { apiService } from '@/services/api';

type InputMode = 'text' | 'voice';

export default function InteractionPage() {
  const router = useRouter();
  const [language, setLanguage] = useState('en');
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [statement, setStatement] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const savedLang = sessionStorage.getItem('selectedLanguage');
    if (savedLang) {
      setLanguage(savedLang);
    }
  }, []);

  // Cleanup audio URL on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [audioUrl]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(250); // Collect data every 250ms
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (err: any) {
      console.error('Failed to start recording:', err);
      setError('Microphone access denied. Please allow microphone access in your browser settings and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const discardRecording = () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (inputMode === 'text' && !statement.trim()) {
      setError('Please provide a description of the event or situation.');
      return;
    }
    if (inputMode === 'voice' && !audioBlob) {
      setError('Please record a voice message first.');
      return;
    }

    let caseResult: any = undefined;
    try {
      setIsSubmitting(true);
      setError(null);

      // First create an anonymous case
      caseResult = await apiService.createAnonymousCase({ language });
      const caseId = caseResult.id;

      let analysisResult;

      if (inputMode === 'text') {
        // Text-only analysis
        analysisResult = await apiService.analyzeTextStandalone(statement, language, String(caseId));
      } else if (inputMode === 'voice' && audioBlob) {
        // Voice analysis — convert blob to File
        const audioFile = new File([audioBlob], `recording_${Date.now()}.webm`, { type: 'audio/webm' });
        if (statement.trim()) {
          // Voice + optional text note
          analysisResult = await apiService.analyzeMultimodalStandalone(statement, audioFile, language, String(caseId));
        } else {
          // Voice only
          analysisResult = await apiService.analyzeAudioStandalone(audioFile, language, String(caseId));
        }
      }

      sessionStorage.setItem('submissionData', JSON.stringify({
        statement: statement || '(Voice recording submitted)',
        language,
        result: analysisResult,
        caseId,
        anonymousCaseId: caseResult.anonymous_case_id,
        inputMode,
        timestamp: new Date().toISOString()
      }));

      router.push('/victim/processing');
    } catch (err: any) {
      console.error('Submission failed:', err);
      // Even if offline/demo, allow simulated processing
      sessionStorage.setItem('submissionData', JSON.stringify({
        statement: statement || '(Voice recording submitted)',
        language,
        inputMode,
        caseId: typeof caseResult !== 'undefined' ? caseResult.id : undefined,
        anonymousCaseId: typeof caseResult !== 'undefined' ? caseResult.anonymous_case_id : undefined,
        demoMode: true,
        timestamp: new Date().toISOString()
      }));
      router.push('/victim/processing');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image src="/logo.png" alt="SahaiSetu Logo" width={40} height={40} className="object-contain" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">SahaiSetu</h1>
                <p className="text-xs text-gray-500">Citizen Helpline Assistance</p>
              </div>
            </div>
            <span className="text-xs font-medium uppercase px-2.5 py-1 bg-primary-50 text-primary-700 rounded-md">
              Language: {language}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Share Your Experience</h2>
          <p className="text-gray-600">Please describe what occurred in your own words. Take as much time as you need.</p>
        </div>

        {/* Input Mode Toggle */}
        <div className="flex justify-center gap-2 mb-6">
          <button
            type="button"
            onClick={() => setInputMode('text')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
              inputMode === 'text'
                ? 'bg-primary-600 text-white shadow-md'
                : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Write Text
          </button>
          <button
            type="button"
            onClick={() => setInputMode('voice')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
              inputMode === 'voice'
                ? 'bg-primary-600 text-white shadow-md'
                : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Mic className="w-4 h-4" />
            Record Voice
          </button>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              {inputMode === 'text' ? (
                <><MessageSquare className="w-5 h-5 text-primary-600" /> Statement Description</>
              ) : (
                <><Mic className="w-5 h-5 text-primary-600" /> Voice Recording</>
              )}
            </CardTitle>
            <CardDescription>
              {inputMode === 'text'
                ? 'Provide details such as what happened, any immediate distress, or safety concerns.'
                : 'Record your statement using the microphone. You may also add an optional written note below.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {error}
                </div>
              )}

              {/* Voice Recording UI */}
              {inputMode === 'voice' && (
                <div className="space-y-4">
                  <div className="flex flex-col items-center gap-4 p-8 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                    {!isRecording && !audioBlob && (
                      <>
                        <button
                          type="button"
                          onClick={startRecording}
                          className="w-20 h-20 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center shadow-lg transition-all hover:scale-105 active:scale-95"
                        >
                          <Mic className="w-8 h-8" />
                        </button>
                        <p className="text-sm text-gray-500">Tap to start recording</p>
                      </>
                    )}

                    {isRecording && (
                      <>
                        <div className="relative">
                          <button
                            type="button"
                            onClick={stopRecording}
                            className="w-20 h-20 rounded-full bg-red-500 text-white flex items-center justify-center shadow-lg animate-pulse hover:bg-red-600 transition-colors cursor-pointer"
                          >
                            <Square className="w-8 h-8 fill-current" />
                          </button>
                          <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-600 rounded-full animate-ping" />
                        </div>
                        <p className="text-lg font-mono font-semibold text-red-600">{formatTime(recordingTime)}</p>
                        <p className="text-sm text-gray-500">Tap to stop recording</p>
                      </>
                    )}

                    {audioBlob && !isRecording && (
                      <div className="w-full space-y-3">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-700">
                            ✅ Recording captured ({formatTime(recordingTime)})
                          </p>
                          <button
                            type="button"
                            onClick={discardRecording}
                            className="flex items-center gap-1 text-xs text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-3 h-3" /> Discard
                          </button>
                        </div>
                        {audioUrl && (
                          <audio controls src={audioUrl} className="w-full" />
                        )}
                      </div>
                    )}
                  </div>

                  {/* Optional text note alongside voice */}
                  <Textarea
                    rows={3}
                    placeholder="(Optional) Add a written note alongside your voice recording..."
                    value={statement}
                    onChange={(e) => setStatement(e.target.value)}
                    className="text-base"
                  />
                </div>
              )}

              {/* Text Input UI */}
              {inputMode === 'text' && (
                <Textarea
                  rows={7}
                  placeholder="Type your statement here..."
                  value={statement}
                  onChange={(e) => setStatement(e.target.value)}
                  required
                  className="text-base"
                />
              )}

              <div className="flex flex-col sm:flex-row gap-4 justify-between items-center pt-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => router.push('/victim/language')}
                >
                  Change Language
                </Button>
                <Button
                  type="submit"
                  size="lg"
                  className="w-full sm:w-auto min-w-[160px]"
                  isLoading={isSubmitting}
                  disabled={isRecording}
                >
                  Submit for Assessment
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Emergency Notice */}
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-red-800">
                <p className="font-semibold">Immediate Danger or Emergency?</p>
                <p className="mt-0.5">Please call <strong>112</strong> (National Emergency) or <strong>100</strong> (Police) immediately if you or someone else is in immediate physical danger.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

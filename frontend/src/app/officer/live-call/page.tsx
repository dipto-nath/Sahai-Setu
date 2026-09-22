'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ShieldAlert, Mic, MicOff, PhoneCall, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import VocalStressMonitor from '@/components/ui/VocalStressMonitor';

interface LivePayload {
  transcript_chunk: string;
  full_transcript: string;
  svi: number;
  guidance: string[];
  risk_detected: boolean;
}

export default function LiveCallPage() {
  const [isActive, setIsActive] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [victimStream, setVictimStream] = useState<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const [transcript, setTranscript] = useState<string>('');
  const [sviScore, setSviScore] = useState<number>(0);
  const [guidance, setGuidance] = useState<string[]>([]);
  const [riskDetected, setRiskDetected] = useState<boolean>(false);
  const [language, setLanguage] = useState<string>('hi'); // Default to Hindi/Hinglish
  const transcriptEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [transcript]);

  const startCall = async () => {
    try {
      // 1. Get Victim Audio (System/Tab)
      const tabStream = await navigator.mediaDevices.getDisplayMedia({ 
        video: true,
        audio: true 
      });
      tabStream.getVideoTracks().forEach(track => track.stop());
      if (tabStream.getAudioTracks().length === 0) {
        alert("You must check 'Share tab audio' in the popup to capture the victim's sound.");
        tabStream.getTracks().forEach(track => track.stop());
        return;
      }

      // 2. Get Officer Audio (Mic)
      const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Store victim stream separately so VocalStressMonitor can analyse it
      setVictimStream(tabStream);

      // Combine for cleanup later
      const combinedStream = new MediaStream([...tabStream.getTracks(), ...micStream.getTracks()]);
      setStream(combinedStream);

      // Connect WebSocket
      const wsUrl = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000';
      const ws = new WebSocket(`${wsUrl}/api/live/stream`);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        const data: LivePayload = JSON.parse(event.data);
        if (data.svi !== undefined) setSviScore(data.svi);
        if (data.guidance) setGuidance(data.guidance);
        if (data.risk_detected !== undefined) setRiskDetected(data.risk_detected);
      };

      let victimInterval: NodeJS.Timeout;
      let officerInterval: NodeJS.Timeout;
      // DEEPGRAM INTEGRATION
      const DEEPGRAM_API_KEY = process.env.NEXT_PUBLIC_DEEPGRAM_API_KEY || '';
      // Use a chronological log array to interleave Officer and Victim sentences properly
      const dialogueLog: { speaker: string, text: string }[] = [];
      
      const setupDeepgramStream = (audioStream: MediaStream, speakerLabel: 'Victim' | 'Officer', langCode: string) => {
        // nova-2 does not support Bengali yet, so we fallback to the 'general' model for Bengali
        const modelToUse = langCode === 'bn' ? 'general' : 'nova-2';
        
        // Appended language flag to support the selected language flawlessly natively
        const dgWs = new WebSocket(`wss://api.deepgram.com/v1/listen?model=${modelToUse}&language=${langCode}`, [
          'token',
          DEEPGRAM_API_KEY
        ]);
        
        let recorder: MediaRecorder | null = null;
        
        dgWs.onopen = () => {
          // No hardcoded mimeType (fixes crashes on Safari/Brave if webm is unsupported)
          recorder = new MediaRecorder(audioStream);
          recorder.addEventListener('dataavailable', event => {
            if (event.data.size > 0 && dgWs.readyState === 1) {
              dgWs.send(event.data);
            }
          });
          recorder.start(250); // Stream 250ms chunks for instant transcription
        };
        
        dgWs.onerror = (e) => console.error('Deepgram WS Error for ' + speakerLabel, e);
        
        dgWs.onmessage = (message) => {
          const received = JSON.parse(message.data);
          const transcript = received.channel?.alternatives[0]?.transcript;
          if (transcript && received.is_final && transcript.trim().length > 0) {
            
            // Push to the chronological log
            dialogueLog.push({ speaker: speakerLabel, text: transcript.trim() });
            
            // Format for UI by interleaving the actual back-and-forth conversation
            const combined = dialogueLog.map(turn => `[${turn.speaker}]: ${turn.text}`).join('\n');
            setTranscript(combined);
            
            // Send to our backend Gemini AI every time a new sentence finishes
            if (wsRef.current?.readyState === WebSocket.OPEN) {
              wsRef.current.send(JSON.stringify({ full_transcript: combined }));
            }
          }
        };

        return {
          stop: () => {
            if (recorder?.state === 'recording') recorder.stop();
            if (dgWs.readyState === 1) dgWs.close();
          }
        };
      };

      let victimLoop: any;
      let officerLoop: any;

      ws.onopen = () => {
        setIsActive(true);
        victimLoop = setupDeepgramStream(tabStream, 'Victim', language);
        officerLoop = setupDeepgramStream(micStream, 'Officer', language);
        (ws as any).loops = [victimLoop, officerLoop];
      };

    } catch (err) {
      console.error('Failed to start live call:', err);
      alert('Could not access microphone/tab or connect to backend.');
    }
  };

  const stopCall = async () => {
    if (wsRef.current) {
      const loops = (wsRef.current as any).loops || [];
      loops.forEach((loop: any) => {
        if (loop && loop.stop) loop.stop();
      });
      wsRef.current.close();
    }
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    setVictimStream(null);
    setIsActive(false);

    // Save live case if transcript exists
    if (transcript && transcript.length > 5) {
      try {
        const token = localStorage.getItem('auth_token');
        const headers: Record<string, string> = {
          'Content-Type': 'application/json'
        };
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const riskLevel = sviScore >= 75 ? 'CRITICAL' : sviScore >= 40 ? 'MODERATE' : 'LOW';
        
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cases/live/save`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            transcript,
            language,
            final_svi: sviScore,
            risk_level: riskLevel,
            guidance
          })
        });
        if (res.ok) {
          const data = await res.json();
          alert(`Live call saved successfully! Case ID: ${data.anonymous_case_id}`);
        } else {
          console.error('Failed to save live case:', await res.text());
        }
      } catch (err) {
        console.error('Error saving live case:', err);
      }
    }
  };

  useEffect(() => {
    return () => {
      stopCall(); // Cleanup on unmount
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Call Analysis</h1>
          <p className="text-gray-600">Real-time STT and SVI Assessment for active crisis calls.</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Language:</span>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              disabled={isActive}
              className="bg-white border border-gray-200 text-gray-700 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2 outline-none shadow-sm disabled:opacity-50"
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="bn">Bengali</option>
            </select>
          </div>
          
          {isActive ? (
            <div className="flex items-center gap-2 text-red-600 bg-red-50 px-3 py-1.5 rounded-full font-medium text-sm animate-pulse">
              <Activity className="w-4 h-4" />
              Recording Active
            </div>
          ) : (
            <div className="flex items-center gap-2 text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full font-medium text-sm">
              <MicOff className="w-4 h-4" />
              Standby
            </div>
          )}
          
          <Button 
            variant={isActive ? 'destructive' : 'primary'} 
            onClick={isActive ? stopCall : startCall}
            className="flex items-center gap-2"
          >
            {isActive ? (
              <>
                <PhoneCall className="w-4 h-4" />
                End Call
              </>
            ) : (
              <>
                <Mic className="w-4 h-4" />
                Start Live Capture
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Transcript */}
        <div className="lg:col-span-2">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="border-b bg-gray-50/50 pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary-600" />
                Live Transcription
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-6 bg-gray-50 font-mono text-sm leading-relaxed whitespace-pre-wrap">
              {transcript ? (
                <div className="text-gray-800">
                  {transcript}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400 italic">
                  {isActive ? "Listening for audio..." : "Start a call to begin transcription."}
                </div>
              )}
              <div ref={transcriptEndRef} />
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Analytics & Guidance */}
        <div className="space-y-4">
          {/* SVI Gauge */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                Live SVI Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-4">
                <div className={`text-6xl font-black ${
                  sviScore >= 75 ? 'text-red-600' :
                  sviScore >= 40 ? 'text-amber-500' :
                  'text-emerald-500'
                }`}>
                  {sviScore}
                </div>
                <div className="text-sm text-gray-500 mt-2 font-medium">
                  {sviScore >= 75 ? 'CRITICAL RISK' :
                   sviScore >= 40 ? 'MODERATE RISK' : 'LOW RISK'}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Vocal Biomarkers — NEW */}
          <VocalStressMonitor isCallActive={isActive} victimStream={victimStream} />

          {/* Gemini Guidance */}
          <Card className={`border-2 transition-colors ${riskDetected ? 'border-red-200 bg-red-50' : 'border-blue-100 bg-blue-50/50'}`}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                {riskDetected ? (
                  <><AlertTriangle className="w-5 h-5 text-red-600" /> Immediate Actions (AI)</>
                ) : (
                  <><ShieldAlert className="w-5 h-5 text-blue-600" /> AI Guidance</>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {guidance.length > 0 ? (
                <ul className="space-y-3">
                  {guidance.map((tip, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${riskDetected ? 'text-red-500' : 'text-blue-500'}`} />
                      <span className={`text-sm ${riskDetected ? 'text-red-900 font-medium' : 'text-blue-900'}`}>{tip}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-sm text-gray-500 italic py-4 text-center">
                  Waiting for conversation context...
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

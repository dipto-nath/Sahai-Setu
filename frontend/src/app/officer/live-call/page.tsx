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

interface BioPayload {
  vocal_stress_score: number;
  biomarker_tags: string[];
}

export default function LiveCallPage() {
  const [isActive, setIsActive]       = useState(false);
  const [stream, setStream]           = useState<MediaStream | null>(null);
  const wsRef                         = useRef<WebSocket | null>(null);

  const [transcript, setTranscript]   = useState<string>('');
  const [sviScore, setSviScore]       = useState<number>(0);
  const [guidance, setGuidance]       = useState<string[]>([]);
  const [riskDetected, setRiskDetected] = useState<boolean>(false);
  const [language, setLanguage]       = useState<string>('hi');
  const transcriptEndRef              = useRef<HTMLDivElement>(null);

  // ── Vocal Biomarker state (owned here, passed down as props) ─────────────
  const [bioScore, setBioScore]       = useState<number>(0);
  const [bioTags, setBioTags]         = useState<string[]>([]);
  const [bioHistory, setBioHistory]   = useState<number[]>([]);
  const [bioConnected, setBioConnected] = useState<boolean>(false);
  const bioWsRef                      = useRef<WebSocket | null>(null);
  const bioRecorderRef                = useRef<MediaRecorder | null>(null);
  const bioBufRef                     = useRef<Blob[]>([]);
  const bioFlushRef                   = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [transcript]);

  // ── Start vocal biomarker streaming from victim's tab audio ──────────────
  function startBioStream(tabStream: MediaStream) {
    const wsBase = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
      .replace(/^https/, 'wss').replace(/^http/, 'ws');

    const bioWs = new WebSocket(`${wsBase}/api/live/audio-stream`);
    bioWsRef.current = bioWs;
    bioBufRef.current = [];

    bioWs.onopen = () => {
      setBioConnected(true);

      // Create a SEPARATE MediaRecorder specifically for biomarker analysis.
      // This does NOT conflict with Deepgram's recorder on the same stream.
      let recorder: MediaRecorder;
      try {
        recorder = new MediaRecorder(tabStream, { mimeType: 'audio/webm;codecs=opus' });
      } catch {
        recorder = new MediaRecorder(tabStream);
      }
      bioRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) bioBufRef.current.push(e.data);
      };
      recorder.start(250); // 250ms micro-chunks

      // Every 3 seconds flush the buffer and send raw bytes to backend
      bioFlushRef.current = setInterval(async () => {
        if (bioBufRef.current.length === 0 || bioWs.readyState !== WebSocket.OPEN) return;
        const blob = new Blob(bioBufRef.current, { type: 'audio/webm' });
        bioBufRef.current = [];
        const buf = await blob.arrayBuffer();
        bioWs.send(buf);
      }, 3000);
    };

    bioWs.onmessage = (event) => {
      try {
        const data: BioPayload = JSON.parse(event.data);
        const s = data.vocal_stress_score ?? 0;
        setBioScore(s);
        setBioTags(data.biomarker_tags ?? []);
        setBioHistory(prev => [...prev.slice(-29), s]);
      } catch { /* ignore */ }
    };

    bioWs.onerror = () => setBioConnected(false);
    bioWs.onclose = () => setBioConnected(false);
  }

  function stopBioStream() {
    bioFlushRef.current && clearInterval(bioFlushRef.current);
    if (bioRecorderRef.current?.state === 'recording') bioRecorderRef.current.stop();
    if (bioWsRef.current?.readyState === WebSocket.OPEN) bioWsRef.current.close();
    setBioConnected(false);
    bioWsRef.current = null;
    bioRecorderRef.current = null;
  }

  // ── Main call start ───────────────────────────────────────────────────────
  const startCall = async () => {
    try {
      // 1. Victim audio (tab/screen share)
      const tabStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });
      tabStream.getVideoTracks().forEach(t => t.stop());
      if (tabStream.getAudioTracks().length === 0) {
        alert("You must check 'Share tab audio' in the popup to capture the victim's audio.");
        tabStream.getTracks().forEach(t => t.stop());
        return;
      }

      // 2. Officer mic
      const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const combinedStream = new MediaStream([...tabStream.getTracks(), ...micStream.getTracks()]);
      setStream(combinedStream);

      // 3. Gemini guidance WebSocket
      const wsUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
        .replace(/^https/, 'wss').replace(/^http/, 'ws');
      const ws = new WebSocket(`${wsUrl}/api/live/stream`);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        const data: LivePayload = JSON.parse(event.data);
        if (data.svi !== undefined) setSviScore(data.svi);
        if (data.guidance) setGuidance(data.guidance);
        if (data.risk_detected !== undefined) setRiskDetected(data.risk_detected);
      };

      const DEEPGRAM_API_KEY = process.env.NEXT_PUBLIC_DEEPGRAM_API_KEY || '';
      const dialogueLog: { speaker: string; text: string }[] = [];

      const setupDeepgramStream = (audioStream: MediaStream, speakerLabel: 'Victim' | 'Officer', langCode: string) => {
        const modelToUse = langCode === 'bn' ? 'general' : 'nova-2';
        const dgWs = new WebSocket(
          `wss://api.deepgram.com/v1/listen?model=${modelToUse}&language=${langCode}`,
          ['token', DEEPGRAM_API_KEY]
        );
        let recorder: MediaRecorder | null = null;

        dgWs.onopen = () => {
          recorder = new MediaRecorder(audioStream);
          recorder.addEventListener('dataavailable', (e) => {
            if (e.data.size > 0 && dgWs.readyState === 1) dgWs.send(e.data);
          });
          recorder.start(250);
        };

        dgWs.onerror = (e) => console.error('Deepgram WS Error for ' + speakerLabel, e);

        dgWs.onmessage = (message) => {
          const received = JSON.parse(message.data);
          const t = received.channel?.alternatives[0]?.transcript;
          if (t && received.is_final && t.trim().length > 0) {
            dialogueLog.push({ speaker: speakerLabel, text: t.trim() });
            const combined = dialogueLog.map(d => `[${d.speaker}]: ${d.text}`).join('\n');
            setTranscript(combined);
            if (wsRef.current?.readyState === WebSocket.OPEN) {
              wsRef.current.send(JSON.stringify({ full_transcript: combined }));
            }
          }
        };

        return {
          stop: () => {
            if (recorder?.state === 'recording') recorder.stop();
            if (dgWs.readyState === 1) dgWs.close();
          },
        };
      };

      ws.onopen = () => {
        setIsActive(true);

        // Start Deepgram for transcription
        const victimLoop  = setupDeepgramStream(tabStream, 'Victim', language);
        const officerLoop = setupDeepgramStream(micStream, 'Officer', language);
        (ws as any).loops = [victimLoop, officerLoop];

        // ✅ Start vocal biomarker stream immediately — stream is guaranteed alive here
        startBioStream(tabStream);
      };
    } catch (err) {
      console.error('Failed to start live call:', err);
      alert('Could not access microphone/tab or connect to backend.');
    }
  };

  // ── Call stop ────────────────────────────────────────────────────────────
  const stopCall = async () => {
    // Stop Deepgram loops
    if (wsRef.current) {
      const loops = (wsRef.current as any).loops || [];
      loops.forEach((l: any) => l?.stop?.());
      wsRef.current.close();
    }
    // Stop biomarker stream
    stopBioStream();

    if (stream) stream.getTracks().forEach(t => t.stop());
    setIsActive(false);

    // Save live case
    if (transcript && transcript.length > 5) {
      try {
        const token = localStorage.getItem('auth_token');
        const headers: Record<string, string> = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const riskLevel = sviScore >= 75 ? 'CRITICAL' : sviScore >= 40 ? 'MODERATE' : 'LOW';
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cases/live/save`,
          {
            method: 'POST',
            headers,
            body: JSON.stringify({ transcript, language, final_svi: sviScore, risk_level: riskLevel, guidance }),
          }
        );
        if (res.ok) {
          const data = await res.json();
          alert(`Live call saved! Case ID: ${data.anonymous_case_id}`);
        }
      } catch (err) {
        console.error('Error saving live case:', err);
      }
    }
  };

  useEffect(() => {
    return () => { stopCall(); };
  }, []);

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
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
              <Activity className="w-4 h-4" /> Recording Active
            </div>
          ) : (
            <div className="flex items-center gap-2 text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full font-medium text-sm">
              <MicOff className="w-4 h-4" /> Standby
            </div>
          )}

          <Button
            variant={isActive ? 'destructive' : 'primary'}
            onClick={isActive ? stopCall : startCall}
            className="flex items-center gap-2"
          >
            {isActive ? <><PhoneCall className="w-4 h-4" /> End Call</> : <><Mic className="w-4 h-4" /> Start Live Capture</>}
          </Button>
        </div>
      </div>

      {/* ── Main Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Transcript */}
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
                <div className="text-gray-800">{transcript}</div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400 italic">
                  {isActive ? 'Listening for audio…' : 'Start a call to begin transcription.'}
                </div>
              )}
              <div ref={transcriptEndRef} />
            </CardContent>
          </Card>
        </div>

        {/* Right: Analytics */}
        <div className="space-y-3">

          {/* Row 1: SVI + Vocal Biomarkers side-by-side */}
          <div className="grid grid-cols-2 gap-3">

            {/* SVI Gauge */}
            <Card className="flex flex-col">
              <CardHeader className="pb-1 pt-3 px-3">
                <CardTitle className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Live SVI Score
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col items-center justify-center py-3 px-2">
                <div className={`text-5xl font-black leading-none ${
                  sviScore >= 75 ? 'text-red-600' : sviScore >= 40 ? 'text-amber-500' : 'text-emerald-500'
                }`}>
                  {sviScore}
                </div>
                <div className={`text-[10px] mt-1.5 font-semibold uppercase tracking-wide ${
                  sviScore >= 75 ? 'text-red-500' : sviScore >= 40 ? 'text-amber-500' : 'text-emerald-500'
                }`}>
                  {sviScore >= 75 ? 'CRITICAL' : sviScore >= 40 ? 'MODERATE' : 'LOW RISK'}
                </div>
                <div className="w-full mt-3 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      sviScore >= 75 ? 'bg-red-500' : sviScore >= 40 ? 'bg-amber-400' : 'bg-emerald-400'
                    }`}
                    style={{ width: `${sviScore}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Vocal Biomarkers — purely display, all logic in this file */}
            <VocalStressMonitor
              score={bioScore}
              tags={bioTags}
              history={bioHistory}
              connected={bioConnected}
              isCallActive={isActive}
              compact
            />
          </div>

          {/* Row 2: AI Guidance */}
          <Card className={`border-2 transition-colors ${
            riskDetected ? 'border-red-200 bg-red-50' : 'border-blue-100 bg-blue-50/50'
          }`}>
            <CardHeader className="pb-2 pt-3 px-4">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                {riskDetected ? (
                  <><AlertTriangle className="w-4 h-4 text-red-600" /> Immediate Actions (AI)</>
                ) : (
                  <><ShieldAlert className="w-4 h-4 text-blue-600" /> AI Guidance</>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-4">
              {guidance.length > 0 ? (
                <ul className="space-y-2">
                  {guidance.map((tip, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${riskDetected ? 'text-red-500' : 'text-blue-500'}`} />
                      <span className={`text-xs ${riskDetected ? 'text-red-900 font-medium' : 'text-blue-900'}`}>{tip}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-xs text-gray-400 italic py-2 text-center">
                  Waiting for conversation context…
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

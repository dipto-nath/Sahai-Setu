'use client';

/**
 * VocalStressMonitor
 * Connects to the backend WebSocket /api/live/audio-stream,
 * streams raw audio chunks via MediaRecorder, and visualises:
 *   1. A circular SVG Vocal Stress Gauge (0–100%)
 *   2. Real-time Biomarker Tags (chips that pop in/out)
 *   3. A 30-slot timeline bar that highlights red for high-stress moments
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Activity, Mic, MicOff } from 'lucide-react';

interface BiomarkerPayload {
  vocal_stress_score: number;   // 0-100
  biomarker_tags: string[];
  raw?: Record<string, number>;
}

const TAG_COLORS: Record<string, string> = {
  'Whispering / Hiding':          'bg-indigo-100 text-indigo-800 border-indigo-300',
  'Sudden Distress / Panic':      'bg-red-100 text-red-800 border-red-300',
  'Crying / Sobbing':             'bg-pink-100 text-pink-800 border-pink-300',
  'Hyperventilating / Rapid Speech': 'bg-orange-100 text-orange-800 border-orange-300',
  'Prolonged Silence / Shock':    'bg-yellow-100 text-yellow-800 border-yellow-300',
  'Screaming / High Pitch Alert': 'bg-red-200 text-red-900 border-red-400',
  'Monotone / Dissociation':      'bg-gray-100 text-gray-700 border-gray-300',
  'Calm / Stable':                'bg-emerald-100 text-emerald-800 border-emerald-300',
};

function scoreToColor(score: number): string {
  if (score >= 75) return '#ef4444';   // red-500
  if (score >= 40) return '#f59e0b';   // amber-500
  return '#10b981';                    // emerald-500
}

function scoreToLabel(score: number): string {
  if (score >= 75) return 'SEVERE STRESS';
  if (score >= 40) return 'MODERATE STRESS';
  return 'CALM / STABLE';
}

/** SVG circular gauge */
function StressGauge({ score }: { score: number }) {
  const r = 54;
  const circumference = 2 * Math.PI * r;
  const filled = (score / 100) * circumference;
  const color = scoreToColor(score);

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="140" height="140" viewBox="0 0 140 140">
        {/* track */}
        <circle cx="70" cy="70" r={r} fill="none" stroke="#e5e7eb" strokeWidth="12" />
        {/* progress — rotate so it starts at 12 o'clock */}
        <circle
          cx="70" cy="70" r={r}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={`${filled} ${circumference}`}
          strokeDashoffset={circumference / 4}
          style={{ transition: 'stroke-dasharray 0.5s ease, stroke 0.5s ease' }}
        />
        {/* label */}
        <text x="70" y="65" textAnchor="middle" className="text-3xl font-black" fontSize="28" fontWeight="900" fill={color}>
          {score}
        </text>
        <text x="70" y="85" textAnchor="middle" fontSize="10" fill="#6b7280">
          / 100
        </text>
      </svg>
      <span className="text-xs font-semibold tracking-wider uppercase" style={{ color }}>
        {scoreToLabel(score)}
      </span>
    </div>
  );
}

/** A 30-slot timeline bar */
function StressTimeline({ history }: { history: number[] }) {
  const MAX_SLOTS = 30;
  const slots = [...Array(MAX_SLOTS - history.length).fill(null), ...history].slice(-MAX_SLOTS);

  return (
    <div className="flex items-end gap-0.5 h-12">
      {slots.map((v, i) => {
        const bg = v === null
          ? 'bg-gray-100'
          : v >= 75 ? 'bg-red-500'
          : v >= 40 ? 'bg-amber-400'
          : 'bg-emerald-400';
        const height = v === null ? 6 : Math.max(8, (v / 100) * 48);
        return (
          <div
            key={i}
            className={`rounded-sm flex-1 transition-all duration-300 ${bg}`}
            style={{ height: `${height}px` }}
            title={v !== null ? `Stress: ${v}` : 'No data'}
          />
        );
      })}
    </div>
  );
}

interface Props {
  isCallActive: boolean;
  /** The victim's audio stream from tab-share, captured by parent */
  victimStream: MediaStream | null;
}

export default function VocalStressMonitor({ isCallActive, victimStream }: Props) {
  const [score, setScore] = useState(0);
  const [tags, setTags] = useState<string[]>([]);
  const [history, setHistory] = useState<number[]>([]);
  const [connected, setConnected] = useState(false);

  const wsRef       = useRef<WebSocket | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const bufferRef   = useRef<Blob[]>([]);
  const flushRef    = useRef<ReturnType<typeof setInterval> | null>(null);

  const stop = useCallback(() => {
    flushRef.current && clearInterval(flushRef.current);
    recorderRef.current?.state === 'recording' && recorderRef.current.stop();
    wsRef.current?.readyState === WebSocket.OPEN && wsRef.current.close();
    setConnected(false);
  }, []);

  const start = useCallback((stream: MediaStream) => {
    const wsBase = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
      .replace(/^https/, 'wss').replace(/^http/, 'ws');
    const ws = new WebSocket(`${wsBase}/api/live/audio-stream`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      bufferRef.current = [];

      // MediaRecorder collects audio chunks
      let recorder: MediaRecorder;
      try {
        recorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      } catch {
        recorder = new MediaRecorder(stream);
      }
      recorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) bufferRef.current.push(e.data);
      };
      recorder.start(250); // 250 ms micro-chunks

      // Every 3 seconds flush buffer → send a combined blob over WS
      flushRef.current = setInterval(async () => {
        if (bufferRef.current.length === 0 || ws.readyState !== WebSocket.OPEN) return;
        const blob = new Blob(bufferRef.current, { type: 'audio/webm' });
        bufferRef.current = [];
        const buf = await blob.arrayBuffer();
        ws.send(buf);
      }, 3000);
    };

    ws.onmessage = (event) => {
      try {
        const data: BiomarkerPayload = JSON.parse(event.data);
        setScore(data.vocal_stress_score ?? 0);
        setTags(data.biomarker_tags ?? []);
        setHistory(prev => [...prev.slice(-29), data.vocal_stress_score ?? 0]);
      } catch {/* ignore malformed */ }
    };

    ws.onerror = () => setConnected(false);
    ws.onclose = () => setConnected(false);
  }, []);

  // Start / stop automatically when call goes active and victim stream is ready
  useEffect(() => {
    if (isCallActive && victimStream) {
      start(victimStream);
    } else {
      stop();
      if (!isCallActive) {
        setScore(0);
        setTags([]);
        setHistory([]);
      }
    }
    return stop;
  }, [isCallActive, victimStream, start, stop]);

  return (
    <Card className="border border-gray-200">
      <CardHeader className="pb-3 border-b bg-gray-50/50">
        <CardTitle className="text-sm font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
          <Activity className="w-4 h-4 text-purple-500" />
          Vocal Biomarkers
          <span className={`ml-auto flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${
            connected ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'
          }`}>
            {connected ? <Mic className="w-3 h-3" /> : <MicOff className="w-3 h-3" />}
            {connected ? 'Analysing' : 'Inactive'}
          </span>
        </CardTitle>
      </CardHeader>

      <CardContent className="p-4 space-y-4">
        {/* Circular Gauge */}
        <div className="flex justify-center">
          <StressGauge score={score} />
        </div>

        {/* Biomarker Tags */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Detected Indicators
          </p>
          <div className="flex flex-wrap gap-1.5 min-h-[28px]">
            {tags.length > 0 ? tags.map(tag => (
              <span
                key={tag}
                className={`text-xs px-2 py-0.5 rounded-full border font-medium transition-all duration-300 ${
                  TAG_COLORS[tag] ?? 'bg-gray-100 text-gray-700 border-gray-300'
                }`}
              >
                {tag}
              </span>
            )) : (
              <span className="text-xs text-gray-400 italic">
                {isCallActive ? 'Awaiting audio…' : 'Start call to detect indicators'}
              </span>
            )}
          </div>
        </div>

        {/* Stress Timeline */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Stress Timeline (last 30 readings)
          </p>
          <StressTimeline history={history} />
          <div className="flex justify-between text-[10px] text-gray-400 mt-1">
            <span>Older</span>
            <span>Now</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

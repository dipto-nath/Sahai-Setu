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
function StressGauge({ score, size = 140 }: { score: number; size?: number }) {
  const r = size === 90 ? 34 : 54;
  const circumference = 2 * Math.PI * r;
  const filled = (score / 100) * circumference;
  const color = scoreToColor(score);
  const cx = size / 2;
  const cy = size / 2;
  const fontSize = size === 90 ? 18 : 28;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* track */}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e5e7eb" strokeWidth={size === 90 ? 8 : 12} />
        {/* progress */}
        <circle
          cx={cx} cy={cy} r={r}
          fill="none"
          stroke={color}
          strokeWidth={size === 90 ? 8 : 12}
          strokeLinecap="round"
          strokeDasharray={`${filled} ${circumference}`}
          strokeDashoffset={circumference / 4}
          style={{ transition: 'stroke-dasharray 0.5s ease, stroke 0.5s ease' }}
        />
        <text x={cx} y={cy - 4} textAnchor="middle" fontSize={fontSize} fontWeight="900" fill={color}>
          {score}
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle" fontSize={size === 90 ? 7 : 10} fill="#6b7280">
          / 100
        </text>
      </svg>
      <span className="text-[10px] font-semibold tracking-wider uppercase" style={{ color }}>
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
  /** Compact mode: smaller gauge, no timeline — for use in 2-col layouts */
  compact?: boolean;
}

export default function VocalStressMonitor({ isCallActive, victimStream, compact = false }: Props) {
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
    <Card className="border border-gray-200 flex flex-col">
      <CardHeader className={`border-b bg-gray-50/50 ${compact ? 'pb-2 pt-3 px-3' : 'pb-3'}`}>
        <CardTitle className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-purple-500" />
          Vocal Bio
          <span className={`ml-auto flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
            connected ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'
          }`}>
            {connected ? <Mic className="w-2.5 h-2.5" /> : <MicOff className="w-2.5 h-2.5" />}
            {connected ? 'On' : 'Off'}
          </span>
        </CardTitle>
      </CardHeader>

      <CardContent className={`flex-1 ${compact ? 'p-2 space-y-2' : 'p-4 space-y-4'}`}>
        {/* Gauge */}
        <div className="flex justify-center">
          <StressGauge score={score} size={compact ? 90 : 140} />
        </div>

        {/* Biomarker Tags */}
        <div>
          {!compact && (
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Detected Indicators
            </p>
          )}
          <div className="flex flex-wrap gap-1 min-h-[20px]">
            {tags.length > 0 ? tags.map(tag => (
              <span
                key={tag}
                className={`text-[10px] px-1.5 py-0.5 rounded-full border font-medium transition-all duration-300 leading-tight ${
                  TAG_COLORS[tag] ?? 'bg-gray-100 text-gray-700 border-gray-300'
                }`}
              >
                {tag}
              </span>
            )) : (
              <span className="text-[10px] text-gray-400 italic">
                {isCallActive ? 'Awaiting…' : 'Inactive'}
              </span>
            )}
          </div>
        </div>

        {/* Stress Timeline — hidden in compact mode */}
        {!compact && (
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
        )}
      </CardContent>
    </Card>
  );
}

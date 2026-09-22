'use client';

/**
 * VocalStressMonitor — PURE DISPLAY COMPONENT
 * Receives pre-computed data as props from page.tsx.
 * page.tsx owns all WebSocket + MediaRecorder logic so there are zero timing issues.
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Activity, Mic, MicOff } from 'lucide-react';

const TAG_COLORS: Record<string, string> = {
  'Whispering / Hiding':             'bg-indigo-100 text-indigo-800 border-indigo-300',
  'Sudden Distress / Panic':         'bg-red-100 text-red-800 border-red-300',
  'Crying / Sobbing':                'bg-pink-100 text-pink-800 border-pink-300',
  'Hyperventilating / Rapid Speech': 'bg-orange-100 text-orange-800 border-orange-300',
  'Prolonged Silence / Shock':       'bg-yellow-100 text-yellow-800 border-yellow-300',
  'Screaming / High Pitch Alert':    'bg-red-200 text-red-900 border-red-400',
  'Monotone / Dissociation':         'bg-gray-100 text-gray-700 border-gray-300',
  'Calm / Stable':                   'bg-emerald-100 text-emerald-800 border-emerald-300',
};

function scoreToColor(s: number) {
  return s >= 75 ? '#ef4444' : s >= 40 ? '#f59e0b' : '#10b981';
}
function scoreToLabel(s: number) {
  return s >= 75 ? 'SEVERE STRESS' : s >= 40 ? 'MODERATE' : 'CALM / STABLE';
}

function StressGauge({ score, size = 140 }: { score: number; size?: number }) {
  const r = size === 90 ? 34 : 54;
  const circ = 2 * Math.PI * r;
  const filled = (score / 100) * circ;
  const color = scoreToColor(score);
  const cx = size / 2, cy = size / 2;
  const fs = size === 90 ? 18 : 28;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e5e7eb" strokeWidth={size === 90 ? 8 : 12} />
        <circle
          cx={cx} cy={cy} r={r} fill="none" stroke={color}
          strokeWidth={size === 90 ? 8 : 12} strokeLinecap="round"
          strokeDasharray={`${filled} ${circ}`} strokeDashoffset={circ / 4}
          style={{ transition: 'stroke-dasharray 0.5s ease, stroke 0.5s ease' }}
        />
        <text x={cx} y={cy - 4} textAnchor="middle" fontSize={fs} fontWeight="900" fill={color}>{score}</text>
        <text x={cx} y={cy + 12} textAnchor="middle" fontSize={size === 90 ? 7 : 10} fill="#6b7280">/ 100</text>
      </svg>
      <span className="text-[10px] font-semibold tracking-wider uppercase" style={{ color }}>
        {scoreToLabel(score)}
      </span>
    </div>
  );
}

function StressTimeline({ history }: { history: number[] }) {
  const MAX = 30;
  const slots = [...Array(MAX - history.length).fill(null), ...history].slice(-MAX);
  return (
    <div className="flex items-end gap-0.5 h-10">
      {slots.map((v, i) => {
        const bg = v === null ? 'bg-gray-100'
          : v >= 75 ? 'bg-red-500' : v >= 40 ? 'bg-amber-400' : 'bg-emerald-400';
        const h = v === null ? 4 : Math.max(6, (v / 100) * 40);
        return <div key={i} className={`rounded-sm flex-1 transition-all duration-300 ${bg}`} style={{ height: `${h}px` }} />;
      })}
    </div>
  );
}

export interface VocalBiomarkerData {
  score: number;
  tags: string[];
  history: number[];
  connected: boolean;
}

interface Props extends VocalBiomarkerData {
  compact?: boolean;
  isCallActive: boolean;
}

export default function VocalStressMonitor({ score, tags, history, connected, compact = false, isCallActive }: Props) {
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
            {connected ? 'Live' : 'Off'}
          </span>
        </CardTitle>
      </CardHeader>

      <CardContent className={`flex-1 ${compact ? 'p-2 space-y-2' : 'p-4 space-y-4'}`}>
        <div className="flex justify-center">
          <StressGauge score={score} size={compact ? 90 : 140} />
        </div>

        <div>
          {!compact && (
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Detected Indicators
            </p>
          )}
          <div className="flex flex-wrap gap-1 min-h-[18px]">
            {tags.length > 0 ? tags.map(tag => (
              <span key={tag} className={`text-[10px] px-1.5 py-0.5 rounded-full border font-medium leading-tight ${
                TAG_COLORS[tag] ?? 'bg-gray-100 text-gray-700 border-gray-300'
              }`}>
                {tag}
              </span>
            )) : (
              <span className="text-[10px] text-gray-400 italic">
                {isCallActive ? 'Analysing…' : 'Inactive'}
              </span>
            )}
          </div>
        </div>

        {!compact && (
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Stress Timeline
            </p>
            <StressTimeline history={history} />
            <div className="flex justify-between text-[10px] text-gray-400 mt-1">
              <span>Older</span><span>Now</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

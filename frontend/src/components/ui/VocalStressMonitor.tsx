'use client';

import React, { useState, useEffect, useRef } from 'react';
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

interface Props {
  victimStream: MediaStream | null;
  compact?: boolean;
  isCallActive: boolean;
}

export default function VocalStressMonitor({ victimStream, compact = false, isCallActive }: Props) {
  const [score, setScore] = useState(0);
  const [tags, setTags] = useState<string[]>([]);
  const [history, setHistory] = useState<number[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!isCallActive || !victimStream) {
      setScore(0);
      setTags([]);
      setHistory([]);
      
      // Clear canvas
      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
      return;
    }

    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    const audioCtx = new AudioContextClass();
    const source = audioCtx.createMediaStreamSource(victimStream);
    const analyser = audioCtx.createAnalyser();
    
    analyser.fftSize = 2048;
    source.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const freqArray = new Uint8Array(bufferLength);

    let animationId: number;
    let lastUpdate = Date.now();
    let recentRms: number[] = [];
    let recentZcr: number[] = [];
    let recentCentroid: number[] = [];

    const draw = () => {
      animationId = requestAnimationFrame(draw);
      
      analyser.getByteTimeDomainData(dataArray);
      analyser.getByteFrequencyData(freqArray);
      
      // Calculate RMS (volume) & Zero-Crossing Rate (ZCR)
      let sumSquares = 0;
      let zcr = 0;
      for (let i = 0; i < bufferLength; i++) {
        const val = (dataArray[i] - 128) / 128;
        sumSquares += val * val;
        
        if (i > 0) {
          const prev = (dataArray[i - 1] - 128) / 128;
          if ((val >= 0 && prev < 0) || (val < 0 && prev >= 0)) zcr++;
        }
      }
      const rms = Math.sqrt(sumSquares / bufferLength);
      const zcrRate = zcr / bufferLength;
      
      recentRms.push(rms);
      if (recentRms.length > 120) recentRms.shift();
      recentZcr.push(zcrRate);
      if (recentZcr.length > 120) recentZcr.shift();
      
      // Calculate Spectral Centroid (Brightness/Pitch proxy)
      let num = 0;
      let den = 0;
      for (let i = 0; i < bufferLength; i++) {
        const magnitude = freqArray[i];
        num += i * magnitude;
        den += magnitude;
      }
      const centroid = den === 0 ? 0 : num / den;
      recentCentroid.push(centroid);
      if (recentCentroid.length > 120) recentCentroid.shift();
      
      // Draw live waveform on Canvas
      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.lineWidth = 2;
          ctx.strokeStyle = score >= 75 ? '#ef4444' : score >= 40 ? '#f59e0b' : '#10b981';
          ctx.beginPath();
          
          const sliceWidth = canvas.width * 1.0 / bufferLength;
          let x = 0;
          
          for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * (canvas.height / 2);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
            x += sliceWidth;
          }
          ctx.lineTo(canvas.width, canvas.height / 2);
          ctx.stroke();
        }
      }
      
      // Every 1 second, calculate heuristics and update UI
      const now = Date.now();
      if (now - lastUpdate >= 1000) {
        lastUpdate = now;
        
        const avgRms = recentRms.reduce((a,b) => a+b, 0) / recentRms.length;
        const avgZcr = recentZcr.reduce((a,b) => a+b, 0) / recentZcr.length;
        const avgCentroid = recentCentroid.reduce((a,b) => a+b, 0) / recentCentroid.length;
        
        // Count rapid spikes (proxy for hyperventilation/panic onsets)
        let spikes = 0;
        for (let i = 1; i < recentRms.length; i++) {
          if (recentRms[i] > avgRms * 1.5 && recentRms[i-1] <= avgRms * 1.5) spikes++;
        }
        
        let newTags: string[] = [];
        let newScore = 0;
        
        // Advanced Speech Heuristics
        if (avgRms < 0.005) {
          newTags.push('Prolonged Silence / Shock');
          newScore = 60;
        } else if (avgRms > 0.005 && avgRms < 0.08 && avgZcr > 0.15) {
          // Whispering: Low/Moderate Volume + High ZCR (Unvoiced/Fricative heavy)
          newTags.push('Whispering / Hiding');
          newScore = 50;
        } else if (avgRms > 0.25 || (avgRms > 0.15 && avgCentroid > bufferLength * 0.25)) {
          // Screaming: Very loud OR somewhat loud but very bright/high-pitch (Shrieking)
          newTags.push('Screaming / High Pitch Alert');
          newScore = 95;
        } else if (avgRms > 0.15) {
          newTags.push('Sudden Distress / Panic');
          newScore = 75;
        }
        
        if (spikes > 10 && avgRms > 0.03) {
          newTags.push('Hyperventilating / Rapid Speech');
          newScore = Math.max(newScore, 70);
        }
        
        if (newTags.length === 0) {
          newTags.push('Calm / Stable');
          newScore = 15;
        }
        
        setScore(newScore);
        setTags(newTags);
        setHistory(prev => [...prev.slice(-29), newScore]);
      }
    };
    
    draw();
    
    return () => {
      cancelAnimationFrame(animationId);
      audioCtx.close();
    };
  }, [isCallActive, victimStream, score]); // score is in dep array so waveform color updates live

  return (
    <Card className="border border-gray-200 flex flex-col overflow-hidden relative">
      <CardHeader className={`border-b bg-gray-50/50 relative z-10 ${compact ? 'pb-2 pt-3 px-3' : 'pb-3'}`}>
        <CardTitle className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-purple-500" />
          Vocal Bio
          <span className={`ml-auto flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
            isCallActive && victimStream ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'
          }`}>
            {isCallActive && victimStream ? <Mic className="w-2.5 h-2.5" /> : <MicOff className="w-2.5 h-2.5" />}
            {isCallActive && victimStream ? 'Live WebAudio' : 'Off'}
          </span>
        </CardTitle>
      </CardHeader>

      <CardContent className={`flex-1 relative z-10 ${compact ? 'p-2 space-y-2' : 'p-4 space-y-4'}`}>
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
      
      {/* Live Waveform Canvas at the very bottom overlapping the card background */}
      <canvas 
        ref={canvasRef} 
        width={300} 
        height={60} 
        className="absolute bottom-0 left-0 w-full opacity-30 pointer-events-none"
      />
    </Card>
  );
}

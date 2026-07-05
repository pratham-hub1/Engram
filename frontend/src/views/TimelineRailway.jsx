import React from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { queryMemory } from '../api/client';
import { History, GitCommit } from 'lucide-react';

export default function TimelineRailway() {
  const { data, error, isLoading } = useSWR('/query?intent=history', () => queryMemory('history'));

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', display: 'flex', justifyContent: 'center' }}>
        <div className="pulse-indicator" style={{ width: 24, height: 24, animationDuration: '1.5s', backgroundColor: 'var(--accent-primary)' }} />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', color: 'var(--accent-danger)' }}>Error loading timeline.</div>
    );
  }

  // Strict JSON: { "data": [ {"date": "...", "event": "..."} ] }
  // Defensive check against LLM occasionally returning { raw_response: "..." }
  let events = [];
  if (Array.isArray(data?.data)) {
    events = data.data;
  } else if (data?.data?.raw_response) {
    events = [{ date: 'Recent', event: data.data.raw_response }];
  } else if (typeof data?.data === 'string') {
    events = [{ date: 'Recent', event: data.data }];
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
        <History color="var(--text-main)" size={20} />
        <h2 className="heading-primary" style={{ margin: 0, fontSize: '1.25rem' }}>Project Milestones</h2>
      </div>

      <div style={{ position: 'relative', flex: 1, paddingLeft: '2rem' }}>
        {/* The Central SVG Railway Track */}
        <div style={{ position: 'absolute', left: '26px', top: 0, bottom: 0, width: '2px', background: 'linear-gradient(to bottom, var(--accent-primary), rgba(94, 67, 255, 0.1))' }}></div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {events.length === 0 ? (
            <div style={{ color: 'var(--text-muted)' }}>No historical events found.</div>
          ) : (
            events.map((ev, idx) => (
              <div key={idx} style={{ position: 'relative', paddingLeft: '1.5rem', animation: `fadeIn 0.5s ease ${idx * 0.1}s forwards`, opacity: 0 }}>
                {/* Node Dot */}
                <div style={{ position: 'absolute', left: '-12px', top: '4px', width: '10px', height: '10px', borderRadius: '50%', background: '#fff', border: '2px solid var(--accent-primary)', zIndex: 2 }}></div>
                
                <div className="text-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                  {ev.date}
                </div>
                <div style={{ fontSize: '1rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                  {ev.event}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      
      <style>{`
        @keyframes fadeIn {
          to { opacity: 1; }
        }
      `}</style>
    </div>
  );
}

import React from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { queryMemory } from '../api/client';
import { BookOpen, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function RecentDecisionsGrid() {
  const { data, error, isLoading } = useSWR('/query?intent=decision', () => queryMemory('decision'));

  if (isLoading) {
    return (
      <GlassCard style={{ padding: '2rem', display: 'flex', justifyContent: 'center' }}>
        <div className="pulse-indicator" style={{ width: 24, height: 24, animationDuration: '1.5s', backgroundColor: 'var(--accent-primary)' }} />
      </GlassCard>
    );
  }

  if (error) {
    return (
      <GlassCard style={{ padding: '2rem', borderColor: 'var(--accent-danger)', background: 'rgba(217, 83, 79, 0.1)' }}>
        <div style={{ color: 'var(--accent-danger)' }}>Error loading decisions.</div>
      </GlassCard>
    );
  }

  // The strict JSON contract expects: { "data": [ {"decision": "...", "reason": "...", "source": "...", "confidence": "Confirmed"} ] }
  // Defensive check against LLM occasionally returning { raw_response: "..." }
  let decisionsList = [];
  if (Array.isArray(data?.data)) {
    decisionsList = data.data;
  } else if (data?.data?.raw_response) {
    decisionsList = [{ source: 'System', confidence: 'Inferred', decision: 'AI Generation Fallback', reason: data.data.raw_response }];
  } else if (typeof data?.data === 'string') {
    decisionsList = [{ source: 'System', confidence: 'Inferred', decision: 'AI Generation Fallback', reason: data.data }];
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
        <BookOpen color="var(--text-main)" size={20} />
        <h2 className="heading-primary" style={{ margin: 0, fontSize: '1.25rem' }}>Neural Decisions</h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
        {decisionsList.length === 0 ? (
          <div style={{ color: 'var(--text-muted)' }}>No recent decisions captured.</div>
        ) : (
          decisionsList.map((item, idx) => (
            <GlassCard key={idx} style={{ 
              padding: '1.5rem', 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '1rem',
              backgroundImage: 'radial-gradient(rgba(0,0,0,0.03) 1px, transparent 1px)',
              backgroundSize: '10px 10px'
            }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span className="text-mono" style={{ fontSize: '0.8rem', color: 'var(--accent-primary)' }}>{item.source}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.5)', padding: '4px 8px', borderRadius: '12px' }}>
                  <div style={{ 
                    width: 8, height: 8, borderRadius: '50%', 
                    background: item.confidence === 'Confirmed' ? 'var(--accent-success)' : 'var(--accent-warning)',
                    animation: item.confidence !== 'Confirmed' ? 'pulse 2s infinite' : 'none'
                  }}></div>
                  <span className="text-mono" style={{ fontSize: '0.75rem', color: 'var(--text-main)' }}>{item.confidence}</span>
                </div>
              </div>

              <div>
                <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem', lineHeight: 1.4 }}>{item.decision}</div>
                <div style={{ fontSize: '0.95rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{item.reason}</div>
              </div>

            </GlassCard>
          ))
        )}
      </div>
      
      <style>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(224, 159, 62, 0.4); }
          70% { box-shadow: 0 0 0 6px rgba(224, 159, 62, 0); }
          100% { box-shadow: 0 0 0 0 rgba(224, 159, 62, 0); }
        }
      `}</style>
    </div>
  );
}

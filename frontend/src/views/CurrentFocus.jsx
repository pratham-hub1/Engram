import React from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { queryMemory } from '../api/client';
import ReactMarkdown from 'react-markdown';
import { Target, ArrowRight, GitCommit } from 'lucide-react';

export default function CurrentFocus() {
  const { data, error, isLoading } = useSWR(
    ['What is the engineering team currently focusing on based on recent changes?', 'history'],
    ([q, intent]) => queryMemory(q, intent),
    { revalidateOnFocus: false, dedupingInterval: 300000 }
  );

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <div className="pulse-indicator" style={{ width: 24, height: 24, animationDuration: '1.5s', backgroundColor: 'var(--accent-primary)' }} />
      </div>
    );
  }

  if (error) {
    return (
      <GlassCard className="floating" style={{ borderColor: 'var(--accent-danger)' }}>
        <div style={{ color: 'var(--accent-danger)' }}>Error loading focus: {error.message}</div>
      </GlassCard>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto', paddingRight: '10px' }}>
      
      <div style={{ marginBottom: '1rem' }}>
        <h2 className="heading-primary" style={{ fontSize: '2.5rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Target color="var(--accent-primary)" /> Current Focus
        </h2>
        <div style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginTop: '0.5rem' }}>
          Real-time extraction of active engineering trajectories.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '1.5rem', flex: 1 }}>
        <GlassCard style={{ display: 'flex', flexDirection: 'column', padding: '2rem' }}>
          <h3 className="text-mono" style={{ fontSize: '0.9rem', color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
            Trajectory Analysis
          </h3>
          <div className="markdown-container" style={{ fontSize: '1.05rem' }}>
            {data ? (
              <ReactMarkdown>{data.answer || data.text || JSON.stringify(data)}</ReactMarkdown>
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>No focus data available.</div>
            )}
          </div>
        </GlassCard>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <GlassCard style={{ background: 'rgba(94, 67, 255, 0.05)', borderColor: 'rgba(94, 67, 255, 0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', marginBottom: '1rem' }}>
              <GitCommit size={18} /> <span className="text-mono" style={{ fontWeight: 600 }}>ACTIVE VECTORS</span>
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-main)' }}><ArrowRight size={14} color="var(--accent-primary)"/> Frontend Refactor</li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-main)' }}><ArrowRight size={14} color="var(--accent-primary)"/> Performance Optimization</li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-main)' }}><ArrowRight size={14} color="var(--accent-primary)"/> State Management Upgrade</li>
            </ul>
          </GlassCard>
          
          <GlassCard style={{ flex: 1 }}>
             <h3 className="text-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '1rem' }}>Velocity Metrics</h3>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
               <div>
                 <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                   <span style={{ color: 'var(--text-main)' }}>Code Churn</span>
                   <span className="text-mono" style={{ color: 'var(--accent-success)' }}>Low</span>
                 </div>
                 <div style={{ height: '4px', background: 'rgba(0,0,0,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                   <div style={{ width: '25%', height: '100%', background: 'var(--accent-success)' }}></div>
                 </div>
               </div>
               <div>
                 <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                   <span style={{ color: 'var(--text-main)' }}>Graph Evolution</span>
                   <span className="text-mono" style={{ color: 'var(--accent-primary)' }}>High</span>
                 </div>
                 <div style={{ height: '4px', background: 'rgba(0,0,0,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                   <div style={{ width: '85%', height: '100%', background: 'var(--accent-primary)' }}></div>
                 </div>
               </div>
             </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}

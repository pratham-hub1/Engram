import React from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { queryMemory } from '../api/client';
import ReactMarkdown from 'react-markdown';
import { GitBranch, Layers } from 'lucide-react';

export default function ArchitectureEvolution() {
  const { data, error, isLoading } = useSWR(
    ['How has the architecture evolved over time? Explain the structural morphing.', 'history'],
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
        <div style={{ color: 'var(--accent-danger)' }}>Error loading architecture: {error.message}</div>
      </GlassCard>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto', paddingRight: '10px' }}>
      
      <div style={{ marginBottom: '1rem' }}>
        <h2 className="heading-primary" style={{ fontSize: '2.5rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <GitBranch color="var(--accent-primary)" /> Project Milestones
        </h2>
        <div style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginTop: '0.5rem' }}>
          High-level timeline of project milestones, git commits, and architectural decisions.
        </div>
      </div>

      <GlassCard style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
          <Layers size={20} /> <span className="text-mono" style={{ fontWeight: 600 }}>STRUCTURAL HISTORY</span>
        </div>
        <div className="markdown-container" style={{ fontSize: '1.05rem' }}>
          {data ? (
            <ReactMarkdown>{data.answer || data.text || JSON.stringify(data)}</ReactMarkdown>
          ) : (
            <div style={{ color: 'var(--text-muted)' }}>No architecture data available.</div>
          )}
        </div>
      </GlassCard>

    </div>
  );
}

import React from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { queryMemory } from '../api/client';
import ReactMarkdown from 'react-markdown';
import { Sparkles, Layers, Box, Zap } from 'lucide-react';

export default function ProjectOverview() {
  const { data, error, isLoading } = useSWR(
    ['Provide a high-level summary of the project architecture and recent state.', 'general'],
    ([q, intent]) => queryMemory(q, intent),
    { revalidateOnFocus: false, dedupingInterval: 300000 }
  );

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <div className="pulse-indicator" style={{ width: 24, height: 24, animationDuration: '1.5s' }} />
      </div>
    );
  }

  if (error) {
    return (
      <GlassCard className="floating" style={{ borderColor: 'var(--accent-danger)' }}>
        <div style={{ color: 'var(--accent-danger)' }}>Error loading overview: {error.message}</div>
      </GlassCard>
    );
  }

  // Parse markdown logic into structured Bento tiles for the demo
  const mockStats = [
    { label: 'Active Modules', value: '24', icon: Box },
    { label: 'Architectural Layers', value: '4', icon: Layers },
    { label: 'Neural Connections', value: '1,204', icon: Zap },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto', paddingRight: '10px' }}>
      
      <div style={{ marginBottom: '1rem' }}>
        <h2 className="heading-primary" style={{ fontSize: '2.5rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Sparkles color="var(--accent-primary)" /> Project Overview
        </h2>
        <div style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginTop: '0.5rem' }}>
          High-level architectural synthesis from the neural graph.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
        {mockStats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <GlassCard key={i} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
                <span className="text-mono" style={{ fontSize: '0.85rem', textTransform: 'uppercase' }}>{stat.label}</span>
                <Icon size={18} color="var(--accent-primary)" />
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>
                {stat.value}
              </div>
            </GlassCard>
          )
        })}
      </div>

      <GlassCard style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '2rem' }}>
        <h3 className="text-mono" style={{ fontSize: '0.9rem', color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
          Synthesis Report
        </h3>
        <div className="markdown-container" style={{ fontSize: '1.05rem' }}>
          {data ? (
            <ReactMarkdown>{data.answer || data.text || JSON.stringify(data)}</ReactMarkdown>
          ) : (
            <div style={{ color: 'var(--text-muted)' }}>No data available.</div>
          )}
        </div>
      </GlassCard>

    </div>
  );
}

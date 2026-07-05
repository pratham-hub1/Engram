import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { fetchHealthStats } from '../api/client';
import { ShieldCheck, CheckCircle2, Server } from 'lucide-react';

export default function MemoryHealth() {
  const { data, error, isLoading } = useSWR('/health/stats', fetchHealthStats);
  
  // Staggered sequential loading animation
  const [loadState, setLoadState] = useState(0);

  useEffect(() => {
    if (data) {
      setTimeout(() => setLoadState(1), 300);
      setTimeout(() => setLoadState(2), 700);
      setTimeout(() => setLoadState(3), 1100);
      setTimeout(() => setLoadState(4), 1500);
      setTimeout(() => setLoadState(5), 1900);
    }
  }, [data]);

  return (
    <GlassCard style={{ display: 'flex', flexDirection: 'column', padding: '1.5rem', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <Server color="var(--text-main)" size={20} />
        <h2 className="heading-primary" style={{ margin: 0, fontSize: '1.25rem' }}>System Integrity</h2>
      </div>

      {isLoading ? (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="pulse-indicator" style={{ width: 24, height: 24, backgroundColor: 'var(--accent-primary)' }} />
        </div>
      ) : error ? (
        <div style={{ color: 'var(--accent-danger)' }}>Failed to load integrity stats.</div>
      ) : data ? (
        <div className="text-mono" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.9rem' }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: loadState >= 1 ? 1 : 0, transform: loadState >= 1 ? 'translateY(0)' : 'translateY(10px)', transition: 'all 0.4s ease' }}>
            <span style={{ color: 'var(--text-muted)' }}>Graph Database</span>
            <span style={{ color: 'var(--accent-success)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckCircle2 size={16} /> Online
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: loadState >= 2 ? 1 : 0, transform: loadState >= 2 ? 'translateY(0)' : 'translateY(10px)', transition: 'all 0.4s ease' }}>
            <span style={{ color: 'var(--text-muted)' }}>Decisions Captured</span>
            <span style={{ color: 'var(--text-main)', fontWeight: 700 }}>{data.decisions_captured}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: loadState >= 3 ? 1 : 0, transform: loadState >= 3 ? 'translateY(0)' : 'translateY(10px)', transition: 'all 0.4s ease' }}>
            <span style={{ color: 'var(--text-muted)' }}>Documents Indexed</span>
            <span style={{ color: 'var(--text-main)', fontWeight: 700 }}>{data.documents_indexed}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: loadState >= 4 ? 1 : 0, transform: loadState >= 4 ? 'translateY(0)' : 'translateY(10px)', transition: 'all 0.4s ease' }}>
            <span style={{ color: 'var(--text-muted)' }}>Architectural Changes</span>
            <span style={{ color: 'var(--text-main)', fontWeight: 700 }}>{data.architectural_changes}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: loadState >= 5 ? 1 : 0, transform: loadState >= 5 ? 'translateY(0)' : 'translateY(10px)', transition: 'all 0.4s ease' }}>
            <span style={{ color: 'var(--text-muted)' }}>Pending 'Why' Notes</span>
            <span style={{ color: 'var(--text-main)', fontWeight: 700 }}>{data.pending_why_notes}</span>
          </div>

        </div>
      ) : null}
      
      {loadState >= 5 && (
        <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-success)', fontSize: '0.85rem' }}>
          <ShieldCheck size={16} /> <span className="text-mono">ALL SYSTEMS NOMINAL</span>
        </div>
      )}
    </GlassCard>
  );
}

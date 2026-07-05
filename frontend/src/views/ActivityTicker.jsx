import React, { useEffect, useRef } from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { fetchActivity } from '../api/client';
import { Activity } from 'lucide-react';

export default function ActivityTicker() {
  const { data, error, isLoading } = useSWR('/activity', fetchActivity, { refreshInterval: 5000 });
  const scrollRef = useRef(null);

  // Scroll to top when new data arrives
  useEffect(() => {
    if (scrollRef.current && data?.feed) {
      scrollRef.current.scrollTop = 0;
    }
  }, [data]);

  return (
    <GlassCard style={{ display: 'flex', flexDirection: 'column', padding: '1.5rem', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
        <Activity color="var(--accent-primary)" size={20} />
        <h2 className="heading-primary" style={{ margin: 0, fontSize: '1.25rem' }}>Live Heartbeat</h2>
      </div>

      <div 
        ref={scrollRef}
        style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', paddingRight: '0.5rem' }}
        className="hide-scrollbar"
      >
        {isLoading ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Listening...</div>
        ) : error ? (
          <div style={{ color: 'var(--accent-danger)' }}>Stream disconnected.</div>
        ) : data?.feed?.length === 0 ? (
          <div style={{ color: 'var(--text-muted)' }}>No recent activity.</div>
        ) : (
          data.feed.map((item, idx) => {
            const isNewest = idx === 0;
            
            // Color logic based on event type string
            let eventColor = 'var(--accent-primary)';
            const typeUpper = (item.event_type || '').toUpperCase();
            if (typeUpper.includes('MEMORY') || typeUpper.includes('SUCCESS') || typeUpper.includes('ADD')) {
              eventColor = 'var(--accent-success)';
            } else if (typeUpper.includes('BLOCKER') || typeUpper.includes('ERROR') || typeUpper.includes('FAIL')) {
              eventColor = 'var(--accent-danger)';
            } else if (typeUpper.includes('MODIFIED') || typeUpper.includes('UPDATE')) {
              eventColor = '#3b82f6'; // distinct blue for file modifications
            }

            return (
              <div key={idx} style={{ 
                display: 'flex', gap: '1rem', alignItems: 'flex-start',
                animation: 'fadeIn 0.5s ease',
                opacity: idx > 2 ? 0.6 : 1, // Fade out older items slightly
                padding: isNewest ? '12px' : '4px 12px',
                background: isNewest ? 'rgba(94, 67, 255, 0.05)' : 'transparent',
                borderRadius: '12px',
                border: isNewest ? '1px solid rgba(94, 67, 255, 0.2)' : '1px solid transparent',
                transition: 'all 0.3s ease'
              }}>
                <div className="text-mono" style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '2px', flexShrink: 0, width: '65px' }}>
                  {isNewest ? (
                    <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Just now</span>
                  ) : (
                    item.timestamp
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '4px' }}>
                    {isNewest && (
                       <div className="pulse-indicator" style={{ width: 8, height: 8, backgroundColor: eventColor }} />
                    )}
                    <div style={{ color: eventColor, fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      {item.event_type}
                    </div>
                  </div>
                  <div className="text-mono" style={{ color: 'var(--text-main)', fontSize: '0.85rem', wordBreak: 'break-word' }}>
                    {item.source_path}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
      
      <style>{`
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </GlassCard>
  );
}

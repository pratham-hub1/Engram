import React, { useState } from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { fetchProjectOnboarding } from '../api/client';
import { Rocket, Target, Clock, AlertTriangle, ChevronDown, ChevronUp, Zap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function HeroSection() {
  const { data, error, isLoading } = useSWR('/project/onboarding', fetchProjectOnboarding);
  const [expanded, setExpanded] = useState(false);

  return (
    <GlassCard style={{ display: 'flex', flexDirection: 'column', padding: '2rem', gridColumn: '1 / -1' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="heading-primary" style={{ margin: 0, fontSize: '3rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            Project: Engram
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '1rem' }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--accent-success)', animation: 'pulse 2s infinite' }}></div>
            <span className="text-mono" style={{ color: 'var(--accent-success)', fontWeight: 600, letterSpacing: '1px' }}>STATUS: ACTIVELY EVOLVING</span>
          </div>
        </div>
        
        {/* Onboarding Button */}
        <button 
          className="glass-btn glass-btn-primary" 
          onClick={() => setExpanded(!expanded)}
          style={{ padding: '1rem 2rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}
        >
          If I Joined This Project Today {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
      </div>

      {isLoading ? (
        <div style={{ marginTop: '2rem', color: 'var(--text-muted)' }}>Loading context...</div>
      ) : error ? (
        <div style={{ marginTop: '2rem', color: 'var(--accent-danger)' }}>Failed to load project onboarding data.</div>
      ) : data ? (
        <>
          <div style={{ marginTop: '2rem', paddingBottom: expanded ? '2rem' : 0, borderBottom: expanded ? '1px solid var(--border-glass)' : 'none' }}>
            
            {/* FULL WIDTH LAST CHANGE BANNER */}
            <div style={{ marginBottom: '2rem', background: 'rgba(255,255,255,0.4)', padding: '1.5rem', borderRadius: '16px', borderLeft: '4px solid var(--accent-primary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                  <Clock size={18} /> <span className="text-mono">LAST MEANINGFUL CHANGE</span>
                </div>
                <div className="text-mono" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  {data.last_change?.time || "Recently"}
                </div>
              </div>
              <div className="markdown-container" style={{ fontSize: '1.15rem', fontStyle: 'italic', lineHeight: 1.5, color: 'var(--text-main)' }}>
                <ReactMarkdown>{data.last_change?.quote || data.last_change}</ReactMarkdown>
              </div>
            </div>

            {/* HORIZONTAL CURRENT FOCUS GRID */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                <Target size={18} /> <span className="text-mono">CURRENT FOCUS</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                {(Array.isArray(data.current_focus) ? data.current_focus : []).map((focus, idx) => {
                  const isString = typeof focus === 'string';

                  return (
                    <div key={idx} className={`glass-panel ${isString ? 'hover-expand' : ''}`} style={{ 
                      padding: '1.25rem', 
                      borderRadius: '12px', 
                      background: 'rgba(255, 255, 255, 0.5)',
                      border: '1px solid rgba(0,0,0,0.03)',
                      cursor: 'default',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.75rem'
                    }}>
                      {isString ? (
                        <div className="line-clamp-2 markdown-container" style={{ fontSize: '1rem', lineHeight: 1.5, color: 'var(--text-main)' }}>
                          <ReactMarkdown>{focus}</ReactMarkdown>
                        </div>
                      ) : (
                        <>
                          <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)' }}>
                            {focus.title || 'Focus Area'}
                          </div>
                          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: 1.5, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {(Array.isArray(focus.details) ? focus.details : [focus.details].filter(Boolean)).map((detail, dIdx) => detail ? (
                              <li key={dIdx}><ReactMarkdown>{detail}</ReactMarkdown></li>
                            ) : null)}
                          </ul>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

          </div>

          {/* Fluid Expansion for Onboarding (Mini Bento) */}
          {expanded && (
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem', marginTop: '2rem', animation: 'fadeIn 0.3s ease' }}>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                
                {/* Welcome Message */}
                <div className="markdown-container" style={{ fontSize: '1.35rem', fontWeight: 600, color: 'var(--text-main)', lineHeight: 1.4 }}>
                  <ReactMarkdown>{data.welcome_message}</ReactMarkdown>
                </div>
                
                {/* Architecture Pill */}
                <div style={{ background: 'rgba(94, 67, 255, 0.1)', padding: '1rem 1.5rem', borderRadius: '12px', borderLeft: '3px solid var(--accent-primary)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', marginBottom: '0.75rem' }}>
                    <Rocket size={16} /> <span className="text-mono" style={{ fontSize: '0.85rem' }}>ARCHITECTURE</span>
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-main)', fontSize: '1rem', lineHeight: 1.5, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {(Array.isArray(data.current_architecture) ? data.current_architecture : [data.current_architecture].filter(Boolean)).map((item, idx) => (
                      <li key={idx}><ReactMarkdown>{item}</ReactMarkdown></li>
                    ))}
                  </ul>
                </div>

                {/* Constraint & Target Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ background: 'rgba(217, 83, 79, 0.1)', padding: '1.25rem', borderRadius: '12px', border: '1px solid rgba(217, 83, 79, 0.2)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-warning)', marginBottom: '0.75rem' }}>
                      <AlertTriangle size={16} /> <span className="text-mono" style={{ fontSize: '0.85rem' }}>BLOCKER</span>
                    </div>
                    <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-main)', fontSize: '0.95rem', lineHeight: 1.4, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {(Array.isArray(data.blocker) ? data.blocker : [data.blocker].filter(Boolean)).map((item, idx) => (
                        <li key={idx}><ReactMarkdown>{item}</ReactMarkdown></li>
                      ))}
                    </ul>
                  </div>

                  <div style={{ background: 'rgba(0, 166, 118, 0.1)', padding: '1.25rem', borderRadius: '12px', border: '1px solid rgba(0, 166, 118, 0.2)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-success)', marginBottom: '0.75rem' }}>
                      <Target size={16} /> <span className="text-mono" style={{ fontSize: '0.85rem' }}>NEXT TASK</span>
                    </div>
                    <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-main)', fontSize: '0.95rem', lineHeight: 1.4, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {(Array.isArray(data.next_task) ? data.next_task : [data.next_task].filter(Boolean)).map((item, idx) => (
                        <li key={idx}><ReactMarkdown>{item}</ReactMarkdown></li>
                      ))}
                    </ul>
                  </div>
                </div>

              </div>
              
              {/* Massive Metric Hero */}
              <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', background: 'rgba(255,255,255,0.4)', borderRadius: '16px', padding: '2rem' }}>
                <div className="text-mono" style={{ color: 'var(--text-muted)', marginBottom: '1rem', letterSpacing: '1px' }}>ESTIMATED ONBOARDING TIME</div>
                <div style={{ fontSize: '4.5rem', fontWeight: 800, color: 'var(--text-main)', lineHeight: 1 }}>
                  {data.onboarding_time_mins} <span style={{ fontSize: '1.5rem', fontWeight: 600 }}>MINS</span>
                </div>
                <div style={{ marginTop: '1rem', color: 'var(--accent-success)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                  <Zap size={20} /> (Saved: 48 Hours)
                </div>
              </div>

            </div>
          )}
        </>
      ) : null}
      
      <style>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(0, 166, 118, 0.4); }
          70% { box-shadow: 0 0 0 10px rgba(0, 166, 118, 0); }
          100% { box-shadow: 0 0 0 0 rgba(0, 166, 118, 0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </GlassCard>
  );
}

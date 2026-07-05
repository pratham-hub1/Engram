import React, { useState } from 'react';
import { LayoutDashboard, Search, BookOpen, GitBranch, Target, Clock, Network, Activity } from 'lucide-react';

const navItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'focus', label: 'Current Focus', icon: Target },
  { id: 'timeline', label: 'Timeline', icon: Clock },
  { id: 'architecture', label: 'Architecture', icon: GitBranch },
  { id: 'health', label: 'Health', icon: Activity },
  { id: 'decisions', label: 'Decisions', icon: BookOpen },
  { id: 'ask', label: 'Ask Project', icon: Search },
  { id: 'graph', label: 'Neural Graph', icon: Network },
];

export default function Sidebar({ activeView, setActiveView }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div 
      className="glass-panel"
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
      style={{ 
        position: 'fixed',
        left: '20px',
        top: '50%',
        transform: 'translateY(-50%)',
        width: isExpanded ? '200px' : '64px',
        display: 'flex', 
        flexDirection: 'column', 
        padding: '1rem 0.5rem', 
        borderRadius: '24px', 
        zIndex: 1000,
        gap: '0.5rem',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
      }}
    >
      <div style={{ padding: '0 0.5rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: isExpanded ? 'flex-start' : 'center' }}>
        <div style={{ width: '32px', height: '32px', borderRadius: '12px', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <Network size={18} color="#fff" />
        </div>
        {isExpanded && <span style={{ marginLeft: '12px', fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)' }}>Memory</span>}
      </div>
      
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', overflow: 'hidden' }}>
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: isExpanded ? 'flex-start' : 'center',
                padding: '0.75rem',
                borderRadius: '16px',
                background: isActive ? 'rgba(255,255,255,0.7)' : 'transparent',
                border: 'none',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-muted)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s ease',
                fontWeight: isActive ? 600 : 500,
                boxShadow: isActive ? '0 4px 12px rgba(0,0,0,0.05)' : 'none'
              }}
              onMouseEnter={(e) => {
                if(!isActive) {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.4)';
                  e.currentTarget.style.color = 'var(--text-main)';
                }
              }}
              onMouseLeave={(e) => {
                if(!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-muted)';
                }
              }}
            >
              <Icon size={20} style={{ flexShrink: 0 }} />
              {isExpanded && (
                <span style={{ marginLeft: '12px', whiteSpace: 'nowrap', fontSize: '0.9rem' }}>
                  {item.label}
                </span>
              )}
            </button>
          )
        })}
      </nav>
    </div>
  );
}

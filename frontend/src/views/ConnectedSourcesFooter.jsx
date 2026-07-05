import React from 'react';
import { GitBranch, FileText, Book, StickyNote, Settings, Code, Network } from 'lucide-react';

export default function ConnectedSourcesFooter() {
  const sources = [
    { name: 'Git', icon: GitBranch },
    { name: 'README', icon: FileText },
    { name: 'Docs', icon: Book },
    { name: 'Notes', icon: StickyNote },
    { name: 'Config', icon: Settings },
    { name: 'Codebase', icon: Code },
    { name: 'Cognee', icon: Network }
  ];

  return (
    <div style={{ 
      gridColumn: '1 / -1', 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      gap: '2.5rem', 
      padding: '2rem 0',
      borderTop: '1px solid var(--border-glass)',
      marginTop: '1rem',
      opacity: 0.8
    }}>
      <div className="text-mono" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', letterSpacing: '1px' }}>
        CONNECTED SOURCES
      </div>
      
      <div style={{ display: 'flex', gap: '2rem' }}>
        {sources.map((source, idx) => {
          const Icon = source.icon;
          return (
            <div key={idx} style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              gap: '0.5rem',
              color: 'var(--text-muted)',
              transition: 'all 0.2s ease',
              cursor: 'default'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = 'var(--accent-primary)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--text-muted)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
            >
              <Icon size={20} />
              <span className="text-mono" style={{ fontSize: '0.75rem' }}>{source.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

import React from 'react';

export default function GlassCard({ children, className = '', title, action }) {
  return (
    <div className={`glass-panel p-6 flex flex-col ${className}`} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
      {(title || action) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          {title && <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-main)' }}>{title}</h3>}
          {action && <div>{action}</div>}
        </div>
      )}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {children}
      </div>
    </div>
  );
}

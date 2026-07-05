import React, { useState } from 'react';
import HeroSection from './views/HeroSection';
import AskYourProject from './views/AskYourProject';
import RecentDecisionsGrid from './views/RecentDecisionsGrid';
import TimelineRailway from './views/TimelineRailway';
import MemoryHealth from './views/MemoryHealth';
import ActivityTicker from './views/ActivityTicker';
import ConnectedSourcesFooter from './views/ConnectedSourcesFooter';
import MemorySummaryGraph from './views/MemorySummaryGraph';
import { Network, Command, Brain, GitMerge } from 'lucide-react';

export default function App() {
  const [activeView, setActiveView] = useState('mission'); // 'mission', 'ledger', 'evolution'

  const NavPill = ({ id, icon: Icon, label }) => (
    <button
      onClick={() => setActiveView(id)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.75rem 1.5rem',
        borderRadius: '20px',
        border: 'none',
        cursor: 'pointer',
        background: activeView === id ? 'var(--accent-primary)' : 'transparent',
        color: activeView === id ? '#fff' : 'var(--text-main)',
        fontWeight: activeView === id ? 600 : 500,
        transition: 'all 0.3s ease',
        fontSize: '0.95rem'
      }}
    >
      <Icon size={18} />
      {label}
    </button>
  );

  return (
    <div style={{ position: 'relative', height: '100vh', width: '100vw', overflowY: 'auto', overflowX: 'hidden' }}>
      
      {/* Top Navbar & Floating Deck */}
      <nav style={{ 
        padding: '1.5rem 3rem', 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center', 
        background: 'rgba(255,255,255,0.2)', 
        backdropFilter: 'blur(10px)', 
        borderBottom: '1px solid var(--border-glass)', 
        position: 'sticky', 
        top: 0, 
        zIndex: 100 
      }}>
        
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '12px', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Network size={20} color="#fff" />
          </div>
          <span style={{ fontWeight: 800, fontSize: '1.25rem', color: 'var(--text-main)', letterSpacing: '-0.5px' }}>Engram</span>
        </div>

        {/* The Floating Command Deck (Segmented Picker) */}
        <div style={{ 
          display: 'flex', 
          background: 'rgba(255,255,255,0.5)', 
          padding: '4px', 
          borderRadius: '24px',
          border: '1px solid rgba(255,255,255,0.8)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
        }}>
          <NavPill id="mission" icon={Command} label="Mission Control" />
          <NavPill id="ledger" icon={Brain} label="Neural Ledger" />
          <NavPill id="evolution" icon={GitMerge} label="Milestones" />
          <NavPill id="graph" icon={Network} label="Neural Graph" />
        </div>

        <div style={{ width: 100 }}></div> {/* Spacer to balance logo */}
      </nav>

      {/* Main Content Area */}
      <main style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '3rem',
        animation: 'fadeIn 0.3s ease'
      }} key={activeView}>
        
        {activeView === 'mission' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '2rem' }}>
            <div style={{ gridColumn: 'span 12' }}>
              <HeroSection />
            </div>
            <div style={{ gridColumn: 'span 8' }}>
              <AskYourProject />
            </div>
            <div style={{ gridColumn: 'span 4', height: '400px' }}>
              <ActivityTicker />
            </div>
          </div>
        )}

        {activeView === 'ledger' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '2rem' }}>
            <div style={{ gridColumn: 'span 8', minHeight: '600px' }}>
              <RecentDecisionsGrid />
            </div>
            <div style={{ gridColumn: 'span 4', height: '400px' }}>
              <MemoryHealth />
            </div>
          </div>
        )}

        {activeView === 'evolution' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
            <div style={{ minHeight: '600px', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
              <TimelineRailway />
            </div>
            <ConnectedSourcesFooter />
          </div>
        )}

        {activeView === 'graph' && (
          <div style={{ width: '100%', height: 'calc(100vh - 220px)', minHeight: '600px', background: 'rgba(255,255,255,0.4)', borderRadius: '24px', padding: '1rem' }}>
            <MemorySummaryGraph />
          </div>
        )}

      </main>
      
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

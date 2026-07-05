import React, { useState } from 'react';
import useSWR from 'swr';
import GlassCard from '../components/GlassCard';
import { queryMemory, captureDecisionNote } from '../api/client';
import { BookOpen, Plus, Loader2, GitCommit } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function RecentDecisions() {
  const { data: decisions, isLoading: loading, mutate } = useSWR(
    ['List all recent architectural decisions and their reasoning.', 'decision'],
    ([q, intent]) => queryMemory(q, intent),
    { revalidateOnFocus: false, dedupingInterval: 300000 }
  );
  
  const [newNote, setNewNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    setSubmitting(true);
    try {
      await captureDecisionNote(newNote);
      setNewNote('');
      await mutate(); // refresh
    } catch (err) {
      alert(`Failed to save note: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', maxWidth: '800px', margin: '0 auto', width: '100%', overflowY: 'auto', paddingRight: '10px', paddingBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 className="heading-primary" style={{ margin: 0, fontSize: '2.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <BookOpen color="var(--accent-primary)" /> Architectural Decisions
          </h2>
          <div style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginTop: '0.5rem' }}>
            Human-in-the-loop context backfilling.
          </div>
        </div>
        {loading && <div className="pulse-indicator" style={{ backgroundColor: 'var(--accent-primary)' }} />}
      </div>

      <GlassCard className="floating" style={{ padding: '1rem', border: '1px solid var(--accent-primary)', background: 'rgba(255, 255, 255, 0.6)' }}>
        <form onSubmit={handleAddNote} style={{ display: 'flex', gap: '1rem' }}>
          <input 
            type="text" 
            placeholder="Log an architectural decision (e.g. Switched to Vite because...)" 
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            style={{ 
              flex: 1, 
              background: 'rgba(255, 255, 255, 0.5)', 
              border: '1px solid var(--border-glass)', 
              borderRadius: '8px', 
              padding: '0.75rem 1rem',
              color: 'var(--text-main)',
              fontFamily: 'var(--font-mono)',
              outline: 'none'
            }} 
          />
          <button 
            type="submit" 
            className="glass-btn glass-btn-primary" 
            disabled={submitting || !newNote.trim()}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem' }}
          >
            {submitting ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Plus size={18} />}
            Capture Node
          </button>
        </form>
      </GlassCard>

      <GlassCard style={{ flex: 1, padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
          <GitCommit size={20} /> <span className="text-mono" style={{ fontWeight: 600 }}>DECISION LEDGER</span>
        </div>
        {loading && !decisions ? (
          <div style={{ color: 'var(--text-muted)' }}>Retrieving from Memory Pipeline...</div>
        ) : decisions ? (
          <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }} className="markdown-container">
            {decisions.answer || decisions.text ? (
              <ReactMarkdown>{decisions.answer || decisions.text}</ReactMarkdown>
            ) : (
              JSON.stringify(decisions, null, 2)
            )}
            
            {decisions.sources && (
              <div style={{ marginTop: '2rem' }}>
                <h4 className="text-mono" style={{ fontSize: '0.85rem', color: 'var(--accent-primary)', textTransform: 'uppercase', marginBottom: '1rem' }}>
                  Linked Neural Evidence
                </h4>
                {decisions.sources.map((s, idx) => (
                  <div key={idx} className="text-mono" style={{ 
                    padding: '1rem', 
                    background: 'rgba(255, 255, 255, 0.5)', 
                    borderRadius: '8px', 
                    borderLeft: '2px solid var(--accent-primary)',
                    marginBottom: '0.5rem',
                    fontSize: '0.85rem',
                    color: 'var(--text-muted)',
                    border: '1px solid rgba(0,0,0,0.05)'
                  }}>
                    {s}
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)' }}>No decisions found in memory.</div>
        )}
      </GlassCard>
      
      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

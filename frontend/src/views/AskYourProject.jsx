import React, { useState, useEffect } from 'react';
import GlassCard from '../components/GlassCard';
import { queryMemory } from '../api/client';
import { Search, Info } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function AskYourProject() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [visibleNodes, setVisibleNodes] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const inputRef = React.useRef(null);

  const loadingPhrases = [
    "Initializing...",
    "Querying graph...",
    "Analyzing vectors...",
    "Synthesizing nodes...",
    "Aggregating paths...",
    "Formatting response..."
  ];

  // Rotate loading phrases
  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep(prev => (prev < loadingPhrases.length - 1 ? prev + 1 : prev));
      }, 1800);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // Command+K listener
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);
    setVisibleNodes(0);
    setShowAnswer(false);
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/query?intent=general&q=${encodeURIComponent(query)}`);
      const data = await res.json();
      const payload = data.data || data;
      
      setResults(payload);
      
      // The Hackathon Demo Stagger Effect
      if (payload.reasoning_path && payload.reasoning_path.length > 0) {
        payload.reasoning_path.forEach((_, index) => {
          setTimeout(() => {
            setVisibleNodes(index + 1);
          }, index * 800); // reveal one node every 800ms
        });
        
        setTimeout(() => {
          setShowAnswer(true);
        }, payload.reasoning_path.length * 800 + 400);
      } else {
        setShowAnswer(true);
      }
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePillClick = (q) => {
    setQuery(q);
    setTimeout(() => {
      const event = new Event('submit', { bubbles: true, cancelable: true });
      document.getElementById('ask-form').dispatchEvent(event);
    }, 50);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', gridColumn: '1 / -1' }}>
      <form id="ask-form" onSubmit={handleSearch} style={{ position: 'relative' }}>
        <div className="glass-panel" style={{ 
          display: 'flex', 
          alignItems: 'center', 
          padding: '1rem 1.5rem', 
          borderRadius: '24px', 
          background: 'rgba(255, 255, 255, 0.7)',
          boxShadow: '0 10px 30px rgba(0,0,0,0.05)',
          border: '1px solid rgba(255,255,255,0.8)'
        }}>
          <Search size={28} color="var(--accent-primary)" style={{ marginRight: '1rem' }} />
          <input 
            ref={inputRef}
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask your project..."
            style={{ 
              flex: 1, 
              background: 'transparent', 
              border: 'none', 
              color: 'var(--text-main)', 
              fontSize: '1.25rem',
              outline: 'none'
            }} 
          />
          <div className="text-mono" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', background: 'rgba(0,0,0,0.05)', padding: '4px 8px', borderRadius: '6px' }}>
            ⌘K
          </div>
        </div>
      </form>

      {/* Suggestion Pills */}
      {!results && !loading && (
        <div style={{ display: 'flex', gap: '0.75rem', paddingLeft: '1rem' }}>
          {["Why Cognee?", "Current Architecture?", "What is the observer doing?"].map((q, idx) => (
            <button key={idx} onClick={() => handlePillClick(q)} className="glass-btn" style={{ fontSize: '0.9rem', padding: '6px 12px', borderRadius: '20px' }}>
              {q}
            </button>
          ))}
        </div>
      )}

      {loading && (
        <GlassCard style={{ padding: '3rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1.5rem', animation: 'fadeIn 0.3s ease' }}>
          <div style={{ position: 'relative', width: '60px', height: '60px' }}>
            <div className="pulse-indicator" style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, margin: 'auto', width: '100%', height: '100%', animationDuration: '1.5s', backgroundColor: 'var(--accent-primary)', opacity: 0.2 }} />
            <div className="pulse-indicator" style={{ position: 'absolute', top: '15px', left: '15px', width: '30px', height: '30px', animationDuration: '1s', backgroundColor: 'var(--accent-primary)' }} />
          </div>
          <div className="text-mono" style={{ color: 'var(--accent-primary)', fontSize: '1.1rem', letterSpacing: '1px', fontWeight: 600 }}>
            {loadingPhrases[loadingStep].toUpperCase()}
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', transition: 'all 0.3s ease' }}>
            {loadingStep < 2 ? "Accessing local-first AI memory layer" : "Synthesizing multi-hop memory paths"}
          </div>
        </GlassCard>
      )}

      {error && (
        <GlassCard style={{ borderColor: 'var(--accent-danger)', background: 'rgba(217, 83, 79, 0.1)' }}>
          <div style={{ color: 'var(--accent-danger)' }}>System Error: {error}</div>
        </GlassCard>
      )}

      {/* Answer Panel */}
      {results && !loading && (
        <GlassCard style={{ animation: 'fadeIn 0.4s ease', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* 1. Show the staggered reasoning trace FIRST */}
          {results.reasoning_path && results.reasoning_path.length > 0 && (
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center', paddingBottom: showAnswer ? '1.5rem' : '0', borderBottom: showAnswer ? '1px solid var(--border-glass)' : 'none', transition: 'all 0.4s ease' }}>
              <div style={{width: '100%', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.25rem'}}>Reasoning Trace:</div>
              {results.reasoning_path.slice(0, visibleNodes).map((step, idx) => (
                <React.Fragment key={idx}>
                  <div className="source-badge" style={{ 
                    display: 'flex', alignItems: 'center', gap: '0.5rem',
                    padding: '6px 12px', background: 'rgba(255, 255, 255, 0.8)', 
                    borderRadius: '8px', border: '1px solid var(--accent-primary)',
                    fontSize: '0.85rem', color: 'var(--text-main)', cursor: 'default',
                    position: 'relative', boxShadow: '0 0 15px rgba(94, 67, 255, 0.3)',
                    animation: 'fadeIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
                  }}>
                    <Info size={14} color="var(--accent-primary)" />
                    <span style={{fontWeight: 600, color: 'var(--accent-primary)', textTransform: 'capitalize'}}>{step.type}:</span> {step.name}
                  </div>
                  {idx < results.reasoning_path.length - 1 && idx < visibleNodes - 1 && (
                    <div style={{ color: 'var(--accent-primary)', fontWeight: 'bold', animation: 'fadeIn 0.4s ease' }}>→</div>
                  )}
                </React.Fragment>
              ))}
              
              {/* Show a mini loading pulse while nodes are still popping in */}
              {visibleNodes < results.reasoning_path.length && (
                <div className="pulse-indicator" style={{ width: 12, height: 12, backgroundColor: 'var(--accent-primary)' }}></div>
              )}
            </div>
          )}

          {/* 2. Fade in the final answer AFTER nodes are done */}
          {showAnswer && (
            <div className="markdown-container" style={{ fontSize: '1.1rem', animation: 'fadeIn 0.6s ease' }}>
              <ReactMarkdown>{results.answer || "No answer returned."}</ReactMarkdown>
            </div>
          )}
          
        </GlassCard>
      )}
    </div>
  );
}

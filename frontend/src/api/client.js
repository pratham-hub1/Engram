export const API_BASE = 'http://127.0.0.1:8000/api';

/**
 * Custom fetch wrapper to handle errors and JSON parsing.
 */
async function fetchApi(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API Error ${res.status}: ${errorText}`);
    }

    return await res.json();
  } catch (error) {
    console.error(`[Engram API] Failed to fetch ${endpoint}:`, error);
    throw error;
  }
}

// Read-Only Endpoints
export const fetchProjectOnboarding = () => fetchApi('/project/onboarding');
export const fetchHealthStats = () => fetchApi('/health/stats');
export const fetchActivity = () => fetchApi('/activity');

export const queryMemory = (intent = 'general') => 
  fetchApi(`/query?intent=${intent}`);

// Write Endpoints
export const captureDecisionNote = (text) => 
  fetchApi('/notes', { method: 'POST', body: JSON.stringify({ text }) });

// "Crazy Cognee" Advanced Endpoints
export const triggerImprove = () => fetchApi('/memory/improve', { method: 'POST' });
export const triggerRootCause = (symptom) => 
  fetchApi('/memory/root-cause', { method: 'POST', body: JSON.stringify({ symptom }) });
export const triggerPrune = () => fetchApi('/memory/prune', { method: 'POST' });

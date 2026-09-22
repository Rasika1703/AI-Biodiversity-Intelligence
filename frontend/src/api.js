const BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* response had no JSON body */
    }
    throw new Error(detail);
  }
  return response.json();
}

export const api = {
  health: () => request('/health'),
  chat: (payload) => request('/chat', { method: 'POST', body: JSON.stringify(payload) }),
  sessions: () => request('/sessions'),
  session: (id) => request(`/sessions/${id}`),
  deleteSession: (id) => request(`/sessions/${id}`, { method: 'DELETE' }),
  metrics: (id) => request(`/metrics/${id}`),
  knowledgeStats: () => request('/knowledge/stats'),
  knowledgeSearch: (q, k = 6) => request(`/knowledge/search?q=${encodeURIComponent(q)}&k=${k}`),
  documents: () => request('/knowledge/documents'),
};

export function relativeTime(iso) {
  if (!iso) return '';
  const then = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : `${iso}Z`);
  const mins = Math.round((Date.now() - then.getTime()) / 60000);
  const time = then.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins} min ago`;
  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);
  if (then >= startOfToday) return `Today, ${time}`;
  const yesterday = new Date(startOfToday.getTime() - 86400000);
  if (then >= yesterday) return `Yesterday, ${time}`;
  return `${then.toLocaleDateString([], { month: 'short', day: 'numeric' })}, ${time}`;
}

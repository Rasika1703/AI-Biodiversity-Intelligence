import { useCallback, useEffect, useRef, useState } from 'react';
import { Menu, Settings, X } from 'lucide-react';
import { api } from './api.js';
import { Logo } from './illustrations.jsx';
import Sidebar from './components/Sidebar.jsx';
import Hero from './components/Hero.jsx';
import Composer from './components/Composer.jsx';
import Analysis from './components/Analysis.jsx';
import Clarify from './components/Clarify.jsx';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [tab, setTab] = useState('history');
  const [mode, setMode] = useState('text');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [online, setOnline] = useState(true);
  const [kbStats, setKbStats] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [drawer, setDrawer] = useState(false);
  const threadRef = useRef(null);

  const refreshSessions = useCallback(async () => {
    try {
      setSessions(await api.sessions());
    } catch {
      /* sidebar stays with last known list */
    }
  }, []);

  const refreshMetrics = useCallback(async (id) => {
    if (!id) {
      setMetrics(null);
      return;
    }
    try {
      setMetrics(await api.metrics(id));
    } catch {
      setMetrics(null);
    }
  }, []);

  useEffect(() => {
    let alive = true;
    async function ping() {
  try {
    const health = await api.health();
    if (!alive) return;
    setOnline(true);
    setKbStats(health.knowledge);
  } catch {
    if (alive) setOnline(false);
  }
}
    ping();
    const timer = setInterval(ping, 30000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  useEffect(() => {
    const el = threadRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);

  async function openSession(id) {
    setDrawer(false);
    if (id === sessionId) return;
    try {
      const detail = await api.session(id);
      setSessionId(id);
      setMessages(
        detail.messages.map((m) =>
          m.role === 'user'
            ? { role: 'user', content: m.content }
            : { role: 'assistant', payload: m.payload },
        ),
      );
      setError('');
      refreshMetrics(id);
    } catch (err) {
      setError(err.message);
    }
  }

  function newSession() {
    setSessionId(null);
    setMessages([]);
    setMetrics(null);
    setError('');
    setDrawer(false);
    setTab('history');
  }

  async function removeSession(id) {
    try {
      await api.deleteSession(id);
      if (id === sessionId) newSession();
      refreshSessions();
    } catch (err) {
      setError(err.message);
    }
  }

  async function send({ message = '', structured = null, force_analysis = false }) {
    if (busy) return;
    setBusy(true);
    setError('');

    const bubble =
      message ||
      (structured ? `Structured site payload (${Object.keys(structured).length} variables)` : '');
    setMessages((prev) => [...prev, { role: 'user', content: bubble }]);

    try {
      const payload = {
        session_id: sessionId,
        message,
        mode: structured ? 'structured' : 'text',
        force_analysis,
      };
      if (structured) payload.structured = structured;

      const data = await api.chat(payload);
      setSessionId(data.session_id);
      setMessages((prev) => [...prev, { role: 'assistant', payload: data }]);
      refreshSessions();
      refreshMetrics(data.session_id);
    } catch (err) {
      setError(err.message || 'Request failed. Is the API running on port 8000?');
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setBusy(false);
    }
  }

  const hasThread = messages.length > 0;

  return (
    <div className="app">
      <header className="brandbar">
        <button className="icon-btn menu-btn" onClick={() => setDrawer((v) => !v)} title="Menu">
          {drawer ? <X size={20} /> : <Menu size={20} />}
        </button>
        <span className="brand-mark">
          <Logo size={26} />
        </span>
        <div>
          <h1 className="brand-name">Darukaa.Earth</h1>
          <p className="brand-sub">AI Biodiversity Intelligence</p>
        </div>
      </header>

      <div className="topbar">
        <span className={`status-pill${online ? '' : ' is-offline'}`}>
          <i className="status-dot" />
          {online ? 'AI Online' : 'API offline'}
        </span>
        <button
          className="icon-btn"
          title="Knowledge base status"
          onClick={() => setTab('about')}
        >
          <Settings size={19} />
        </button>
      </div>

      {drawer && <div className="scrim" onClick={() => setDrawer(false)} />}

      <Sidebar
        open={drawer}
        tab={tab}
        onTab={setTab}
        sessions={sessions}
        activeId={sessionId}
        onSelect={openSession}
        onNew={newSession}
        onDelete={removeSession}
        metrics={metrics}
        kbStats={kbStats}
      />

      <main className="main">
        <div className="thread" ref={threadRef}>
          <div className="thread-inner">
            {!hasThread && <Hero onPick={(p) => send({ message: p })} busy={busy} />}

            {messages.map((m, i) =>
              m.role === 'user' ? (
                <div className="msg-user" key={i}>
                  <div>{m.content}</div>
                </div>
              ) : m.payload?.kind === 'clarify' ? (
                <Clarify
                  key={i}
                  data={m.payload}
                  busy={busy}
                  onAnswer={(answer) => send({ message: answer })}
                  onSkip={() =>
                    send({
                      message: 'Please analyse now with stated assumptions.',
                      force_analysis: true,
                    })
                  }
                />
              ) : (
                <Analysis key={i} data={m.payload} />
              ),
            )}

            {error && <div className="error-banner">{error}</div>}

            {busy && (
              <div className="msg-ai">
                <div className="card">
                  <span className="typing">
                    <i />
                    <i />
                    <i />
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        <Composer mode={mode} onMode={setMode} onSend={send} busy={busy} />
      </main>
    </div>
  );
}

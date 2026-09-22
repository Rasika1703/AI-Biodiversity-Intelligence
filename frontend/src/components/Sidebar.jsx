import { MessageSquare, Plus, Trash2 } from 'lucide-react';
import { relativeTime } from '../api.js';
import LiveMetrics from './LiveMetrics.jsx';
import About from './About.jsx';

const TABS = [
  { id: 'history', label: 'History' },
  { id: 'metrics', label: 'Live Metrics' },
  { id: 'about', label: 'About' },
];

export default function Sidebar({
  open,
  tab,
  onTab,
  sessions,
  activeId,
  onSelect,
  onNew,
  onDelete,
  metrics,
  kbStats,
}) {
  return (
    <aside className={`sidebar${open ? ' is-open' : ''}`}>
      <button className="new-analysis" onClick={onNew}>
        <Plus size={18} /> New Analysis
      </button>

      <div className="tabs" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            className="tab"
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => onTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'history' && (
        <div className="panel" role="tabpanel">
          <p className="panel-label">RECENT SESSIONS</p>
          {sessions.length === 0 && (
            <p className="empty-note">
              No sessions yet. Describe a site in the composer and the first analysis will be saved
              here with its full context memory.
            </p>
          )}
          {sessions.map((s) => (
            <div
              key={s.id}
              className={`session${s.id === activeId ? ' is-active' : ''}`}
              onClick={() => onSelect(s.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelect(s.id);
              }}
            >
              <MessageSquare size={16} className="session-icon" />
              <div style={{ minWidth: 0, flex: 1 }}>
                <div className="session-title">{s.title}</div>
                <div className="session-meta">{relativeTime(s.updated_at)}</div>
              </div>
              <button
                className="session-del"
                title="Delete session"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(s.id);
                }}
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === 'metrics' && <LiveMetrics metrics={metrics} kbStats={kbStats} />}
      {tab === 'about' && <About kbStats={kbStats} />}
    </aside>
  );
}

import { useState } from 'react';
import {
  ArrowDownRight,
  ArrowUpRight,
  BookOpen,
  Compass,
  Database,
  ExternalLink,
  Gauge,
  Layers,
  LineChart as LineChartIcon,
  Minus,
  Radar,
  ShieldAlert,
} from 'lucide-react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Logo, Scene, sceneForTags } from '../illustrations.jsx';

const PRETTY = {
  soil_organic_carbon: 'Soil organic carbon',
  soil_ph: 'Soil pH',
  soil_moisture: 'Soil moisture',
  soil_texture: 'Soil texture',
  salinity_ds_m: 'Salinity',
  land_use: 'Land use',
  crop: 'Crop',
  area_ha: 'Area',
  region: 'Region',
  biome: 'Climate zone',
  rainfall_mm: 'Rainfall',
  rainfall_pattern: 'Rainfall pattern',
  temperature_c: 'Temperature',
  irrigation: 'Water source',
  tree_cover_pct: 'Tree cover',
  natural_habitat_pct: 'Semi-natural habitat',
  species_of_concern: 'Species of concern',
  observed_changes: 'Observed changes',
  fertiliser_kg_n_ha: 'Nitrogen rate',
  pesticide_use: 'Pesticide use',
  pollution_sources: 'Pollution sources',
  latitude: 'Latitude',
  longitude: 'Longitude',
  goal: 'Objective',
  constraints: 'Constraints',
};

const UNITS = {
  soil_organic_carbon: '%',
  rainfall_mm: ' mm',
  area_ha: ' ha',
  tree_cover_pct: '%',
  natural_habitat_pct: '%',
  salinity_ds_m: ' dS/m',
  temperature_c: ' °C',
  fertiliser_kg_n_ha: ' kg N/ha',
};

function renderValue(key, value) {
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'string') return value.replace(/_/g, ' ');
  return `${value}${UNITS[key] || ''}`;
}

/** Turn the model's inline [DOC-ID] markers into styled citation chips. */
function Narrative({ text }) {
  const parts = String(text || '').split(/(\[[A-Z0-9][A-Z0-9-]{3,}\])/g);
  return (
    <p className="narrative">
      {parts.map((part, i) =>
        /^\[[A-Z0-9][A-Z0-9-]{3,}\]$/.test(part) ? (
          <cite key={i}>{part.slice(1, -1)}</cite>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </p>
  );
}

function MetricArrow({ direction }) {
  if (direction === 'increase') return <ArrowUpRight size={15} className="arrow-up" />;
  if (direction === 'decrease') return <ArrowDownRight size={15} className="arrow-down" />;
  return <Minus size={15} className="arrow-flat" />;
}

function RecommendationCard({ rec, citationsById }) {
  const [tab, setTab] = useState('action');
  const tabs = [
    ['action', 'What to do'],
    ['why', 'Why it works'],
    ['metrics', 'Metrics moved'],
    ['evidence', `Evidence (${rec.evidence_ids.length})`],
    ['cautions', 'Watch-outs'],
  ];

  return (
    <article className="rec">
      <div className="rec-top">
        <span className="rec-rank">{rec.rank}</span>
        <Scene name={sceneForTags(rec.tags)} className="rec-art" />
        <div style={{ flex: 1, minWidth: 0 }}>
          <h4 className="rec-title">{rec.title}</h4>
          <div className="rec-badges">
            <span className={`badge ${rec.time_horizon}`}>
              <Gauge size={12} /> {rec.time_horizon} term · {rec.horizon_detail}
            </span>
            <span className={`badge conf-${rec.confidence_label}`}>
              Confidence {Math.round(rec.confidence * 100)}% · {rec.confidence_label}
            </span>
            {rec.tags.slice(0, 2).map((t) => (
              <span className="badge" key={t}>
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="rec-tabs" role="tablist">
        {tabs.map(([key, label]) => (
          <button
            key={key}
            role="tab"
            className="rec-tab"
            aria-selected={tab === key}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="rec-body">
        {tab === 'action' && (
          <>
            <p>{rec.what_to_do}</p>
            {rec.first_actions?.length > 0 && (
              <>
                <p style={{ fontWeight: 600, color: 'var(--ink)', marginBottom: 6 }}>Start with</p>
                <ul>
                  {rec.first_actions.map((a) => (
                    <li key={a}>{a}</li>
                  ))}
                </ul>
              </>
            )}
          </>
        )}

        {tab === 'why' && (
          <>
            <p>{rec.why_it_works}</p>
            {rec.interactions?.length > 0 && (
              <>
                <p style={{ fontWeight: 600, color: 'var(--ink)', marginBottom: 6 }}>
                  How it interacts with the other measures
                </p>
                <ul>
                  {rec.interactions.map((i) => (
                    <li key={i}>{i}</li>
                  ))}
                </ul>
              </>
            )}
          </>
        )}

        {tab === 'metrics' && (
          <div>
            {rec.metrics.map((m) => (
              <div className="metric-row" key={m.metric + m.expected_change}>
                <div className="metric-name">
                  <MetricArrow direction={m.direction} />
                  {m.label}
                </div>
                <div className="metric-change">{m.expected_change}</div>
                <span className={`badge ${m.horizon}`}>{m.horizon} term</span>
              </div>
            ))}
            <p style={{ marginTop: 12, fontSize: 12.5, color: 'var(--muted)' }}>
              {rec.confidence_basis}
            </p>
          </div>
        )}

        {tab === 'evidence' &&
          rec.evidence_ids.map((id) => {
            const c = citationsById[id];
            if (!c) return null;
            return (
              <div className="evidence-item" key={id}>
                <span className="evidence-id">{id}</span>
                <div className="evidence-body">
                  <b>{c.title}</b>
                  <small>
                    {c.authors} · {c.source} · {c.year} · {c.tier.replace('_', ' ')}
                  </small>
                  <p>{c.snippet}</p>
                  <a href={c.url} target="_blank" rel="noreferrer" style={{ fontSize: 12.5 }}>
                    Open source <ExternalLink size={11} style={{ verticalAlign: '-1px' }} />
                  </a>
                </div>
              </div>
            );
          })}

        {tab === 'cautions' && (
          <ul>
            {(rec.watch_outs?.length ? rec.watch_outs : ['No specific cautions recorded for this measure.']).map(
              (w) => (
                <li key={w}>{w}</li>
              ),
            )}
          </ul>
        )}
      </div>
    </article>
  );
}

function Projection({ projection }) {
  if (!projection?.length) return null;
  const primary = projection[0];
  const chartData = ['baseline', 'year_1', 'year_3', 'year_5'].map((k, i) => {
    const row = { label: ['Now', 'Year 1', 'Year 3', 'Year 5'][i] };
    projection.slice(0, 3).forEach((p) => {
      row[p.label] = p[k];
    });
    return row;
  });
  const colors = ['#178a57', '#2d7fa8', '#c8892b'];

  return (
    <section className="section">
      <h3 className="section-head">
        <LineChartIcon size={16} /> Projected trajectory
      </h3>
      <div className="card">
        <div className="chart-wrap" style={{ height: 250 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 16, right: 22, bottom: 6, left: 0 }}>
              <CartesianGrid stroke="#e4ebe7" strokeDasharray="4 4" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#6d8279' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#6d8279' }} axisLine={false} tickLine={false} width={48} />
              <Tooltip
                contentStyle={{
                  borderRadius: 12,
                  border: '1px solid #e4ebe7',
                  fontSize: 12.5,
                  boxShadow: '0 8px 24px rgba(16,32,26,.08)',
                }}
              />
              {projection.slice(0, 3).map((p, i) => (
                <Line
                  key={p.metric}
                  type="monotone"
                  dataKey={p.label}
                  stroke={colors[i]}
                  strokeWidth={2.4}
                  dot={{ r: 3.5, strokeWidth: 0, fill: colors[i] }}
                  activeDot={{ r: 5 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="proj-grid">
          {projection.map((p) => (
            <div className="proj-tile" key={p.metric}>
              <b>{p.label}</b>
              <div className="proj-values">
                <span className="proj-now">{p.baseline}</span>
                <span style={{ color: 'var(--muted)' }}>→</span>
                <span className="proj-then">{p.year_3}</span>
                <span style={{ fontSize: 11.5, color: 'var(--muted)' }}>by year 3</span>
              </div>
              <small>
                {p.measured ? 'From your measured value. ' : 'From an assumed baseline. '}
                {p.basis}
              </small>
            </div>
          ))}
        </div>
      </div>
      <p className="hint" style={{ marginTop: 8 }}>
        Trajectories are literature-derived expectations for the selected bundle, not site predictions. The
        monitoring plan below is what converts them into measured fact.
      </p>
    </section>
  );
}

export default function Analysis({ data }) {
  const citationsById = Object.fromEntries((data.citations || []).map((c) => [c.id, c]));
  const contextEntries = Object.entries(data.context || {}).filter(
    ([, v]) => v !== null && v !== '' && !(Array.isArray(v) && v.length === 0),
  );

  return (
    <div className="msg-ai">
      <div className="ai-head">
        <span className="ai-avatar">
          <Logo size={18} />
        </span>
        <div>
          <div className="ai-name">Darukaa environmental scientist</div>
          <div className="ai-gen">
            {data.generator} · {data.latency_ms} ms
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="headline">{data.headline}</h3>
        <Narrative text={data.message} />

        {contextEntries.length > 0 && (
          <div className="context-strip">
            {contextEntries.map(([k, v]) => (
              <span className="var-chip" key={k}>
                <b>{renderValue(k, v)}</b>
                <span>{PRETTY[k] || k.replace(/_/g, ' ')}</span>
              </span>
            ))}
          </div>
        )}

        <div className="completeness">
          <span>Site profile {Math.round((data.context_completeness || 0) * 100)}% complete</span>
          <div className="meter">
            <i style={{ width: `${Math.round((data.context_completeness || 0) * 100)}%` }} />
          </div>
        </div>

        {data.assumptions?.length > 0 && (
          <div className="assumptions">
            <h5>Assumed, because it was not supplied — worth checking before spending</h5>
            <ul>
              {data.assumptions.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {data.recommendations?.length > 0 && (
        <section className="section">
          <h3 className="section-head">
            <Compass size={16} /> Sequenced recommendations
          </h3>
          {data.recommendations.map((rec) => (
            <RecommendationCard key={rec.rank} rec={rec} citationsById={citationsById} />
          ))}
        </section>
      )}

      {data.linkages?.length > 0 && (
        <section className="section">
          <h3 className="section-head">
            <Radar size={16} /> How the variables interact
          </h3>
          <div className="card linkages">
            {data.linkages.map((l) => (
              <div className="link-row" key={`${l.source}-${l.target}`}>
                <div className="link-pair">
                  <span>{PRETTY[l.source] || l.source.replace(/_/g, ' ')}</span>
                  <span className="link-rel">{l.relation}</span>
                  <span>{PRETTY[l.target] || l.target.replace(/_/g, ' ')}</span>
                </div>
                <div className="link-text">{l.explanation}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      <Projection projection={data.metric_projection} />

      {data.monitoring_plan?.length > 0 && (
        <section className="section">
          <h3 className="section-head">
            <ShieldAlert size={16} /> Monitoring loop
          </h3>
          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>Indicator</th>
                  <th>Method</th>
                  <th>Frequency</th>
                  <th>Target</th>
                </tr>
              </thead>
              <tbody>
                {data.monitoring_plan.map((m) => (
                  <tr key={m.indicator}>
                    <td>{m.indicator}</td>
                    <td>{m.method}</td>
                    <td>{m.frequency}</td>
                    <td>{m.target}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {data.citations?.length > 0 && (
        <section className="section">
          <h3 className="section-head">
            <BookOpen size={16} /> Sources used in this answer
          </h3>
          <div className="card" style={{ padding: '6px 18px 14px' }}>
            {data.citations.map((c) => (
              <div className="evidence-item" key={c.id}>
                <span className="evidence-id">{c.id}</span>
                <div className="evidence-body">
                  <b>{c.title}</b>
                  <small>
                    {c.authors} · {c.source} · {c.year}
                  </small>
                  <a href={c.url} target="_blank" rel="noreferrer" style={{ fontSize: 12.5 }}>
                    Open source <ExternalLink size={11} style={{ verticalAlign: '-1px' }} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {data.retrieval && (
        <section className="section">
          <details className="disclosure">
            <summary>
              <Database size={14} /> Retrieval trace — {data.retrieval.chunks.length} chunks from{' '}
              {data.retrieval.backend}, {data.retrieval.embedding_model}
            </summary>
            <div className="disclosure-body">
              <p className="hint" style={{ marginBottom: 10 }}>
                Query sent to the vector index:
              </p>
              <p className="mono" style={{ marginBottom: 14 }}>
                {data.retrieval.query}
              </p>
              {data.retrieval.chunks.map((c) => (
                <div className="retrieval-row" key={c.id}>
                  <div>
                    <b style={{ fontSize: 13 }}>{c.title}</b>
                    <div className="mono">
                      {c.id} · {c.source}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="score-bar">
                      <i style={{ width: `${Math.min(100, Math.round(c.score * 100))}%` }} />
                    </div>
                    <span className="mono">{c.score.toFixed(3)}</span>
                  </div>
                </div>
              ))}
            </div>
          </details>
        </section>
      )}

      {data.questions?.length > 0 && (
        <section className="section">
          <h3 className="section-head">
            <Layers size={16} /> One more variable would sharpen this
          </h3>
          {data.questions.map((q) => (
            <div className="question" key={q.slot}>
              <h4>{q.question}</h4>
              <p>{q.why_it_matters}</p>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

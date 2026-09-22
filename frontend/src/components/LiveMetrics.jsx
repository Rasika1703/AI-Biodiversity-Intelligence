const LABELS = {
  soil_organic_carbon: 'Soil organic carbon',
  soil_ph: 'Soil pH',
  soil_moisture: 'Soil moisture',
  soil_texture: 'Soil texture',
  salinity_ds_m: 'Salinity (dS/m)',
  land_use: 'Land use',
  crop: 'Crop',
  area_ha: 'Area (ha)',
  region: 'Region',
  biome: 'Climate zone',
  rainfall_mm: 'Rainfall (mm)',
  rainfall_pattern: 'Rainfall pattern',
  temperature_c: 'Temperature (°C)',
  irrigation: 'Water source',
  tree_cover_pct: 'Tree cover (%)',
  natural_habitat_pct: 'Semi-natural habitat (%)',
  species_of_concern: 'Species of concern',
  observed_changes: 'Observed changes',
  fertiliser_kg_n_ha: 'Fertiliser (kg N/ha)',
  pesticide_use: 'Pesticide use',
  pollution_sources: 'Pollution sources',
  latitude: 'Latitude',
  longitude: 'Longitude',
  goal: 'Goal',
  constraints: 'Constraints',
};

function Ring({ value = 0 }) {
  const pct = Math.max(0, Math.min(1, value));
  const r = 26;
  const c = 2 * Math.PI * r;
  return (
    <svg width="68" height="68" viewBox="0 0 68 68" aria-hidden="true">
      <circle cx="34" cy="34" r={r} fill="none" stroke="#e4ebe7" strokeWidth="8" />
      <circle
        cx="34"
        cy="34"
        r={r}
        fill="none"
        stroke="#2f9e68"
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={`${c * pct} ${c}`}
        transform="rotate(-90 34 34)"
      />
      <text
        x="34"
        y="38"
        textAnchor="middle"
        fontSize="15"
        fontWeight="700"
        fill="#0c3a27"
        fontFamily="Plus Jakarta Sans, sans-serif"
      >
        {Math.round(pct * 100)}
      </text>
    </svg>
  );
}

function fmt(v) {
  if (Array.isArray(v)) return v.join(', ');
  if (typeof v === 'number') return String(v);
  return String(v).replace(/_/g, ' ');
}

export default function LiveMetrics({ metrics, kbStats }) {
  const context = metrics?.context || {};
  const entries = Object.entries(context).filter(
    ([, v]) => v !== null && v !== '' && !(Array.isArray(v) && v.length === 0),
  );
  const docsUsed = metrics?.documents_used?.length || 0;
  const recs = metrics?.recommendations || [];
  const projection = metrics?.projection || [];

  return (
    <div className="panel" role="tabpanel">
      <h3>Session telemetry</h3>
      <div className="ring-wrap">
        <Ring value={metrics?.completeness || 0} />
        <div className="ring-text">
          <b>Site profile</b>
          <small>
            {entries.length} of {Object.keys(LABELS).length} variables captured
          </small>
          <small>{(metrics?.asked_slots || []).length} questions asked (never repeated)</small>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat">
          <b>{recs.length}</b>
          <small>Recommendations</small>
        </div>
        <div className="stat">
          <b>{docsUsed}</b>
          <small>Sources cited</small>
        </div>
        <div className="stat">
          <b>{kbStats?.document_count ?? '—'}</b>
          <small>Indexed studies</small>
        </div>
        <div className="stat">
          <b>{kbStats?.sources ?? '—'}</b>
          <small>Institutions</small>
        </div>
      </div>

      <h4>Captured variables</h4>
      {entries.length === 0 ? (
        <p className="empty-note">
          Nothing captured yet. Every fact you mention is extracted into a persistent site profile
          and reused across turns.
        </p>
      ) : (
        <div className="mini-list">
          {entries.map(([k, v]) => (
            <div className="mini-item" key={k}>
              <span>{LABELS[k] || k.replace(/_/g, ' ')}</span>
              <span>{fmt(v)}</span>
            </div>
          ))}
        </div>
      )}

      <h4>Prioritised actions</h4>
      {recs.length === 0 ? (
        <p className="empty-note">Run an analysis to populate the ranked intervention list.</p>
      ) : (
        <div className="mini-list">
          {recs.map((r) => (
            <div className="mini-item" key={r.rank}>
              <span>
                {r.rank}. {r.title}
              </span>
              <span>
                {r.time_horizon} · {Math.round((r.confidence || 0) * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}

      {projection.length > 0 && (
        <>
          <h4>Projected metric movement</h4>
          <div className="mini-list">
            {projection.map((p) => (
              <div className="mini-item" key={p.metric}>
                <span>{p.metric}</span>
                <span>
                  {p.baseline} → {p.year_3} <small>(yr 3)</small>
                </span>
              </div>
            ))}
          </div>
        </>
      )}

      <h4>Retrieval backend</h4>
      <div className="tag-cloud">
        <span className="tag">{kbStats?.vector_backend || 'vector store'}</span>
        <span className="tag">{kbStats?.embedding_model || 'embeddings'}</span>
        <span className="tag">{kbStats?.embedding_dim || 512}-dim vectors</span>
        <span className="tag">hybrid dense + BM25</span>
        <span className="tag">metadata boosting</span>
      </div>
    </div>
  );
}

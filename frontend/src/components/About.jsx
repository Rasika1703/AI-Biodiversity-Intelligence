import { Scene } from '../illustrations.jsx';

const PIPELINE = [
  {
    title: 'Slot extraction',
    body: 'Free text is parsed into 24 typed site variables — SOC %, pH, rainfall, salinity, tree cover, coordinates — and merged into a persistent profile.',
  },
  {
    title: 'Gap analysis + clarifying questions',
    body: 'Only the highest-value missing variables are asked about, at most two per turn. Every asked slot is written to a ledger so no question is ever repeated.',
  },
  {
    title: 'Hybrid retrieval',
    body: 'A query built from the site profile hits a vector store (ChromaDB with dense embeddings) blended with BM25-lite lexical scoring and metadata boosts for variable, biome and source tier.',
  },
  {
    title: 'Multi-metric reasoning',
    body: 'A deterministic engine evaluates ~30 diagnostic flags and scores 16 interventions against soil↔biodiversity, water↔species and land-use↔fragmentation couplings.',
  },
  {
    title: 'Evidence binding + confidence',
    body: 'Each recommendation is bound to retrieved studies, projected onto measurable metrics with a time horizon, and scored for confidence using evidence tier, site fit and how much was measured versus assumed.',
  },
  {
    title: 'Narration',
    body: 'An LLM writes only the connective prose, constrained to cite retrieved document IDs and forbidden from inventing figures. Without an API key a deterministic narrator takes over.',
  },
];

export default function About({ kbStats }) {
  return (
    <div className="panel" role="tabpanel">
      <div className="about-art">
        <Scene name="landscape" />
      </div>
      <h3>How this system thinks</h3>
      <p>
        Darukaa.Earth is a retrieval-grounded environmental reasoning engine, not a prompt wrapper.
        Knowledge lives in an indexed corpus of peer-reviewed studies and institutional reports;
        the language model only narrates what the engine has already decided and retrieved.
      </p>

      <div className="stat-grid">
        <div className="stat">
          <b>{kbStats?.document_count ?? '—'}</b>
          <small>Indexed documents</small>
        </div>
        <div className="stat">
          <b>{kbStats?.variables_covered ?? '—'}</b>
          <small>Variables covered</small>
        </div>
      </div>

      <h4>Retrieval-to-answer pipeline</h4>
      <div className="pipeline">
        {PIPELINE.map((step, i) => (
          <div className="pipe-step" key={step.title}>
            <span className="pipe-num">{i + 1}</span>
            <div>
              <b>{step.title}</b>
              <small>{step.body}</small>
            </div>
          </div>
        ))}
      </div>

      <h4>Evidence base</h4>
      <div className="tag-cloud">
        {['FAO', 'IPCC', 'IUCN', 'IPBES', 'CBD', 'UNCCD', 'Ramsar', 'UNEP', 'TEEB', 'ISRIC', 'ESA', 'GEO BON'].map(
          (t) => (
            <span className="tag" key={t}>
              {t}
            </span>
          ),
        )}
      </div>

      <h4>Variables reasoned over</h4>
      <div className="tag-cloud">
        {(kbStats?.top_variables || []).map(([name, count]) => (
          <span className="tag" key={name}>
            {name.replace(/_/g, ' ')} · {count}
          </span>
        ))}
      </div>

      <p style={{ marginTop: 14 }}>
        Every claim in an analysis carries a bracketed document ID that resolves to a real study or
        report, with the year and publishing institution shown in the sources list.
      </p>
    </div>
  );
}

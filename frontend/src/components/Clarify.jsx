import { HelpCircle } from 'lucide-react';
import { Logo } from '../illustrations.jsx';

const PRETTY = {
  soil_organic_carbon: 'Soil organic carbon',
  soil_ph: 'Soil pH',
  land_use: 'Land use',
  biome: 'Climate zone',
  rainfall_pattern: 'Rainfall',
  natural_habitat_pct: 'Semi-natural habitat',
  species_of_concern: 'Species of concern',
  pesticide_use: 'Pesticide use',
  area_ha: 'Area',
  crop: 'Crop',
  irrigation: 'Water source',
};

export default function Clarify({ data, onAnswer, onSkip, busy }) {
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
          <div className="ai-gen">{data.generator}</div>
        </div>
      </div>

      <div className="card">
        <h3 className="headline">{data.headline}</h3>
        <p className="narrative">{data.message}</p>

        {contextEntries.length > 0 && (
          <div className="context-strip">
            {contextEntries.map(([k, v]) => (
              <span className="var-chip" key={k}>
                <b>{Array.isArray(v) ? v.join(', ') : String(v).replace(/_/g, ' ')}</b>
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
      </div>

      <section className="section">
        <h3 className="section-head">
          <HelpCircle size={16} /> Asked once, never again
        </h3>
        {data.questions.map((q) => (
          <div className="question" key={q.slot}>
            <h4>{q.question}</h4>
            <p>{q.why_it_matters}</p>
            {q.options?.length > 0 && (
              <div className="option-row">
                {q.options.map((opt) => (
                  <button
                    key={opt}
                    className="option"
                    disabled={busy}
                    onClick={() => onAnswer(`${PRETTY[q.slot] || q.slot.replace(/_/g, ' ')}: ${opt}`)}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            )}
            {q.example && <p className="hint" style={{ marginTop: 8 }}>{q.example}</p>}
          </div>
        ))}
        <div className="skip-row">
          <button className="link-btn" onClick={onSkip} disabled={busy}>
            Skip these and analyse with stated assumptions
          </button>
        </div>
      </section>
    </div>
  );
}

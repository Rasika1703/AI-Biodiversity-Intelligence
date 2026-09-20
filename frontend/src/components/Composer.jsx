import { useEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';

const SAMPLE = {
  soil_organic_carbon: 0.3,
  soil_ph: 8.4,
  soil_moisture: 'low',
  soil_texture: 'sandy loam',
  land_use: 'monoculture cropland',
  crop: 'wheat',
  area_ha: 40,
  region: 'Rajasthan, India',
  biome: 'semi_arid',
  rainfall_mm: 420,
  rainfall_pattern: 'erratic',
  temperature_c: 32,
  irrigation: 'borehole',
  tree_cover_pct: 3,
  natural_habitat_pct: 2,
  species_of_concern: ['native bees', 'sandgrouse'],
  observed_changes: ['fewer pollinators', 'declining yields'],
  fertiliser_kg_n_ha: 120,
  pesticide_use: 'moderate',
  latitude: 26.91,
  longitude: 75.79,
  goal: 'restore biodiversity without losing income',
};

export default function Composer({ mode, onMode, onSend, busy }) {
  const [text, setText] = useState('');
  const [json, setJson] = useState(JSON.stringify(SAMPLE, null, 2));
  const [note, setNote] = useState('');
  const [error, setError] = useState('');
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 190)}px`;
  }, [text]);

  function sendText() {
    const value = text.trim();
    if (!value || busy) return;
    setText('');
    onSend({ message: value });
  }

  function sendJson() {
    if (busy) return;
    let parsed;
    try {
      parsed = JSON.parse(json);
    } catch (err) {
      setError(`Invalid JSON — ${err.message}`);
      return;
    }
    if (typeof parsed !== 'object' || Array.isArray(parsed) || parsed === null) {
      setError('Payload must be a JSON object of site variables.');
      return;
    }
    setError('');
    onSend({ message: note.trim(), structured: parsed, mode: 'structured' });
    setNote('');
  }

  return (
    <div className="composer">
      <div className="composer-inner">
        <div className="mode-row">
          <button className="mode" aria-pressed={mode === 'text'} onClick={() => onMode('text')}>
            Text
          </button>
          <button
            className="mode"
            aria-pressed={mode === 'structured'}
            onClick={() => onMode('structured')}
          >
            Structured JSON
          </button>
          {mode === 'structured' && (
            <span className="hint">Site variables are merged into session memory.</span>
          )}
        </div>

        {mode === 'text' ? (
          <div className="input-row">
            <textarea
              ref={ref}
              rows={1}
              value={text}
              placeholder="Describe your ecosystem, land conditions, or biodiversity concern…"
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendText();
                }
              }}
            />
            <button className="send" onClick={sendText} disabled={busy || !text.trim()} title="Send">
              <Send size={18} />
            </button>
          </div>
        ) : (
          <div>
            <textarea
              className="json-editor"
              value={json}
              spellCheck={false}
              onChange={(e) => {
                setJson(e.target.value);
                setError('');
              }}
            />
            {error && <div className="json-error">{error}</div>}
            <div className="input-row" style={{ marginTop: 10 }}>
              <textarea
                rows={1}
                value={note}
                placeholder="Optional note to send alongside the payload…"
                onChange={(e) => setNote(e.target.value)}
              />
            </div>
            <div className="json-actions">
              <button className="btn primary" onClick={sendJson} disabled={busy}>
                Analyse payload
              </button>
              <button
                className="btn"
                onClick={() => {
                  setJson(JSON.stringify(SAMPLE, null, 2));
                  setError('');
                }}
                disabled={busy}
              >
                Load sample site
              </button>
              <span className="hint">
                Any subset of fields is accepted — geo-coordinates included.
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

# Darukaa.Earth — AI Biodiversity Intelligence

An AI environmental scientist you can talk to. Describe a piece of land in plain English — or POST a JSON site profile — and get ranked, evidence-backed biodiversity interventions with the metrics they move, a time horizon, a confidence score, and a citation to a real study.

Built for the Darukaa.Earth AI hackathon challenge.

---

## Why this is not a prompt wrapper

The knowledge lives in a **retrievable, indexed corpus**, not in a system prompt. A deterministic reasoning engine decides *what to recommend*; the language model is only allowed to *narrate* what the engine has already decided and retrieved, and is forbidden from inventing figures. With no API key present, a deterministic narrator takes over and the system still works end to end.

| Requirement | How it is met |
|---|---|
| Retrievable knowledge layer | 48-document curated corpus indexed in ChromaDB with dense embeddings, blended with BM25-lite lexical scoring and metadata boosts |
| Conversational intelligence | Slot extraction into a persistent site profile, gap-driven clarifying questions, and a permanent **asked-slot ledger** so no question is ever repeated |
| Evidence-backed recommendations | Every card carries what to do / why it works / which metrics improve / which studies support it |
| Multi-metric reasoning | ~30 diagnostic flags and explicit couplings: soil↔biodiversity, water↔species, land use↔fragmentation |
| Text + structured input | Free text and a JSON `SiteContext` payload, geo-coordinates included |
| Required output fields | Recommendation, impacted metrics, time horizon (short/medium/long), confidence with a stated basis |

---

## Architecture

```
┌──────────────────────── React (Vite) ────────────────────────┐
│  Sidebar: History · Live Metrics · About                     │
│  Thread:  Hero → Clarify cards → Analysis cards              │
│  Composer: Text | Structured JSON                            │
└───────────────────────────── /api ───────────────────────────┘
                                │
┌──────────────────────── FastAPI ─────────────────────────────┐
│  1. extraction.py   free text → 24 typed site variables      │
│  2. session_store   SQLite: context, messages, asked-slots   │
│  3. clarify.py      gap analysis, ≤2 questions, never repeat │
│  4. vector_store    ChromaDB dense + BM25 + metadata boost   │
│  5. reasoning.py    30 flags → 16 interventions → confidence │
│  6. llm.py          narration only, must cite [DOC-ID]       │
└──────────────────────────────────────────────────────────────┘
```

**Request flow:** `POST /api/chat` → merge structured + extracted context into session memory → decide clarify vs analyse → hybrid retrieval → score interventions → bind evidence → project metrics → narrate → persist.

### Why retrieval is hybrid

Dense embeddings alone miss exact technical tokens (`dS/m`, `SOC`, species names); BM25 alone misses paraphrase. Scores are blended `0.62 · dense + 0.38 · lexical`, then boosted for variable overlap, biome match and source tier. `GET /api/knowledge/search` exposes all three components so the ranking is auditable.

### Why confidence is not a fixed number

Confidence blends evidence tier depth, engine fit, biome match, site-profile completeness, and **how many of the variables an intervention depends on were measured rather than assumed**. The same measure scores `high` on a well-characterised site and `indicative` where the key variables were guessed. A regression test asserts this relationship holds.

### How repetition is prevented

Every clarifying question writes its slot to `sessions.asked_slots_json` before the response is returned. `clarify.next_questions()` filters against that ledger, against already-known values, and against relevance predicates. Questioning stops entirely after turn 4 or once four core slots are known; anything asked but never answered is converted into an explicitly stated assumption shown in the analysis.

---

## Data model

**SQLite** (`backend/data/darukaa.db`)

| Table | Columns |
|---|---|
| `sessions` | `id`, `title`, `created_at`, `updated_at`, `context_json`, `asked_slots_json`, `meta_json` |
| `messages` | `id`, `session_id`, `turn`, `role`, `content`, `payload_json`, `created_at` |
| `retrieval_log` | `id`, `session_id`, `turn`, `query`, `doc_id`, `score`, `created_at` |

**Vector store** (`backend/data/chroma`) — one record per document: embedding plus metadata `{id, title, source, year, tier, variables, biomes, metrics}`.

**`SiteContext`** — 24 optional fields: `soil_organic_carbon`, `soil_ph`, `soil_moisture`, `soil_texture`, `salinity_ds_m`, `land_use`, `crop`, `area_ha`, `region`, `biome`, `rainfall_mm`, `rainfall_pattern`, `temperature_c`, `irrigation`, `tree_cover_pct`, `natural_habitat_pct`, `species_of_concern`, `observed_changes`, `fertiliser_kg_n_ha`, `pesticide_use`, `pollution_sources`, `latitude`, `longitude`, `goal`, `constraints`. Live schema at `GET /api/schema/site-context`.

---

## Local setup

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # add ANTHROPIC_API_KEY (optional)
uvicorn app.main:app --reload --port 8000
```

Docs at `http://localhost:8000/docs`. Optional higher-quality embeddings: `pip install -r requirements-embeddings.txt`.

**Frontend**

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, /api proxied to :8000
```

**Docker**

```bash
cp backend/.env.example backend/.env
docker compose up --build      # web :8080, api :8000
```

**Tests**

```bash
cd backend && pip install pytest && pytest -q
```

---

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Status, LLM availability, knowledge-base stats |
| POST | `/api/chat` | Main conversational endpoint |
| GET/POST | `/api/sessions` | List / create sessions |
| GET/DELETE | `/api/sessions/{id}` | Full transcript / delete |
| GET | `/api/knowledge/stats` | Corpus and retrieval configuration |
| GET | `/api/knowledge/search?q=&k=` | Auditable retrieval with score components |
| GET | `/api/knowledge/documents[/{id}]` | Browse the evidence corpus |
| GET | `/api/metrics/{session_id}` | Live telemetry for the session |
| GET | `/api/schema/site-context` | JSON schema for structured input |

**Example**

```bash
curl -X POST http://localhost:8000/api/chat -H 'Content-Type: application/json' -d '{
  "message": "Biodiversity is falling on my land.",
  "structured": {
    "soil_organic_carbon": 0.3, "soil_ph": 8.4, "land_use": "monoculture cropland",
    "biome": "semi_arid", "rainfall_mm": 420, "tree_cover_pct": 3,
    "latitude": 26.91, "longitude": 75.79
  }
}'
```

Returns `kind`, `headline`, `message`, `context`, `context_completeness`, `assumptions`, `questions`, `recommendations`, `linkages`, `citations`, `retrieval`, `metric_projection`, `monitoring_plan`, `generator`, `latency_ms`.

---

## CI/CD

`.github/workflows/ci.yml` runs on every push and PR to `main`:

1. **Backend** — install, `pytest -q`, then boot `uvicorn` and poll `/api/health` as a smoke test.
2. **Frontend** — `npm install`, `npm run build`, upload `dist/` as an artifact.
3. **Docker** — build both images, gated on the first two jobs passing.

**Deploy.** `render.yaml` provisions the API (with a 1 GB persistent disk mounted at `/var/data` for ChromaDB and SQLite) and the static frontend. The frontend also deploys to Vercel as-is via `frontend/vercel.json` — set `VITE_API_URL` to the API origin. Set `ANTHROPIC_API_KEY` as a secret; without it the deterministic narrator is used and the app still functions.

---

## Evidence base

48 documents spanning FAO, IPCC (SRCCL, AR6), IUCN, IPBES, CBD GBF, UNCCD, Ramsar, UNEP, TEEB, ISRIC SoilGrids, ESA WorldCover and GEO BON, alongside peer-reviewed work including Lal (2004), Poeplau & Don (2015), Tamburini (2020), Garibaldi (2013), Haddad (2015), Newbold (2015), Crouzeilles (2016), Isbell (2015) and Dainese (2019). Each record is typed with `variables`, `biomes`, `metrics` and a `tier` (`meta_analysis` / `peer_reviewed` / `institutional`) that feeds both retrieval boosting and confidence scoring.

## Project layout

```
backend/   app/{config,models,main}.py · knowledge/{corpus,vector_store}.py
           app/services/{extraction,session_store,clarify,reasoning,llm,advisor}.py
           app/routers/api.py · tests/test_system.py
frontend/  src/{App,main,api,illustrations,styles}
           src/components/{Sidebar,Hero,Composer,Analysis,Clarify,LiveMetrics,About}.jsx
.github/workflows/ci.yml · docker-compose.yml · render.yaml
```

## License

MIT.

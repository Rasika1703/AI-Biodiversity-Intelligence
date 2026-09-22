# Sample Requests

## 1. Text input, incomplete (triggers clarifying question)

```bash
curl -X POST https://ai-biodiversity-intelligencee.onrender.com/api/chat
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo-1", "message": "Biodiversity is declining on my land"}'
```

Expected: `needs_clarification: true`, with a clarifying question about SOC, rainfall, and land use.

## 2. Text input, complete (from the brief's worked example)

```bash
curl -X POST https://ai-biodiversity-intelligencee.onrender.com/api/chat
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo-2", "message": "Soil organic carbon is 0.3%, rainfall is low, monoculture wheat in a semi-arid region"}'
```

Expected: full recommendation set (agroforestry/intercropping, cover crops, etc.) each with mechanism, quantitative impact, time horizon, confidence, and source.

## 3. Structured JSON input (per brief's "Structured input" requirement)

```bashcurl -X POST https://ai-biodiversity-intelligencee.onrender.com/api/chat
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-3",
    "variables": {
      "soil_organic_carbon": 0.3,
      "rainfall": "low",
      "land_use": "monoculture wheat",
      "crop_type": "wheat",
      "region": "semi-arid"
    }
  }'
```

## 4. Structured input with geo-coordinates (bonus requirement)

```bash
curl -X POST https://ai-biodiversity-intelligencee.onrender.com/api/chat
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-4",
    "variables": {"soil_organic_carbon": 0.8, "rainfall": "moderate", "land_use": "pasture"},
    "latitude": 18.5204,
    "longitude": 73.8567
  }'
```

## 5. Inspect session memory (multi-turn debugging aid)

```bash
curl -X POST https://ai-biodiversity-intelligencee.onrender.com/api/chat
```

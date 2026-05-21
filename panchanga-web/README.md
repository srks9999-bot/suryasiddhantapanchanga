# Panchanga Compare Web

This is a standalone Next.js app for comparing **Panchanga + Navagraha planetary positions** across multiple date/time/location entries.

## Prerequisites

- Python Panchanga FastAPI running from `packages/panchanga/api/`
- Node 20+ and `pnpm`

## Configure

Create `apps/panchanga-web/.env.local`:

```bash
PANCHANGA_API_BASE_URL=http://localhost:8000
```

(`apps/panchanga-web/env.example` is provided as a template.)

## Run (dev)

### 1) Start the Python API

From the repo root:

```bash
cd /Users/vikas/rnd/sathkaal/pandit-allocation/packages/panchanga
python -m uvicorn api.main:app --reload --port 8000
```

Verify: `http://localhost:8000/docs`

### 2) Start the web app

```bash
cd /Users/vikas/rnd/sathkaal/pandit-allocation/apps/panchanga-web
pnpm dev
```

Open: `http://localhost:3000`

## API used

The UI calls a Next.js route handler:

- `POST /api/panchanga/calculate_many` (Next.js) → proxies to Python:
  - `POST /api/v1/panchanga/calculate_at/batch`

### Single-entry endpoint (Python)

- `POST /api/v1/panchanga/calculate_at`

### Batch endpoint (Python)

- `POST /api/v1/panchanga/calculate_at/batch`

Example payload:

```json
{
  "entries": [
    {
      "client_id": "entry-1",
      "date_time": "2026-01-16T09:30:00",
      "location": { "latitude": 23.2, "longitude": 75.8 }
    },
    {
      "client_id": "entry-2",
      "date_time": "2026-01-17T09:30:00",
      "location": { "latitude": 17.4, "longitude": 78.5 }
    }
  ]
}
```

## Notes

- The UI uses `datetime-local`, which is **timezone-less**; we treat the provided time as the **local civil time** for the chosen location.
- Planetary details are returned in `planets_detailed`. The UI computes Rasi from each planet’s `true_longitude`.


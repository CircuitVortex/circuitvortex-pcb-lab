# CircuitVortex PCB Lab

A real PCB processing platform: upload a KiCad board, inspect it, run KiCad DRC, run DFM checks, apply deterministic safe fixes, autoroute through FreeRouting, verify again, and download artifacts.

## Architecture

GitHub Pages hosts `web/`. A FastAPI service runs the processing worker. The processing image is based on `kicad/kicad:10.0.5`, uses an isolated Python virtual environment, includes a Java 25 runtime for FreeRouting, and verifies the KiCad/Java/Python toolchain during image build.

Pipeline:

`Upload → Inspect → DRC → DFM → Safe Fix → FreeRouting → Verify → Download`

The API never reports success for a subprocess that failed. Uploaded ZIPs are path-traversal checked and the original board remains in the job's input directory.

## Local run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Open `web/index.html` in a browser. Set `window.CIRCUITVORTEX_API` to the API URL when the API is not on localhost. The API has CORS middleware for a separately hosted Pages frontend; restrict `CORS_ORIGINS` in production.

## Docker / KiCad

```bash
docker compose build
docker compose up
```

Then the API is at `http://localhost:8000` and the health endpoint is `/health`.

## FreeRouting

Autorouting is fail-closed. The Docker image downloads the pinned FreeRouting 2.2.4 executable JAR and uses KiCad’s `pcbnew.ExportSpecctraDSN` / `ImportSpecctraSES` Python API for the DSN/SES round trip. A missing router, failed route, failed import, or failed verification is surfaced as a failed job rather than success.

For local non-Docker use, install FreeRouting and set `FREEROUTING_JAR` explicitly.

## API

- `GET /health`
- `POST /api/jobs` — multipart `file=.kicad_pcb|.zip`
- `GET /api/jobs/{id}`
- `POST /api/jobs/{id}/actions` with `{ "action": "drc|dfm|fix|autoroute|verify|pipeline" }`
- `GET /api/jobs/{id}/download/{artifact}`

## Security

Do not expose the processing service directly to the public internet without TLS, authentication/rate limiting, a sandbox, resource quotas, and isolated job storage. Uploaded PCB files are untrusted input. The worker never executes files from an upload as programs.

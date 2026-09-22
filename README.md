# CircuitVortex PCB Lab

A real PCB processing platform: upload a KiCad board, inspect it, run KiCad DRC, run DFM checks, apply deterministic safe fixes, autoroute through FreeRouting, verify again, and download artifacts.

## Architecture

GitHub Pages hosts `web/`. A FastAPI service runs the processing worker. The production Docker image is based on `kicad/kicad:10.0.5`, so authoritative KiCad DRC is executed in the same environment as the worker.

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

Open `web/index.html` in a browser. Set `window.CIRCUITVORTEX_API` to the API URL when the API is not on localhost.

## Docker / KiCad

```bash
docker compose build
docker compose up
```

Then the API is at `http://localhost:8000` and the health endpoint is `/health`.

## FreeRouting

Autorouting is deliberately fail-closed. Install a FreeRouting JAR and set `FREEROUTING_JAR`; the system will not claim autorouting succeeded if the router is missing or fails.

```bash
scripts/install_freerouting.sh /opt/freerouting
export FREEROUTING_JAR=/opt/freerouting/freerouting.jar
```

The DSN/SES adapter remains isolated in `scripts/autoroute.py` so it can be replaced by a native KiCad/Specctra adapter without changing the API.

## API

- `GET /health`
- `POST /api/jobs` — multipart `file=.kicad_pcb|.zip`
- `GET /api/jobs/{id}`
- `POST /api/jobs/{id}/actions` with `{ "action": "drc|dfm|fix|autoroute|verify|pipeline" }`
- `GET /api/jobs/{id}/download/{artifact}`

## Security

Do not expose the processing service directly to the public internet without TLS, authentication/rate limiting, a sandbox, resource quotas, and isolated job storage. Uploaded PCB files are untrusted input. The worker never executes files from an upload as programs.

## GitHub push-to-route automation

For GitHub-hosted processing, place a real `.kicad_pcb` in `pcb/input/` and push to `main`. The `PCB Auto Pipeline` workflow installs the KiCad and Java toolchain, downloads FreeRouting 2.2.4, performs inspection/DRC/DFM, autoroutes through the Specctra DSN/SES bridge, refills zones, runs final DRC/DFM, and publishes the resulting files as a workflow artifact. See `README-GITHUB-AUTOMATION.md`.

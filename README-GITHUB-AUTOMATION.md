# GitHub automation

Put a real KiCad board at `pcb/input/<name>.kicad_pcb` and push it to `main`.

GitHub Actions automatically installs:

- KiCad 10.0.5 from `kicad/kicad:10.0.5`
- Python dependencies from `requirements.txt`
- Java runtime
- FreeRouting 2.2.4 from the official FreeRouting GitHub release

Then it runs:

1. PCB inspection
2. KiCad DRC
3. DFM checks
4. Specctra DSN export through KiCad's `pcbnew` Python API
5. FreeRouting headless autoroute
6. Specctra SES import through KiCad's `pcbnew` Python API
7. Zone refill
8. Final KiCad DRC
9. Final DFM
10. Artifact packaging

Open the workflow run on GitHub and download `circuitvortex-pcb-results`.

## Manual run

Actions → PCB Auto Pipeline → Run workflow.

Set `board` to a path such as:

`pcb/input/myboard.kicad_pcb`

The workflow deliberately fails when a required tool or routing stage fails. It never labels a failed autoroute as successful.

### Important

GitHub Pages itself cannot execute KiCad. The GitHub Actions worker performs the actual PCB processing and stores the resulting artifacts.

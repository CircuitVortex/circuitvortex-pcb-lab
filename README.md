# CircuitVortex PCB Lab
Autonomous KiCad PCB inspection, DRC, DFM, safe editing, FreeRouting, reporting, and GitHub Pages dashboard.

Pipeline: Inspect → DRC → DFM → optional Autoroute → Refill → DRC → DFM → Summary.

This starter repository is intentionally deterministic: AI agents request explicit operations; Python validates and executes them; KiCad provides authoritative DRC; FreeRouting provides routing.

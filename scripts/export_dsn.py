#!/usr/bin/env python3
import argparse, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description='Export KiCad PCB to Specctra DSN using pcbnew Python API.')
    ap.add_argument('pcb'); ap.add_argument('dsn'); a=ap.parse_args()
    try:
        import pcbnew
    except Exception as e:
        raise SystemExit(f'KiCad pcbnew Python module unavailable: {e}')
    pcb=Path(a.pcb).resolve(); dsn=Path(a.dsn).resolve(); dsn.parent.mkdir(parents=True,exist_ok=True)
    board=pcbnew.LoadBoard(str(pcb))
    if board is None: raise SystemExit(f'Unable to load board: {pcb}')
    ok=pcbnew.ExportSpecctraDSN(board, str(dsn))
    if not ok or not dsn.exists() or dsn.stat().st_size == 0:
        raise SystemExit('KiCad Specctra DSN export failed')
    print(dsn)

if __name__ == '__main__': main()

#!/usr/bin/env python3
import argparse, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description='Import Specctra SES into a KiCad PCB using pcbnew Python API.')
    ap.add_argument('pcb'); ap.add_argument('ses'); ap.add_argument('output'); a=ap.parse_args()
    try:
        import pcbnew
    except Exception as e:
        raise SystemExit(f'KiCad pcbnew Python module unavailable: {e}')
    pcb=Path(a.pcb).resolve(); ses=Path(a.ses).resolve(); out=Path(a.output).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    board=pcbnew.LoadBoard(str(pcb))
    if board is None: raise SystemExit(f'Unable to load board: {pcb}')
    if not ses.exists(): raise SystemExit(f'SES file missing: {ses}')
    ok=pcbnew.ImportSpecctraSES(board, str(ses))
    if not ok: raise SystemExit('KiCad Specctra SES import failed')
    if not pcbnew.SaveBoard(str(out), board): raise SystemExit('KiCad board save failed after SES import')
    print(out)

if __name__ == '__main__': main()

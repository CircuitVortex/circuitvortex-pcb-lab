#!/usr/bin/env python3
import argparse, os, sys
from pathlib import Path

def load_pcbnew():
    candidates = [
        '/usr/lib/kicad/lib/python3/dist-packages',
        '/usr/lib/kicad/lib/python3/dist-packages/pcbnew',
        '/usr/lib/python3/dist-packages',
    ]
    for p in candidates:
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)
    try:
        import pcbnew
        return pcbnew
    except Exception as e:
        raise RuntimeError(f'Unable to import KiCad pcbnew Python API: {e}')

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd',required=True)
    ex=sub.add_parser('export')
    ex.add_argument('pcb'); ex.add_argument('dsn')
    im=sub.add_parser('import')
    im.add_argument('pcb'); im.add_argument('ses'); im.add_argument('output')
    a=ap.parse_args(); pcbnew=load_pcbnew()
    if a.cmd=='export':
        board=pcbnew.LoadBoard(a.pcb)
        if board is None: raise SystemExit('KiCad could not load board')
        Path(a.dsn).parent.mkdir(parents=True,exist_ok=True)
        ok=pcbnew.ExportSpecctraDSN(board,a.dsn)
        if not ok or not Path(a.dsn).exists(): raise SystemExit('Specctra DSN export failed')
        print(a.dsn)
    else:
        board=pcbnew.LoadBoard(a.pcb)
        if board is None: raise SystemExit('KiCad could not load board')
        ok=pcbnew.ImportSpecctraSES(board,a.ses)
        if not ok: raise SystemExit('Specctra SES import failed')
        Path(a.output).parent.mkdir(parents=True,exist_ok=True)
        if not pcbnew.SaveBoard(a.output,board): raise SystemExit('KiCad board save failed')
        print(a.output)
if __name__=='__main__': main()

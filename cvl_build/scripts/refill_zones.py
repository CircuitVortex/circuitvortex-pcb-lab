#!/usr/bin/env python3
import argparse, os, sys
from pathlib import Path

def load_pcbnew():
    for p in ['/usr/lib/kicad/lib/python3/dist-packages','/usr/lib/python3/dist-packages']:
        if os.path.isdir(p): sys.path.insert(0,p)
    import pcbnew
    return pcbnew

ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('output'); a=ap.parse_args()
pcbnew=load_pcbnew(); board=pcbnew.LoadBoard(a.input)
if board is None: raise SystemExit('KiCad could not load board')
try:
    board.Zones().clear if False else None
    filler=pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
except Exception as e:
    raise SystemExit(f'Zone refill failed: {e}')
Path(a.output).parent.mkdir(parents=True,exist_ok=True)
if not pcbnew.SaveBoard(a.output,board): raise SystemExit('Failed to save refilled board')
print(a.output)

#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
from common import result,save_json
def check(path,profile="generic"):
    text=Path(path).read_text(encoding="utf-8",errors="replace"); issues=[]
    if "Edge.Cuts" not in text: issues.append({"rule":"board_outline","severity":"error","message":"No Edge.Cuts reference detected"})
    for m in re.finditer(r'\(via\s+\(at\s+[^\)]+\).*?\(size\s+([0-9.]+)\).*?\(drill\s+([0-9.]+)',text,re.S):
        size,drill=map(float,m.groups()); ring=(size-drill)/2
        if ring<0.15: issues.append({"rule":"minimum_annular_ring","severity":"warning","annular_ring_mm":ring})
    return result("issues" if any(x["severity"]=="error" for x in issues) else "ok",input=str(path),profile=profile,issues=issues,issue_count=len(issues))
ap=argparse.ArgumentParser(); ap.add_argument("pcb"); ap.add_argument("--profile",default="generic"); ap.add_argument("-o","--output")
a=ap.parse_args(); r=check(a.pcb,a.profile)
if a.output: save_json(a.output,r)
print(json.dumps(r,indent=2))

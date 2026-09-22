#!/usr/bin/env python3
import argparse,shutil,re
from pathlib import Path
try:
    from scripts.common import save_json,utc_now
except ImportError:
    from common import save_json,utc_now
pat=re.compile(r'^\s*\((gr_text|gr_line|gr_rect|gr_circle|gr_arc|gr_poly|dimension)\b')
def items(text):
    lines=text.splitlines(True); out=[]; i=0
    while i<len(lines):
        if pat.match(lines[i]):
            s=i; depth=0
            while i<len(lines):
                depth+=lines[i].count("(")-lines[i].count(")"); i+=1
                if depth<=0: break
            out.append((s,i,"".join(lines[s:i])))
        else: i+=1
    return out
def remove(path,side):
    p=Path(path); original=p.read_text(encoding="utf-8",errors="replace"); backup=p.with_suffix(p.suffix+".bak"); shutil.copy2(p,backup)
    layers={"F.SilkS","B.SilkS"} if side=="both" else {("F.SilkS" if side=="front" else "B.SilkS")}
    doomed=set()
    for s,e,b in items(original):
        if any(f'(layer "{x}")' in b for x in layers): doomed.update(range(s,e))
    lines=original.splitlines(True); p.write_text("".join(x for i,x in enumerate(lines) if i not in doomed),encoding="utf-8")
    return {"status":"ok","timestamp":utc_now(),"backup":str(backup),"removed_items":len([1 for s,e,b in items(original) if any(f'(layer "{x}")' in b for x in layers)]),"layers":sorted(layers)}
ap=argparse.ArgumentParser(); ap.add_argument("pcb"); ap.add_argument("--front",action="store_const",const="front",dest="side"); ap.add_argument("--back",action="store_const",const="back",dest="side"); ap.add_argument("--both",action="store_const",const="both",dest="side"); ap.add_argument("-o","--report")
a=ap.parse_args(); r=remove(a.pcb,a.side or "both")
if a.report: save_json(a.report,r)
print(r)
